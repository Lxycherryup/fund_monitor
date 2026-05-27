from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class FeishuNotifier:
    def __init__(self, webhook_url: str | None = None, dry_run: bool = False, timeout: float = 8.0):
        self.webhook_url = webhook_url or os.environ.get("FEISHU_WEBHOOK_URL")
        self.dry_run = dry_run
        self.timeout = timeout

    def send_text(self, text: str) -> None:
        if self.dry_run:
            print(text)
            return
        if not self.webhook_url:
            raise RuntimeError("FEISHU_WEBHOOK_URL is required unless --dry-run is used")

        payload = json.dumps(
            {"msg_type": "text", "content": {"text": text}},
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            self.webhook_url,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"failed to send Feishu message: {exc}") from exc

        if '"StatusCode":0' not in body and '"code":0' not in body:
            raise RuntimeError(f"Feishu webhook returned non-success response: {body}")
