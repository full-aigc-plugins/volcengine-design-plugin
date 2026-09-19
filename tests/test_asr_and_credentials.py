from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import volcengine_asr  # noqa: E402
import volcengine_config  # noqa: E402


class AsrContractTests(unittest.TestCase):
    def test_submit_requires_exactly_one_audio_source(self) -> None:
        with self.assertRaises(SystemExit):
            volcengine_asr.main(["submit"])
        with self.assertRaises(SystemExit):
            volcengine_asr.main(["submit", "--url", "https://example.test/a.wav", "--file", "a.wav"])

    def test_failed_status_stops_immediately_and_returns_nonzero(self) -> None:
        args = argparse.Namespace(task_id="task-1", timeout=30, interval=0, json_output=False)
        response = {"status": "Failed", "message": "unsupported audio"}
        with mock.patch.object(volcengine_asr, "call_speech", return_value=response):
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                rc = volcengine_asr.cmd_wait(args)
        self.assertEqual(1, rc)
        self.assertIn("unsupported audio", stderr.getvalue())

    def test_cancelled_status_stops_immediately(self) -> None:
        args = argparse.Namespace(task_id="task-1", timeout=30, interval=0, json_output=True)
        with mock.patch.object(volcengine_asr, "call_speech", return_value={"status": "Cancelled"}):
            rc = volcengine_asr.cmd_wait(args)
        self.assertEqual(1, rc)

    def test_wait_timeout_preserves_task_id_for_recovery(self) -> None:
        args = argparse.Namespace(task_id="task-recover", timeout=1, interval=0, json_output=False)
        with mock.patch.object(volcengine_asr, "call_speech", return_value={"status": "Running"}):
            with mock.patch.object(volcengine_asr.time, "time", side_effect=[0, 2]):
                with self.assertRaisesRegex(SystemExit, "task-recover"):
                    volcengine_asr.cmd_wait(args)


@unittest.skipIf(os.name == "nt", "POSIX permission bits are not available on Windows")
class CredentialContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "config.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_rejects_group_or_world_readable_credentials(self) -> None:
        self.path.write_text(json.dumps({"ARK_API_KEY": "placeholder"}), encoding="utf-8")
        self.path.chmod(0o644)
        with mock.patch.object(volcengine_config, "CONFIG_FILE", self.path):
            with self.assertRaisesRegex(RuntimeError, "chmod 600"):
                volcengine_config._user_credentials()

    def test_malformed_json_reports_path(self) -> None:
        self.path.write_text("{bad", encoding="utf-8")
        self.path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        with mock.patch.object(volcengine_config, "CONFIG_FILE", self.path):
            with self.assertRaisesRegex(RuntimeError, re.escape(str(self.path))):
                volcengine_config._user_credentials()

    def test_rejects_credentials_owned_by_another_user(self) -> None:
        self.path.write_text(json.dumps({"ARK_API_KEY": "placeholder"}), encoding="utf-8")
        self.path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        with mock.patch.object(volcengine_config, "CONFIG_FILE", self.path):
            with mock.patch.object(volcengine_config.os, "geteuid", return_value=os.geteuid() + 1):
                with self.assertRaisesRegex(RuntimeError, "所有者"):
                    volcengine_config._user_credentials()


class ManifestContractTests(unittest.TestCase):
    def test_codex_manifest_has_interface(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["interface"]["displayName"])
        self.assertTrue(manifest["interface"]["shortDescription"])


if __name__ == "__main__":
    unittest.main()
