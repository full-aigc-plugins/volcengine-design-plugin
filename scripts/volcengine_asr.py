#!/usr/bin/env python3
"""豆包大模型录音文件识别 (bigmodel ASR) deterministic client.

Facts (official docs, 录音文件识别 2.0 / bigmodel):
- Submit: POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit
- Query:  POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/query
- Headers: Authorization: Bearer; {access_token} (note the "; " separator),
  X-Api-App-Key: {app_id}, X-Api-Resource-Id: volc.bigasr.auc.duration (2.0),
  X-Api-Request-Id: uuid.
- Audio: URL ("audio_url") or base64 ("data"); duration-capped model handles
  long audio; result carries utterances with per-word millisecond timestamps.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from volcengine_config import SPEECH_BASE_URL, speech_credentials  # noqa: E402

RESOURCE_ID = "volc.bigasr.auc.duration"
TERMINAL = {"Completed", "completed"}


def call_speech(path: str, payload: dict, request_id: str) -> dict:
    app_id, token = speech_credentials()
    headers = {
        "Authorization": f"Bearer; {token}",
        "X-Api-App-Key": app_id,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": request_id,
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(
        SPEECH_BASE_URL + path, data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code} from {path}: {exc.read().decode()[:400]}")


def audio_payload(args: argparse.Namespace) -> dict:
    payload: dict = {"user": {"uid": "partme-volcengine-design"}}
    audio: dict = {"format": args.format}
    if args.url:
        audio["url"] = args.url
    else:
        raw = Path(args.file).read_bytes()
        audio["data"] = base64.b64encode(raw).decode()
    payload["audio"] = audio
    if args.model:
        payload["model_name"] = args.model
    if args.language:
        payload["request"] = {"model_name": args.language}
    return payload


def cmd_submit(args: argparse.Namespace) -> int:
    request_id = str(uuid.uuid4())
    result = call_speech("/api/v3/auc/bigmodel/submit", audio_payload(args), request_id)
    print(json.dumps({"request_id": request_id, "task_id": result.get("id"), "resp": result}, ensure_ascii=False))
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    request_id = args.request_id or str(uuid.uuid4())
    result = call_speech("/api/v3/auc/bigmodel/query", {"id": args.task_id}, request_id)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    resp = result.get("result", result)
    text = resp.get("text", "")
    print(json.dumps({"task_id": args.task_id, "status": result.get("status"), "text": text[:200]}, ensure_ascii=False))
    return 0


def cmd_wait(args: argparse.Namespace) -> int:
    deadline = time.time() + args.timeout
    result: dict = {}
    while True:
        request_id = str(uuid.uuid4())
        result = call_speech("/api/v3/auc/bigmodel/query", {"id": args.task_id}, request_id)
        status = result.get("status")
        print(json.dumps({"task_id": args.task_id, "status": status}, ensure_ascii=False), flush=True)
        if status in TERMINAL:
            if args.json_output:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if status in ("Completed", "completed") else 1
        if time.time() > deadline:
            sys.exit(f"轮询超时（{args.timeout}s）；task_id={args.task_id} 已持久化，可稍后 query 恢复")
        time.sleep(args.interval)


def cmd_words(args: argparse.Namespace) -> int:
    """Print the millisecond word timeline (the 口播 slicing base)."""
    request_id = str(uuid.uuid4())
    result = call_speech("/api/v3/auc/bigmodel/query", {"id": args.task_id}, request_id)
    resp = result.get("result", result)
    utterances = resp.get("utterances", [])
    for utt in utterances:
        words = utt.get("words", [])
        for w in words:
            print(json.dumps({
                "start": w.get("start_time"),
                "end": w.get("end_time"),
                "word": w.get("text", ""),
                "utterance_end": utt.get("end_time"),
            }, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="豆包大模型录音文件识别 deterministic client")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", default="wav", help="wav/mp3/m4a…")
    common.add_argument("--url", help="音频公网 URL（与 --file 二选一）")
    common.add_argument("--file", help="本地音频文件（base64 上传）")
    common.add_argument("--model", default="bigmodel", help="bigmodel / 2.0 形态名")
    common.add_argument("--language", default="zh-CN")

    p = sub.add_parser("submit", parents=[common], help="submit one transcription task")
    p.set_defaults(fn=cmd_submit)

    p = sub.add_parser("query", parents=[common], help="query once")
    p.add_argument("--task-id", required=True)
    p.add_argument("--request-id", help="原始 request_id（可选）")
    p.add_argument("--json", dest="json_output", action="store_true")
    p.set_defaults(fn=cmd_query)

    p = sub.add_parser("wait", parents=[common], help="poll until Completed")
    p.add_argument("--task-id", required=True)
    p.add_argument("--interval", type=int, default=10)
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--json", dest="json_output", action="store_true")
    p.set_defaults(fn=cmd_wait)

    p = sub.add_parser("words", help="print millisecond word timeline")
    p.add_argument("--task-id", required=True)
    p.set_defaults(fn=cmd_words)

    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
