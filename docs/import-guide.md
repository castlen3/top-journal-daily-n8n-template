# Import Guide

## Requirements

- n8n instance with HTTP Request, Code, Schedule Trigger, and Email Send nodes.
- An LLM credential compatible with the n8n LangChain chat model node.
- Optional PubMed API key from NCBI.

## Import

1. Open n8n.
2. Choose **Import from file**.
3. Select `workflows/top-journal-daily-template.json`.
4. Save the workflow under your own name.

## Configure

Check these nodes first:

- `Daily Schedule`: set your desired hour, minute, and timezone.
- `Search PubMed Articles`: adjust journals, date range, `retmax`, or PubMed query terms.
- `OpenAI Chat Model`: attach your own OpenAI-compatible credential and model.
- `Send Final Summary Email`: replace with your preferred output node.
- `Send No Results Email`: optional fallback when PubMed returns no articles.

## PubMed Query

The template uses a broad top-journal query:

```text
(top journal list) AND (hasabstract) AND yesterday[dp]
```

You can adapt it for a specialty:

```text
("Lancet"[Journal] OR "JAMA"[Journal])
AND (primary care OR pediatrics OR prevention)
AND (hasabstract)
AND "2026/06/21"[dp]
```

## Testing

Run manually with a small `retmax` such as `5` before activating. Once the output looks right, raise `retmax` and activate the workflow.

