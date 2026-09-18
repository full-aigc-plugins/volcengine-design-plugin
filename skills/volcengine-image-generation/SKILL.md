---
name: volcengine-image-generation
description: "Generate images with Doubao Seedream via Ark /images/generations: text2image, reference-guided editing, sequential 组图. Use for 生图 tasks on Volcengine."
---

# Seedream — Image Generation

Client: `scripts/volcengine_ark.py image` (OpenAI images shape, model
`doubao-seedream-4-0-250828`).

## Workflow

1. Preflight: `ARK_API_KEY` present.
2. `python3 scripts/volcengine_ark.py image --prompt "…" --size 2048x2048 --download out/`
3. Reference-guided editing/组图: `--reference img1.png [img2.png] --seq`.
4. Report saved paths + model + size.

## Notes

- `--seq` enables sequential 组图 (auto); text-key consistency across the set.
- b64 与 url 两种响应都落盘处理；不落盘时输出完整 JSON。
