#!/usr/bin/env python3
"""Sanitize a private n8n workflow export into a public template."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


SECRET_RE = re.compile(r"^[a-f0-9]{32,}$", re.IGNORECASE)
EMAIL_RE = re.compile(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}")
LOCAL_IP_RE = re.compile(r"\b(?:10|127|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b")


def walk_replace(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in list(value.items()):
            if key == "api_key" or (isinstance(item, str) and SECRET_RE.fullmatch(item)):
                value[key] = '={{ $env.PUBMED_API_KEY || "" }}'
            else:
                walk_replace(item)
    elif isinstance(value, list):
        for item in value:
            walk_replace(item)


def sanitize(workflow: dict[str, Any], replacements: list[str] | None = None) -> dict[str, Any]:
    public = {
        "name": "Top Journal Daily Digest - Public Template",
        "nodes": copy.deepcopy(workflow["nodes"]),
        "connections": copy.deepcopy(workflow["connections"]),
        "settings": {"executionOrder": "v1", "timezone": "Asia/Taipei"},
        "staticData": None,
        "pinData": {},
        "meta": {"templateCredsSetupCompleted": False},
        "tags": ["pubmed", "literature-review", "daily-digest", "template"],
    }

    for node in public["nodes"]:
        node.pop("credentials", None)
        node.pop("webhookId", None)
        if "id" in node:
            node["id"] = f"template-{str(node['id'])[:8]}"

        params = node.get("parameters") or {}
        walk_replace(params)

        if node.get("name") == "Search PubMed Articles":
            query_params = params.get("queryParameters", {}).get("parameters", [])
            for kv in query_params:
                if kv.get("name") == "api_key":
                    kv["value"] = '={{ $env.PUBMED_API_KEY || "" }}'
                if kv.get("name") == "=term":
                    kv["value"] = (
                        '=( ("N Engl J Med"[Journal]) OR ("Lancet"[Journal]) OR '
                        '("JAMA"[Journal]) OR ("BMJ"[Journal]) OR '
                        '("Ann Intern Med"[Journal]) OR ("JAMA Intern Med"[Journal]) OR '
                        '("Nat Med"[Journal]) OR ("Nature"[Journal]) OR '
                        '("Science"[Journal]) OR ("Cell"[Journal]) ) '
                        'AND (hasabstract) '
                        'AND "{{ $now.minus({days: 1}).toFormat(\'yyyy/MM/dd\') }}"[dp]'
                    )

        if node.get("name") in {"Send No Results Email", "Send Final Summary Email"}:
            params["fromEmail"] = "={{ $env.DIGEST_FROM_EMAIL }}"
            params["toEmail"] = "={{ $env.DIGEST_TO_EMAIL }}"
            node["notes"] = (
                "Output example. Replace with Telegram, WhatsApp, Notion, "
                "local file writing, or your own email credential."
            )

        if node.get("name") == "OpenAI Chat Model":
            params["model"] = {
                "__rl": True,
                "value": '={{ $env.OPENAI_MODEL || "qwen/qwen3.5-9b" }}',
                "mode": "list",
                "cachedResultName": "Configurable chat model",
            }
            params["options"] = {"timeout": 600000}
            node["notes"] = (
                "Add your own OpenAI-compatible credential. For local LLMs, "
                "configure the credential base URL in n8n, not in this public template."
            )

        if node.get("name") == "OpenRouter Model Final Summary":
            params["model"] = '={{ $env.OPENROUTER_MODEL || "deepseek/deepseek-v4-flash" }}'
            node["disabled"] = True
            node["notes"] = (
                "Optional disabled example. The workflow currently uses the "
                "OpenAI Chat Model node for both LLM chains."
            )

    serialized = json.dumps(public, ensure_ascii=False)
    serialized = EMAIL_RE.sub("reader@example.com", serialized)
    serialized = LOCAL_IP_RE.sub("LOCAL_LLM_HOST", serialized)

    for replacement in replacements or []:
        if "=" not in replacement:
            raise ValueError(f"Invalid replacement {replacement!r}; expected private=public")
        private, public_text = replacement.split("=", 1)
        serialized = serialized.replace(private, public_text)

    return json.loads(serialized)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--replace",
        action="append",
        default=[],
        help="Extra text replacement in private=public form. Can be passed multiple times.",
    )
    args = parser.parse_args()

    workflow = json.loads(args.input.read_text())
    public = sanitize(workflow, args.replace)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
