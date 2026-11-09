# AI英文配音交付记录

2026-11-09 完成 `deliverables/EE5110_Final_Demo.mp4`。

- 视频：300秒，1280×720，25 fps，H.264；与原审片版逐帧SHA-256一致，原烧录字幕保留。
- 配音：Microsoft Edge 在线语音，`en-US-GuyNeural`，美式英语男声，通过 `edge-tts==7.3.1` 生成。
- 内容：直接采用 `NARRATION_EN.md` 对应的 storyboard 54条cue，635词，未改写讲稿。
- 同步：逐句裁去边缘静音，保留短停顿，以保持音高的 atempo 调整语速，所有语句均落在对应cue区间内。
- 音频：AAC、48 kHz、单声道，实测综合响度 -16.3 LUFS，真峰值 -1.4 dBFS。
- 验证：全片7500帧及音频完整解码通过；54条时间边界检查通过；解码画面流哈希相同。
- 验证范围：以上为程序化时间轴、解码、画面一致性和响度检查，未进行人工全片听审。

部分短cue需要较快语速，最大调整为1.537倍；最后一句在300秒前结束。AAC解码后的尾部填充约11毫秒，视频容器时长为300秒。

## 重建

在项目根目录执行：

```powershell
.venv\Scripts\python -m pip install -r requirements-narration.txt
.venv\Scripts\python scripts/build_narrated_video.py
```

首次生成需联网，将逐句英文文本发送给在线语音服务。缓存位于 `outputs/narration/`，文本和声音不变时重用缓存。脚本从 `storyboard.json` 读取时间轴，并核对每句确实存在于口播稿中。

本地完整检查结果为 `outputs/narration/verification.json`，版本化副本为 [AI_NARRATION_CHECK.json](AI_NARRATION_CHECK.json)。临时MP3、WAV及工具保留于忽略目录，不提交到Git。
