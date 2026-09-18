#!/usr/bin/env python3
"""Volcengine Ark (方舟 v3) deterministic client: chat / images / video tasks.

Facts baked in (verified against working integrations and official docs):
- Base: https://ark.cn-beijing.volces.com/api/v3, Authorization: Bearer <API key>.
- Video: POST /contents/generations/tasks with model doubao-seedance-1-5-pro
  (default), content[] = [{type:text,text}, {type:image_url,image_url:{url},
  role:first_frame|last_frame|reference_image}]; local images are sent as
  data URIs. Poll GET /contents/generations/tasks/{id} — status ∈
  queued/running/succeeded/failed/cancelled; result video at content.video_url.
- Image: POST /images/generations (OpenAI shape), model doubao-seedream-4-0-250828,
  response data[].url or b64_json.
- First/last frame and reference images are mutually exclusive per request.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from volcengine_config import ark_api_key, ark_base_url, ark_headers  # noqa: E402

DEFAULT_VIDEO_MODEL = "doubao-seedance-1-5-pro-251215"
DEFAULT_IMAGE_MODEL = "doubao-seedream-4-0-250828"
DEFAULT_CHAT_MODEL = "doubao-seed-1-6-250615"
TERMINAL = {"succeeded", "failed", "cancelled"}


def encode_image(path: str) -> str:
    if path.startswith(("http://", "https://", "data:")):
        return path
    mime = mimetypes.guess_type(path)[0] or "image/png"
    raw = Path(path).read_bytes()
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def call(method: str, path: str, payload: dict | None = None) -> dict:
    request = urllib.request.Request(
        ark_base_url() + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=ark_headers(ark_api_key()),
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:400]
        sys.exit(f"HTTP {exc.code} from {path}: {detail}")
    return json.loads(body) if body else {}


def image_to_data_uri(path: str) -> str:
    return encode_image(path)


def cmd_chat(args: argparse.Namespace) -> int:
    payload = {"model": args.model, "messages": [{"role": "user", "content": args.prompt}]}
    result = call("POST", "/chat/completions", payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_image(args: argparse.Namespace) -> int:
    payload: dict = {"model": args.model, "prompt": args.prompt}
    if args.size:
        payload["size"] = args.size
    if args.reference:
        payload["image"] = [encode_image(p) for p in args.reference]
    if args.seq:
        payload["sequential_image_generation"] = "auto"
    result = call("POST", "/images/generations", payload)
    out_dir = Path(args.download) if args.download else None
    items = result.get("data", [])
    for i, item in enumerate(items):
        if item.get("b64_json") and out_dir:
            target = out_dir / f"image-{i}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(base64.b64decode(item["b64_json"]))
            print(f"saved: {target}")
    if out_dir:
        for i, item in enumerate(items):
            if item.get("url"):
                target = out_dir / f"image-{i}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(item["url"], target)
                print(f"saved: {target}")
    if not out_dir:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_video_content(args: argparse.Namespace) -> list[dict]:
    if args.first_frame and (args.last_frame or args.reference):
        sys.exit("首尾帧与参考图互斥（Ark 拒绝混用：first/last frame content cannot be mixed with reference media）")
    content: list[dict] = [{"type": "text", "text": args.prompt}]
    for role, flag in (("first_frame", args.first_frame), ("last_frame", args.last_frame)):
        if flag:
            content.append({"type": "image_url", "image_url": {"url": encode_image(flag)}, "role": role})
    for ref in args.reference or []:
        content.append({"type": "image_url", "image_url": {"url": encode_image(ref)}, "role": "reference_image"})
    return content


def cmd_video_submit(args: argparse.Namespace) -> int:
    payload = {
        "model": args.model,
        "content": build_video_content(args),
    }
    if args.resolution:
        payload["resolution"] = args.resolution
    if args.duration:
        payload["duration"] = args.duration
    if args.ratio and not args.first_frame:
        payload["ratio"] = args.ratio
    result = call("POST", "/contents/generations/tasks", payload)
    task_id = result.get("id", "")
    print(json.dumps({"task_id": task_id, "status": result.get("status")}, ensure_ascii=False))
    return 0


def cmd_video_status(args: argparse.Namespace) -> int:
    result = call("GET", f"/contents/generations/tasks/{args.task_id}")
    status = result.get("status")
    video_url = (result.get("content") or {}).get("video_url", "")
    summary = {"task_id": args.task_id, "status": status, "done": status in TERMINAL}
    if video_url:
        summary["video_url"] = video_url
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(summary, ensure_ascii=False))
    return 0 if status in TERMINAL else 1


def cmd_video_download(args: argparse.Namespace) -> int:
    result = call("GET", f"/contents/generations/tasks/{args.task_id}")
    video_url = (result.get("content") or {}).get("video_url", "")
    if not video_url:
        sys.exit(f"任务 {args.task_id} 尚无 video_url（status={result.get('status')}）")
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(video_url, target)
    print(json.dumps({"saved": str(target), "bytes": target.stat().st_size}, ensure_ascii=False))
    return 0


def cmd_video_wait(args: argparse.Namespace) -> int:
    deadline = time.time() + args.timeout
    while True:
        result = call("GET", f"/contents/generations/tasks/{args.task_id}")
        status = result.get("status")
        print(json.dumps({"task_id": args.task_id, "status": status}, ensure_ascii=False), flush=True)
        if status in TERMINAL:
            video_url = (result.get("content") or {}).get("video_url", "")
            if args.download and video_url:
                target = Path(args.download)
                target.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(video_url, target)
                print(json.dumps({"saved": str(target), "bytes": target.stat().st_size}, ensure_ascii=False))
            return 0 if status == "succeeded" else 1
        if time.time() > deadline:
            sys.exit(f"轮询超时（{args.timeout}s），task_id 已持久化，可稍后 video-status 恢复")
        time.sleep(args.interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Volcengine Ark deterministic client (chat/images/video)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("chat", help="doubao LLM chat completion")
    p.add_argument("--prompt", required=True)
    p.add_argument("--model", default=DEFAULT_CHAT_MODEL)
    p.set_defaults(fn=cmd_chat)

    p = sub.add_parser("image", help="Seedream image generation")
    p.add_argument("--prompt", required=True)
    p.add_argument("--model", default=DEFAULT_IMAGE_MODEL)
    p.add_argument("--size", default="2048x2048")
    p.add_argument("--reference", nargs="*", help="参考图（组图/编辑）")
    p.add_argument("--seq", action="store_true", help="组图模式 sequential_image_generation=auto")
    p.add_argument("--download", help="落盘目录（url/b64 均保存）")
    p.set_defaults(fn=cmd_image)

    p = sub.add_parser("video-submit", help="Seedance video task submit")
    p.add_argument("--prompt", required=True)
    p.add_argument("--model", default=DEFAULT_VIDEO_MODEL)
    p.add_argument("--first-frame", help="白模首帧图（本地路径或 URL）")
    p.add_argument("--last-frame", help="白模尾帧图（FL2VA 模式）")
    p.add_argument("--reference", nargs="*", help="参考图（与首尾帧互斥）")
    p.add_argument("--resolution", choices=["480p", "720p", "1080p"])
    p.add_argument("--duration", type=int, help="秒")
    p.add_argument("--ratio", choices=["16:9", "9:16", "4:3", "3:4", "1:1", "21:9", "adaptive"])
    p.set_defaults(fn=cmd_video_submit)

    p = sub.add_parser("video-status", help="query one task")
    p.add_argument("--task-id", required=True)
    p.add_argument("--json", dest="json_output", action="store_true")
    p.set_defaults(fn=cmd_video_status)

    p = sub.add_parser("video-wait", help="poll until terminal, optional --download")
    p.add_argument("--task-id", required=True)
    p.add_argument("--interval", type=int, default=10)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--download")
    p.set_defaults(fn=cmd_video_wait)

    p = sub.add_parser("video-download", help="download finished task video")
    p.add_argument("--task-id", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(fn=cmd_video_download)

    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
