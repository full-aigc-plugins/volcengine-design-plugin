#!/usr/bin/env python3
"""豆包大模型语音合成 (TTS) v3 unidirectional HTTP deterministic client.

Facts (official docs, 大模型语音合成 v3 HTTP):
- POST https://openspeech.bytedance.com/api/v3/tts/unidirectional
- Headers: X-Api-App-Key, X-Api-Access-Key, X-Api-Resource-Id
  (volc.service_type.10029 = 豆包大模型语音合成), Content-Type: application/json.
- Body: {user:{uid}, req_params:{text, speaker, audio_params:{format, sample_rate},
  additions:{...}}}; response is a JSON event stream whose data chunks carry
  base64 audio; collect until the last chunk and write the file.

Speaker examples: zh_female_cancan_mars_bigtts, zh_male_chunhou_mars_bigtts…
(音色列表见 docs：豆包语音 → 音色列表；用 --speaker 覆盖)。
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from volcengine_config import SPEECH_BASE_URL, speech_credentials  # noqa: E402

RESOURCE_ID = "volc.service_type.10029"


def synthesize(text: str, speaker: str, audio_format: str, sample_rate: int) -> bytes:
    app_id, token = speech_credentials()
    headers = {
        "X-Api-App-Key": app_id,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": str(uuid.uuid4()),
        "Content-Type": "application/json",
    }
    payload = {
        "user": {"uid": "partme-volcengine-design"},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "audio_params": {"format": audio_format, "sample_rate": sample_rate},
        },
    }
    request = urllib.request.Request(
        SPEECH_BASE_URL + "/api/v3/tts/unidirectional",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    audio = bytearray()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            for line in response:
                line = line.strip()
                if not line.startswith(b"data:"):
                    continue
                event = json.loads(line[5:].strip())
                data = event.get("data")
                if data:
                    audio.extend(base64.b64decode(data))
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code}: {exc.read().decode()[:400]}")
    if not audio:
        sys.exit("未收到音频数据（检查音色名/文本长度/凭据）")
    return bytes(audio)


def main() -> int:
    parser = argparse.ArgumentParser(description="豆包 TTS deterministic client")
    parser.add_argument("--text", required=True, help="要合成的文本（长文本自行分段调用）")
    parser.add_argument("--speaker", default="zh_female_cancan_mars_bigtts")
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav", "pcm", "ogg_opus"])
    parser.add_argument("--sample-rate", type=int, default=24000)
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    audio = synthesize(args.text, args.speaker, args.format, args.sample_rate)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(audio)
    print(json.dumps({"saved": str(target), "bytes": len(audio), "speaker": args.speaker}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
