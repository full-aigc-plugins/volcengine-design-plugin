---
name: volcengine-video-generation
description: "Generate video with Doubao Seedance via Ark task API: t2v, i2v (first frame), FL2VA (first+last frame — white-model previs anchoring), and reference-image mode; submit-once with persisted task_id, resumable polling, verified download. Use for 生视频 on Volcengine."
---

# Seedance — Video Generation (task API)

Client: `scripts/volcengine_ark.py video-submit / video-status / video-wait / video-download`.
Model: `doubao-seedance-1-5-pro-251215` (default); 2.0/2.5 families differ in
first/last-frame vs reference support — never mix 首尾帧与参考图 in one request
(API rejects the combination).

## Modes

- **T2V**: prompt only (`--prompt`).
- **I2V**: `--first-frame <png>` — start from the frame, develop forward.
- **FL2VA**: `--first-frame <png> --last-frame <png>` — describe the continuous
  path BETWEEN the frames. **This is the white-model previs anchoring mode**:
  blender 白模逐镜首尾帧直接喂入。
- **Ref2V**: `--reference img…` — reference-image mode (mutually exclusive with
  首尾帧).

## Workflow

1. Preflight: `ARK_API_KEY` present; state the billing items (model/resolution/
   duration) before submitting.
2. `video-submit --prompt "…" --first-frame shot-01-first.png --last-frame shot-01-last.png
   --resolution 720p --duration 5` → persist `task_id` **before reporting**.
3. `video-wait --task-id <id> --interval 10 --timeout 900 --download shot-01.mp4`
   (interrupted polling resumes with `video-status` — never resubmit a live task).
4. On `failed`: report the API error verbatim; resubmission needs fresh user authorization.

## Previs anchoring notes

- 首帧在场时比例自适应（`adaptive`），不要再下发固定 ratio 与首帧冲突。
- 生成切点会漂移：成片拼接后必须 `detect_shots` 实测，不沿用镜头表。
