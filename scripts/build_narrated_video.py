"""Generate cue-aligned AI narration and mux it with the reviewed picture.

Install requirements-narration.txt first. Online synthesis sends cue text to
Microsoft's Edge speech service; cached MP3 files are reused on subsequent runs.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import subprocess
import wave

import edge_tts
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "outputs/narration"
SOURCE = ROOT / "deliverables/EE5110_5min_reviewed_preview.mp4"
OUTPUT = ROOT / "deliverables/EE5110_Final_Demo.mp4"
VOICE = "en-US-GuyNeural"
SAMPLE_RATE = 24000
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def run(*args):
    return subprocess.run([FFMPEG, "-hide_banner", "-v", "error", *map(str, args)],
                          check=True, capture_output=True)


def decode(path, filters=None):
    args = ["-i", path]
    if filters:
        args += ["-af", filters]
    return np.frombuffer(run(*args, "-f", "s16le", "-ac", 1, "-ar",
                             SAMPLE_RATE, "pipe:1").stdout, dtype="<i2").copy()


async def synthesize(cues):
    semaphore = asyncio.Semaphore(3)

    async def one(index, cue):
        # Cache identity includes exact text and voice, so edits regenerate audio.
        key = hashlib.sha256((VOICE + cue["text"]).encode()).hexdigest()[:12]
        path = WORK / f"{index:02d}_{key}.mp3"
        async with semaphore:
            if path.exists() and path.stat().st_size > 1000:
                return path
            for attempt in range(4):
                try:
                    await edge_tts.Communicate(cue["text"], VOICE).save(str(path))
                    decode(path)
                    print(f"Synthesized {index + 1}/{len(cues)}", flush=True)
                    return path
                except Exception:
                    path.unlink(missing_ok=True)
                    if attempt == 3:
                        raise
                    await asyncio.sleep(2 ** attempt)

    return await asyncio.gather(*(one(i, c) for i, c in enumerate(cues)))


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    storyboard = json.loads((ROOT / "docs/final_video/storyboard.json").read_text(encoding="utf-8"))
    cues = storyboard["cues"]
    narration = (ROOT / "docs/final_video/NARRATION_EN.md").read_text(encoding="utf-8")
    for cue in cues:
        if cue["text"] not in narration:
            raise ValueError("Storyboard cue differs from the narration manuscript")
    paths = asyncio.run(synthesize(cues))
    track = np.zeros(round(storyboard["duration_s"] * SAMPLE_RATE), dtype="<i2")
    records = []
    for index, (cue, path) in enumerate(zip(cues, paths)):
        raw = decode(path)
        # Trim encoder padding and synthesized leading/trailing silence only.
        active = np.flatnonzero(np.abs(raw.astype(np.int32)) > 180)
        if not len(active):
            raise ValueError(f"Silent cue {index}")
        first = max(0, active[0] - round(.04 * SAMPLE_RATE))
        last = min(len(raw), active[-1] + round(.10 * SAMPLE_RATE))
        raw = raw[first:last]
        target = cue["end"] - cue["start"] - .24
        duration = len(raw) / SAMPLE_RATE
        tempo = max(.85, duration / target)
        # atempo changes duration while preserving pitch.
        pcm_path = WORK / f"cue_{index:02d}.wav"
        with wave.open(str(pcm_path), "wb") as wav:
            wav.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
            wav.writeframes(raw.tobytes())
        aligned = decode(pcm_path, f"atempo={tempo:.8f},afade=t=in:d=0.012,areverse,afade=t=in:d=0.025,areverse")
        start = round((cue["start"] + .07) * SAMPLE_RATE)
        if start + len(aligned) > round(cue["end"] * SAMPLE_RATE):
            raise ValueError(f"Cue {index} overruns its picture interval")
        track[start:start + len(aligned)] = aligned
        records.append({"index": index + 1, **cue, "raw_s": duration,
                        "tempo": tempo, "speech_start_s": start / SAMPLE_RATE,
                        "speech_end_s": (start + len(aligned)) / SAMPLE_RATE})
    wav_path = WORK / "narration.wav"
    with wave.open(str(wav_path), "wb") as wav:
        wav.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
        wav.writeframes(track.tobytes())
    run("-y", "-i", SOURCE, "-i", wav_path, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "300",
        "-movflags", "+faststart", OUTPUT)
    # Decode every frame and audio packet; compare decoded video frame hashes.
    run("-i", OUTPUT, "-f", "null", "-")
    hashes = [run("-i", p, "-map", "0:v:0", "-f", "streamhash", "-hash", "sha256", "-").stdout.decode().strip()
              for p in (SOURCE, OUTPUT)]
    if hashes[0] != hashes[1]:
        raise ValueError("Muxed picture differs from reviewed source")
    final_audio = decode(OUTPUT)
    report = {"voice": VOICE, "provider": "Microsoft Edge online speech via edge-tts",
              "duration_s": len(final_audio) / SAMPLE_RATE,
              "cue_count": len(cues), "all_cues_within_intervals": True,
              "full_decode_passed": True, "video_frame_hash_equal": True,
              "video_stream_hash": hashes[0], "output_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              "peak_dbfs": float(20 * np.log10(max(1, np.abs(final_audio.astype(np.int32)).max()) / 32768)),
              "cues": records}
    (WORK / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "cues"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
