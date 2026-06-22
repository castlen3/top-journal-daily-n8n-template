# Output Options

The included workflow ends with email nodes because email is the easiest portable example. You can replace the final output with any of these patterns.

## Email

Use `Send Final Summary Email` with your own SMTP credential.

Good for:

- archival reading
- forwarding
- long HTML digests

## Telegram

Replace the final email node with a Telegram node or HTTP Request to the Telegram Bot API.

Recommended payload:

```json
{
  "chat_id": "={{ $env.TELEGRAM_CHAT_ID }}",
  "text": "={{ $json.text || $json.html }}",
  "parse_mode": "HTML"
}
```

Telegram may reject very long messages. For long reports, send a short summary plus a file attachment.

## WhatsApp

Use a WhatsApp Business Cloud API HTTP Request node.

Typical shape:

```json
{
  "messaging_product": "whatsapp",
  "to": "={{ $env.WHATSAPP_TO }}",
  "type": "text",
  "text": {
    "body": "={{ $json.text || $json.html }}"
  }
}
```

WhatsApp templates and opt-in rules depend on your provider and account setup.

## Local File

For a self-hosted n8n instance, replace the final email node with a file-writing step. A simple pattern is:

1. Add a Code node that returns a filename and content.
2. Add a Write Binary File node or run a controlled local command if your n8n deployment allows it.

Example filename:

```text
daily-digest-{{ $now.toFormat('yyyy-LL-dd') }}.html
```

Keep output paths environment-specific and out of public workflow exports.

