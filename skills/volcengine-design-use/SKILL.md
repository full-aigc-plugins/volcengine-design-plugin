---
name: volcengine-design-use
description: "Router for Volcengine (火山引擎) creation workflows: Doubao ASR transcription with millisecond word timestamps, TTS narration, Seedream image generation, and Seedance video generation (first/last-frame and reference modes). Use when the user wants transcription, narration, image or video generation through Volcengine, or names 豆包/火山引擎/Seedance/Seedream."
---

# Volcengine Design — Router

Deterministic clients live in `scripts/`. Every paid call runs only after the
step-0 preflight in this skill passes (credentials present, endpoint reachable).

| Need | Client | Skill |
|---|---|---|
| 口播转写 / 词级毫秒时间戳 | `scripts/volcengine_asr.py` | `volcengine-asr-transcribe` |
| 解说配音 | `scripts/volcengine_tts.py` | `volcengine-tts-narration` |
| 生图（Seedream） | `scripts/volcengine_ark.py image` | `volcengine-image-generation` |
| 生视频（Seedance，首尾帧/参考图） | `scripts/volcengine_ark.py video-*` | `volcengine-video-generation` |

## Credential families (two, independent)

1. **ARK_API_KEY** — 方舟 v3（chat/images/video）。console.volcengine.com/ark → API Key 管理。
2. **VOLCENGINE_APP_ID + VOLCENGINE_ACCESS_TOKEN** — 豆包语音（ASR/TTS）。console.volcengine.com/speech/app。

Env, project `.env`, or `~/.volcengine-design/config.json`. Missing values fail
fast with the exact remediation; never prompt mid-call.

## Cost discipline

- ASR/TTS 按时长计费（ASR ≈0.8 元/小时档）；Seedream/Seedance 按张/按秒计费。
- 提交前复述计费项；视频任务提交后先持久化 task_id 再报告（一次提交原则）。
