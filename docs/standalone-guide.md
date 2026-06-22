# Standalone Script Guide

This project can run without n8n. The standalone script is useful when you want a simple cron, launchd, GitHub Actions, or server job.

## Run Once

```bash
python3 scripts/daily_top_journal_digest.py --output-dir ./out --retmax 10 --no-llm
```

This writes:

- `out/top-journal-digest-YYYY-MM-DD.html`
- `out/top-journal-digest-YYYY-MM-DD.json`

## Optional LLM Summary

Set an OpenAI-compatible endpoint:

```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="your-key"
export LLM_MODEL="gpt-4o-mini"
python3 scripts/daily_top_journal_digest.py --output-dir ./out
```

The script still works without an LLM; it will render PubMed metadata and abstracts.

## Configuration

Environment variables:

- `PUBMED_API_KEY`: optional NCBI key.
- `DIGEST_OUTPUT_DIR`: output folder, default `./out`.
- `DIGEST_LOOKBACK_DAYS`: default `1`.
- `DIGEST_RETMAX`: default `20`.
- `DIGEST_JOURNALS`: comma-separated journal list.
- `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`: optional AI summary.

## Scheduling Choices

- n8n: import `workflows/top-journal-daily-template.json`.
- launchd: use `launchd/com.example.top-journal-digest.plist`.
- cron or systemd: call `python3 scripts/daily_top_journal_digest.py`.
- GitHub Actions: call the same script and upload the output artifact.

