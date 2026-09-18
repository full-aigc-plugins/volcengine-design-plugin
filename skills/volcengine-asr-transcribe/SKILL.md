---
name: volcengine-asr-transcribe
description: "Transcribe speech audio with Doubao bigmodel ASR: submit → wait → millisecond word-level timeline. This is the slicing base for 口播/short-form video editing — word timestamps drive cut points. Use for 口播、访谈、任何需要按语音切片的任务。"
---

# Doubao ASR — Transcription with Word Timestamps

Client: `scripts/volcengine_asr.py` (bigmodel 2.0, `volc.bigasr.auc.duration`).

## Workflow

1. Preflight: `VOLCENGINE_APP_ID` + `VOLCENGINE_ACCESS_TOKEN` present (env/.env/config).
2. Submit: `python3 scripts/volcengine_asr.py submit --file <audio> --format wav`
   (or `--url <public audio url>`). Persist the returned `request_id` + `task_id`
   **before reporting** — they are the recovery keys.
3. Wait: `wait --task-id <id> --interval 10 --timeout 1800`.
4. Timeline: `words --task-id <id>` prints one JSON per word
   (`start` / `end` / `word` / `utterance_end`, milliseconds).
5. Full record: `query --task-id <id> --json` (utterances + text).

## 口播切片语义

- 词级时间戳是切片点的事实来源；句末标点的 `utterance_end` 是自然切点。
- 静音段（相邻词 start 差 > 400ms）是强切点候选。
- 切片决策交给上游（video-factory / yichen 式剪辑脑）；本技能只产出时间轴事实。
