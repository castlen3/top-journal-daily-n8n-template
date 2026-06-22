# Top Journal Daily Digest for n8n

A public, privacy-safe n8n template for building a daily clinical literature digest from PubMed.

The workflow searches selected top journals, fetches PubMed metadata and abstracts, triages articles with an LLM, renders a mobile-friendly HTML digest, and sends it to an output channel you choose.

## What This Includes

- `workflows/top-journal-daily-template.json`: importable n8n workflow template.
- `docs/import-guide.md`: how to import and configure the workflow.
- `docs/output-options.md`: email, Telegram, WhatsApp, and local-file output patterns.
- `docs/security-checklist.md`: what to verify before publishing or sharing.
- `scripts/sanitize_workflow.py`: repeatable sanitizer for private n8n exports.
- `examples/workflow-summary.json`: short metadata summary of the template.

## Default Workflow

The template searches PubMed for articles from:

`N Engl J Med`, `Lancet`, `JAMA`, `BMJ`, `Ann Intern Med`, `JAMA Intern Med`, `Nat Med`, `Nature`, `Science`, and `Cell`.

By default it looks at the previous publication date and runs daily at `06:30` in the workflow timezone.

## Quick Start

1. Import `workflows/top-journal-daily-template.json` into n8n.
2. Add your own credentials for PubMed if desired, SMTP or another output channel, and an OpenAI-compatible LLM.
3. Open the schedule node and confirm the timezone and trigger time.
4. Test manually before activating.
5. Replace the final email node if you prefer Telegram, WhatsApp, Notion, Google Drive, or a local file.

## Privacy

The public workflow has been sanitized. It does not include private email addresses, API keys, credential IDs, hostnames, local IPs, internal paths, or personal deployment notes.

The folder `private-source/` is intentionally ignored by Git and is only for local private exports.

