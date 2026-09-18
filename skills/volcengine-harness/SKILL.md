---
name: volcengine-harness
description: "Volcengine calling spec: the two independent credential families (ARK_API_KEY for Seedream/Seedance/chat; VOLCENGINE_APP_ID+ACCESS_TOKEN for Doubao ASR/TTS), the four deterministic clients, cost gates (discovery free, generation billed), and the submit-once discipline for video tasks. Read this before any Volcengine call."
---

# 火山引擎调用规范

四个确定性客户端（纯 stdlib，零 SDK 依赖）：`scripts/volcengine_ark.py`（chat /
image / video-*）、`volcengine_asr.py`（豆包大模型录音识别 2.0）、
`volcengine_tts.py`（TTS v3 unidirectional）、`volcengine_config.py`（凭据解析）。

## 1. 双凭据族（独立，不混用）

| 族 | 凭据 | 覆盖 |
|---|---|---|
| 方舟 v3 | `ARK_API_KEY` | chat / Seedream 生图 / Seedance 生视频 |
| 豆包语音 | `VOLCENGINE_APP_ID` + `VOLCENGINE_ACCESS_TOKEN` | ASR / TTS |

解析序：环境变量 → `.env` → `~/.volcengine-design/config.json`；缺失即 fail-fast
并给出补办指引（不要替用户填）。

## 2. 计费门禁

- **发现/查询免费，生成计费**：ASR ≈0.8 元/小时档；Seedream 按张；Seedance 按秒（分分辨率）。
- 视频 `video-submit` 前复述计费项（模型/分辨率/时长）；`task_id` 先持久化再报告。

## 3. 硬规则（来自工作集成与官方文档）

- Seedance `content[]`：`{type:text}` + `{type:image_url, role:first_frame|last_frame|reference_image}`；
  本地图转 data URI；**首尾帧与参考图互斥**（API 400 拒绝混用）。
- 轮询 `GET /contents/generations/tasks/{id}`，status ∈ queued/running/succeeded/failed/cancelled；
  失败/超时/Unknown 上报，**绝不自动二次提交**。
- 语音 Bearer 头是火山特有格式 `Bearer; {token}`（分号+空格），脚本已内置。
- TTS 音色名以官方音色列表为准，不编造；长文本分段调用。

## 4. 纪律

- 每步以客户端 JSON 输出为事实来源；凭据不进日志与产物清单。
- 白模首尾帧（blender 预演产物）直接喂 `--first-frame/--last-frame`（FL2VA 锚定模式）。
