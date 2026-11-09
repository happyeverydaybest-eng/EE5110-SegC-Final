# AI英文配音与节奏优化

2026-11-09 更新 `deliverables/EE5110_Final_Demo.mp4`。

- 视频：300秒，1280×720，25 fps，H.264。原审片画面与烧录字幕按逐句区间同步重定时，镜头顺序与动作标注保留。
- 配音：Microsoft Edge 在线语音，`en-US-GuyNeural`，美式英语男声，通过 `edge-tts==7.3.1` 生成。
- 内容：直接采用 `NARRATION_EN.md` 对应的 storyboard 54条cue，635词，未改写讲稿。
- 同步：合成语速 `-8%`，全部使用自然合成音频，不进行音频时长压缩。按实际语音长度分配镜头与字幕时间，句尾停顿至少0.47秒。
- 音频：AAC、48 kHz、单声道，响度标准化目标 -16 LUFS。
- 验证：全片7500帧及音频完整解码，54条时间边界和停顿检查；抽查第21、33、50、54句的字幕、图表/动作与版面。技术结果见下方JSON。

原4秒的软体应变说明调整为6.24秒；原3秒的实验分母说明调整为5.20秒；末句从4秒调整为5.88秒。字幕最短3.56秒，最高字幕词速约163词/分钟，总时长保持300秒。右侧播放速度标记更新为 `Narration-paced playback`。

新版[逐句时间稿](NARRATION_PACED_EN.md)与[字幕](narration_paced.srt)对应最终成片；原 `NARRATION_EN.md`、`narration.srt`、`storyboard.json`、镜头表与全片审片记录对应原无声审片版。新版画面时间戳随口播改变。

## 重建

在项目根目录执行：

```powershell
.venv\Scripts\python -m pip install -r requirements-narration.txt
.venv\Scripts\python scripts/build_narrated_video.py
```

默认入口调用 `scripts/optimize_video_pacing.py`。首次生成需联网，将逐句英文文本发送给在线语音服务。缓存位于 `outputs/narration_paced/`，文本和声音不变时重用缓存。脚本从 `storyboard.json` 读取时间轴，并核对每句确实存在于口播稿中。若自然语音与最小停顿合计超过300秒，脚本会停止，要求调整剪辑。

检查结果为 [AI_NARRATION_CHECK.json](AI_NARRATION_CHECK.json)。临时MP3、WAV及工具保留于忽略目录，不提交到Git。旧版固定字幕时间并压缩音频的流程可通过 `--legacy-timing` 复现，会覆盖最终成片；旧成片也可从Git历史恢复。
