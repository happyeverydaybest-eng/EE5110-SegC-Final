"""Retime reviewed picture/subtitles around uncompressed, slower AI speech."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import shutil
import textwrap
import wave

import edge_tts
import numpy as np

from build_narrated_video import ROOT, SOURCE, OUTPUT, VOICE, SAMPLE_RATE, run, decode
from build_final_video_materials import timestamp

WORK = ROOT / "outputs/narration_paced"
DOCS = ROOT / "docs/final_video"
RATE = "-8%"
FPS = 25


async def synthesize(cues):
    gate = asyncio.Semaphore(3)

    async def one(index, cue):
        key = hashlib.sha256((VOICE + RATE + cue['text']).encode()).hexdigest()[:12]
        path = WORK / f"speech_{index:02d}_{key}.mp3"
        async with gate:
            for attempt in range(4):
                try:
                    if not path.exists():
                        await edge_tts.Communicate(cue['text'], VOICE, rate=RATE).save(str(path))
                    raw = decode(path)
                    active = np.flatnonzero(np.abs(raw.astype(np.int32)) > 180)
                    if not len(active):
                        raise ValueError('Silent speech')
                    raw = raw[max(0, active[0] - 960):min(len(raw), active[-1] + 2400)]
                    print(f"Natural speech {index+1}/{len(cues)}", flush=True)
                    return raw
                except Exception:
                    path.unlink(missing_ok=True)
                    if attempt == 3:
                        raise
                    await asyncio.sleep(2 ** attempt)

    return await asyncio.gather(*(one(i, c) for i, c in enumerate(cues)))


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    data = json.loads((DOCS / 'storyboard.json').read_text(encoding='utf-8'))
    cues = data['cues']
    manuscript = (DOCS / 'NARRATION_EN.md').read_text(encoding='utf-8')
    if any(cue['text'] not in manuscript for cue in cues):
        raise ValueError('Cue text differs from the narration manuscript')
    speech = asyncio.run(synthesize(cues))
    # Reserve breathing room and readability; redistribute remaining time.
    frames = np.array([math.ceil(max(len(pcm)/SAMPLE_RATE + .55,
                                    (c['end']-c['start'])*.7, 3.5)*FPS)
                       for pcm, c in zip(speech, cues)], dtype=int)
    if frames.sum() > 300*FPS:
        raise ValueError(f'Natural reading needs {frames.sum()/FPS:.2f}s; revise the edit rather than accelerate audio')
    spare = 300*FPS - int(frames.sum())
    weights = np.array([c['end']-c['start'] for c in cues])
    shares = spare * weights / weights.sum()
    extra = np.floor(shares).astype(int)
    for index in np.argsort(-(shares-extra))[:spare-int(extra.sum())]:
        extra[index] += 1
    frames += extra
    starts = np.concatenate(([0], np.cumsum(frames)))
    signature = hashlib.sha256(SOURCE.read_bytes() + frames.tobytes()).hexdigest()
    cache_manifest = WORK / 'picture_signature.txt'
    cached = cache_manifest.exists() and cache_manifest.read_text() == signature
    records = []
    track = np.zeros(300*SAMPLE_RATE, dtype='<i2')
    subtitles = []
    for i, (cue, pcm) in enumerate(zip(cues, speech)):
        begin, end = starts[i]/FPS, starts[i+1]/FPS
        offset = round((begin+.12)*SAMPLE_RATE)
        track[offset:offset+len(pcm)] = pcm
        speech_end = (offset+len(pcm))/SAMPLE_RATE
        if speech_end > end-.3:
            raise ValueError('Missing breathing room')
        records.append({'index': i+1, 'source_start': cue['start'], 'source_end': cue['end'],
                        'start': begin, 'end': end, 'text': cue['text'],
                        'speech_start': offset/SAMPLE_RATE, 'speech_end': speech_end,
                        'trailing_pause_s': end-speech_end, 'audio_tempo': 1.0})
        subtitles += [str(i+1), f'{timestamp(begin, True)} --> {timestamp(end, True)}',
                      '\n'.join(textwrap.wrap(cue['text'], width=72)), '']
    (DOCS / 'narration_paced.srt').write_text('\n'.join(subtitles), encoding='utf-8')

    def render(i):
        cue = cues[i]
        first, last = math.ceil(cue['start']*FPS), math.ceil(cue['end']*FPS)
        factor = int(frames[i])/(last-first)
        path = WORK / f'picture_{i:02d}.mp4'
        if cached and path.exists():
            return path
        # Captions and all action labels travel with their original picture.
        filters = (f'trim=start_frame={first}:end_frame={last},'
                   f'setpts=(PTS-STARTPTS)*{factor:.12f},'
                   'tpad=stop_mode=clone:stop_duration=1,fps=25')
        run('-y', '-i', SOURCE, '-vf', filters, '-frames:v', int(frames[i]),
            '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
            '-threads', '2', '-pix_fmt', 'yuv420p', path)
        print(f'Retimed picture {i+1}/{len(cues)}', flush=True)
        return path

    with ThreadPoolExecutor(max_workers=3) as pool:
        pictures = list(pool.map(render, range(len(cues))))
    cache_manifest.write_text(signature)
    listing = WORK / 'concat.txt'
    listing.write_text('\n'.join("file '" + p.as_posix() + "'" for p in pictures), encoding='utf-8')
    audio = WORK / 'natural_narration.wav'
    with wave.open(str(audio), 'wb') as wav:
        wav.setparams((1, 2, SAMPLE_RATE, 0, 'NONE', 'not compressed'))
        wav.writeframes(track.tobytes())
    final = WORK / 'final.mp4'
    run('-y', '-f', 'concat', '-safe', '0', '-i', listing, '-i', audio,
        '-map', '0:v:0', '-map', '1:a:0', '-vf',
        "drawbox=x=936:y=557:w=310:h=46:color=0x183345:t=fill,"
        "drawtext=text='Narration-paced playback':fontfile='C\\:/Windows/Fonts/arial.ttf':"
        'fontcolor=0x62d4d0:fontsize=17:x=940:y=565',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '4', '-af',
        'loudnorm=I=-16:TP=-1.5:LRA=7', '-c:a', 'aac', '-b:a', '192k',
        '-ar', '48000', '-metadata:s:a:0', 'language=eng', '-t', '300',
        '-movflags', '+faststart', final)
    run('-i', final, '-f', 'null', '-')
    samples = decode(final)
    # Count every decoded picture frame, independently of container metadata.
    probe = run('-i', final, '-map', '0:v:0', '-f', 'framemd5', '-')
    count = sum(1 for row in probe.stdout.decode().splitlines() if row and not row.startswith('#'))
    if count != 7500:
        raise ValueError(f'Unexpected decoded frame count: {count}')
    report = {'revision': 'natural-paced-2026-11-09', 'voice': VOICE, 'synthesis_rate': RATE,
              'duration_s': 300, 'decoded_frames': count, 'audio_tempo': 1.0,
              'full_decode_passed': True, 'cue_count': len(cues),
              'minimum_caption_s': float(min(frames)/FPS),
              'minimum_trailing_pause_s': min(c['trailing_pause_s'] for c in records),
              'output_sha256': hashlib.sha256(final.read_bytes()).hexdigest(),
              'peak_dbfs': float(20*np.log10(np.abs(samples.astype(np.int32)).max()/32768)),
              'cues': records}
    (DOCS/'AI_NARRATION_CHECK.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    lines = ['# Natural-paced English narration', '', '300 seconds; AI speech at -8%, no audio time compression.', '']
    for record in records:
        lines += [f"## {timestamp(record['start'])}–{timestamp(record['end'])}", '', record['text'], '']
    (DOCS/'NARRATION_PACED_EN.md').write_text('\n'.join(lines), encoding='utf-8')
    shutil.copyfile(final, OUTPUT)
    print(json.dumps({k:v for k,v in report.items() if k != 'cues'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
