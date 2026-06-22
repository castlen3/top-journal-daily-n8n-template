# Security Checklist

Before sharing or publishing an n8n workflow:

- Remove `credentials` blocks from every node.
- Remove real API keys, tokens, webhook URLs, email addresses, phone numbers, and chat IDs.
- Remove local IP addresses, internal hostnames, private file paths, and deployment commands.
- Replace personal names and private reader context with neutral wording.
- Use environment variables or placeholders for configurable values.
- Keep raw exports in `private-source/`, which is ignored by Git.
- Run a text scan before committing.

Suggested scan:

```bash
rg -n "api_key|credential|password|token|Bearer|@[A-Za-z0-9.-]+|192\\.168|localhost|ngrok|private|internal|gmail|whatsapp|telegram" .
```

Some placeholder words may still match. Review each hit before publishing.
