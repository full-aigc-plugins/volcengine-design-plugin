---
name: volcengine-audio-spec
description: "Spec knowledge for 豆包语音 credential families, audio formats, limits, and speaker resources. Use when debugging auth failures, choosing audio formats, or picking speakers."
---

# 豆包语音 — Spec & Debug

## Credentials (speech family)

- `VOLCENGINE_APP_ID` — 语音技术应用 AppID（console.volcengine.com/speech/app）
- `VOLCENGINE_ACCESS_TOKEN` — 同页 Access Token
- ASR resource: `volc.bigasr.auc.duration`（大模型录音识别 2.0，时长档）
- TTS resource: `volc.service_type.10029`（大模型语音合成）
- Bearer 头格式是火山特有的 `Bearer; {token}`（分号+空格），脚本已内置。

## Audio formats

- ASR 输入：wav/mp3/m4a…（时长档模型适配长音频；本地文件 base64 上传或公网 URL）
- TTS 输出：mp3/wav/pcm/ogg_opus，sample_rate 默认 24000

## Debug

- 401/鉴权错误：先跑 `volcengine-check`——两大凭据族独立，别混用（ARK key 不能访问 openspeech）。
- 空音频：检查音色名是否来自官方音色列表；文本是否为空/超长（长文本分段）。
