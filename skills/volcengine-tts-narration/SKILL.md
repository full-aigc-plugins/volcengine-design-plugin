---
name: volcengine-tts-narration
description: "Generate narration audio with Doubao TTS v3: speaker selection, long-text chunking, deterministic download. Use when a video needs 解说配音/旁白 or any text-to-speech."
---

# Doubao TTS — Narration

Client: `scripts/volcengine_tts.py` (v3 unidirectional, resource 10029).

## Workflow

1. Preflight credentials (same family as ASR).
2. `python3 scripts/volcengine_tts.py --text "<解说词>" --speaker zh_female_cancan_mars_bigtts --format mp3 --output narration.mp3`
3. Long text: chunk by sentence (~300 chars per call) and concatenate, or let the
   caller split by `volcengine-asr-transcribe` utterance boundaries for 翻配.
4. Verify: file exists, bytes > 0; report speaker/format/sample_rate.

## Speaker discipline

- 音色名以官方音色列表为准，不编造；默认 `zh_female_cancan_mars_bigtts`。
- 男声推荐 `zh_male_chunhou_mars_bigtts`；具体音色让用户选或按文案风格指定。
