#!/usr/bin/env python3
"""Standalone PubMed top-journal digest generator.

This script mirrors the public n8n template's core idea without requiring n8n:
search PubMed, fetch article abstracts, optionally ask an OpenAI-compatible LLM
for a short Traditional Chinese briefing, and write HTML/JSON files locally.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import pathlib
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


DEFAULT_JOURNALS = [
    "N Engl J Med",
    "Lancet",
    "JAMA",
    "BMJ",
    "Ann Intern Med",
    "JAMA Intern Med",
    "Nat Med",
    "Nature",
    "Science",
    "Cell",
]


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def request_json(url: str, params: dict[str, str], timeout: int = 30) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str, params: dict[str, str], timeout: int = 30) -> str:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def journal_query(journals: list[str], date: dt.date) -> str:
    journal_terms = " OR ".join(f'"{journal}"[Journal]' for journal in journals)
    return f"({journal_terms}) AND (hasabstract) AND \"{date:%Y/%m/%d}\"[dp]"


def search_pubmed(journals: list[str], date: dt.date, retmax: int, api_key: str) -> list[str]:
    params = {
        "db": "pubmed",
        "retmode": "json",
        "term": journal_query(journals, date),
        "retmax": str(retmax),
    }
    if api_key:
        params["api_key"] = api_key
    data = request_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params)
    return list(data.get("esearchresult", {}).get("idlist", []))


def fetch_pubmed_xml(pmids: list[str], api_key: str) -> str:
    if not pmids:
        return ""
    params = {
        "db": "pubmed",
        "retmode": "xml",
        "id": ",".join(pmids),
    }
    if api_key:
        params["api_key"] = api_key
    return request_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params)


def text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(part.strip() for part in element.itertext() if part.strip())


def parse_articles(xml_text: str) -> list[dict[str, str]]:
    if not xml_text.strip():
        return []
    root = ET.fromstring(xml_text)
    articles: list[dict[str, str]] = []
    for pubmed_article in root.findall(".//PubmedArticle"):
        medline = pubmed_article.find("MedlineCitation")
        article = medline.find("Article") if medline is not None else None
        journal = article.find("Journal") if article is not None else None
        pmid = text_content(medline.find("PMID")) if medline is not None else ""
        title = text_content(article.find("ArticleTitle")) if article is not None else ""
        journal_title = text_content(journal.find("Title")) if journal is not None else ""
        journal_iso = text_content(journal.find("ISOAbbreviation")) if journal is not None else ""
        abstract_parts = []
        if article is not None:
            for abstract_text in article.findall(".//AbstractText"):
                label = abstract_text.attrib.get("Label", "").strip()
                value = text_content(abstract_text)
                if label and value:
                    abstract_parts.append(f"{label}: {value}")
                elif value:
                    abstract_parts.append(value)
        date = text_content(article.find("Journal/JournalIssue/PubDate")) if article is not None else ""
        articles.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal_iso or journal_title,
                "date": date,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                "abstract": " ".join(abstract_parts),
            }
        )
    return articles


def llm_summary(articles: list[dict[str, str]]) -> str:
    base_url = env("LLM_BASE_URL")
    api_key = env("LLM_API_KEY")
    model = env("LLM_MODEL", env("OPENAI_MODEL", "gpt-4o-mini"))
    if not base_url or not api_key:
        return ""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是臨床文獻摘要助理。請用繁體中文，依重要性整理 PubMed 文章，"
                    "輸出短而清楚的臨床 briefing。不要捏造摘要中沒有的結果。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps({"articles": articles}, ensure_ascii=False),
            },
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        urllib.parse.urljoin(base_url.rstrip("/") + "/", "chat/completions"),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
        return f"LLM summary unavailable: {exc}"


def render_html(report_date: dt.date, articles: list[dict[str, str]], summary: str) -> str:
    items = []
    for article in articles:
        items.append(
            textwrap.dedent(
                f"""
                <li>
                  <a href="{html.escape(article['url'])}"><strong>{html.escape(article['title'])}</strong></a>
                  <div>{html.escape(article['journal'])} | {html.escape(article['date'])}</div>
                  <p>{html.escape(article['abstract'][:1400] or 'No abstract available.')}</p>
                </li>
                """
            )
        )
    summary_block = (
        f"<section><h2>LLM Briefing</h2><pre>{html.escape(summary)}</pre></section>"
        if summary
        else "<section><h2>LLM Briefing</h2><p>Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL to enable AI summarization.</p></section>"
    )
    return textwrap.dedent(
        f"""\
        <!doctype html>
        <html lang="zh-Hant">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Top Journal Daily Digest {report_date:%Y-%m-%d}</title>
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 820px; margin: 32px auto; padding: 0 16px; line-height: 1.65; color: #243447; }}
            h1 {{ color: #7a1f3d; }}
            li {{ margin-bottom: 18px; }}
            pre {{ white-space: pre-wrap; background: #f6f7f8; padding: 14px; border-radius: 8px; }}
          </style>
        </head>
        <body>
          <h1>Top Journal Daily Digest</h1>
          <p>Report date: {report_date:%Y-%m-%d} | Articles: {len(articles)}</p>
          {summary_block}
          <section><h2>Articles</h2><ol>{''.join(items)}</ol></section>
        </body>
        </html>
        """
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Publication date in YYYY-MM-DD. Defaults to today minus lookback days.")
    parser.add_argument("--lookback-days", type=int, default=int(env("DIGEST_LOOKBACK_DAYS", "1")))
    parser.add_argument("--retmax", type=int, default=int(env("DIGEST_RETMAX", "20")))
    parser.add_argument("--output-dir", default=env("DIGEST_OUTPUT_DIR", "./out"))
    parser.add_argument("--journals", default=env("DIGEST_JOURNALS", ",".join(DEFAULT_JOURNALS)))
    parser.add_argument("--no-llm", action="store_true", help="Skip optional LLM summarization.")
    args = parser.parse_args()

    report_date = (
        dt.date.fromisoformat(args.date)
        if args.date
        else dt.date.today() - dt.timedelta(days=args.lookback_days)
    )
    journals = [item.strip() for item in args.journals.split(",") if item.strip()]
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pmids = search_pubmed(journals, report_date, args.retmax, env("PUBMED_API_KEY"))
    articles = parse_articles(fetch_pubmed_xml(pmids, env("PUBMED_API_KEY")))
    summary = "" if args.no_llm else llm_summary(articles)

    stem = f"top-journal-digest-{report_date:%Y-%m-%d}"
    json_path = output_dir / f"{stem}.json"
    html_path = output_dir / f"{stem}.html"
    json_path.write_text(
        json.dumps({"date": str(report_date), "articles": articles, "summary": summary}, ensure_ascii=False, indent=2)
        + "\n"
    )
    html_path.write_text(render_html(report_date, articles, summary))
    print(f"Wrote {html_path}")
    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

