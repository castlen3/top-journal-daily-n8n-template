# Top Journal Daily Digest

A public, privacy-safe template for building a daily clinical literature digest from PubMed.

You can run it three ways:

- Import the n8n workflow.
- Run the standalone Python script.
- Schedule the standalone script with macOS launchd, cron, systemd, or another scheduler.

The digest searches selected top journals, fetches PubMed metadata and abstracts, optionally asks an LLM for a briefing, renders a mobile-friendly HTML digest, and writes or sends it to an output channel you choose.

## What This Includes

- `workflows/top-journal-daily-template.json`: importable n8n workflow template.
- `scripts/daily_top_journal_digest.py`: standalone script that does not require n8n.
- `launchd/com.example.top-journal-digest.plist`: macOS launchd scheduling template.
- `docs/import-guide.md`: how to import and configure the workflow.
- `docs/standalone-guide.md`: how to run without n8n.
- `docs/launchd-guide.md`: how to schedule on macOS.
- `docs/output-options.md`: email, Telegram, WhatsApp, and local-file output patterns.
- `docs/security-checklist.md`: what to verify before publishing or sharing.
- `scripts/sanitize_workflow.py`: repeatable sanitizer for private n8n exports.
- `examples/workflow-summary.json`: short metadata summary of the template.

## Default Workflow

The template searches PubMed for articles from:

`N Engl J Med`, `Lancet`, `JAMA`, `BMJ`, `Ann Intern Med`, `JAMA Intern Med`, `Nat Med`, `Nature`, `Science`, and `Cell`.

By default it looks at the previous publication date. The n8n and launchd examples both use `06:30`, but the standalone script can be called by any scheduler.

## Quick Start

### Option A: n8n

1. Import `workflows/top-journal-daily-template.json` into n8n.
2. Add your own credentials for PubMed if desired, SMTP or another output channel, and an OpenAI-compatible LLM.
3. Open the schedule node and confirm the timezone and trigger time.
4. Test manually before activating.
5. Replace the final email node if you prefer Telegram, WhatsApp, Notion, Google Drive, or a local file.

### Option B: No n8n

```bash
python3 scripts/daily_top_journal_digest.py --output-dir ./out --retmax 10 --no-llm
```

This writes an HTML and JSON digest under `out/`.

### Option C: macOS launchd

Copy `launchd/com.example.top-journal-digest.plist` to `~/Library/LaunchAgents/`, replace placeholder paths, validate with `plutil`, and load with `launchctl`.

See `docs/launchd-guide.md`.

## Privacy

The public workflow has been sanitized. It does not include private email addresses, API keys, credential IDs, hostnames, local IPs, internal paths, or personal deployment notes.

The folder `private-source/` is intentionally ignored by Git and is only for local private exports.
