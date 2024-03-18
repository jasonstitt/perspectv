# perspectv

Creates an LLM-powered summary of a business from its website.

## 💭 Introduction

`perspectv` is a command-line tool that scrapes a business website and creates a report. The content of the report is currently:

* Business summary
* Product summary
* SWOT
* Software & data strategy

LLMs are used to extract content from the pages of the company's website, and to generate the report. Two different models may be used (e.g. a low-cost extraction model and a large-context reporting model -- since the latter model is expected to take the entire website content as context).

## 🚀 Running

While `perspectv` is in beta, it must be run from the repo directory using `poetry`:

```bash
poetry run perspectv example.com
```

A single environment variable is required, `OPENROUTER_API_KEY`. Currently, (OpenRouter)[https://openrouter.ai/] is used to provide a strong model selection. In the future, it would be beneficial to support other LLM vendors directly.

## 🧂 Options

* `--dbfile`: Filename for a SQLite database used to store incremental data for the web scrape and the LLM usage. `perspectv` will by default avoid redoing the same work. Deleting the database or using a new file will start over.

* `--model-extract`: Override the OpenRouter model name used for web page extracts. This should be a low-cost model with reasonable extraction performance (many models can do this acceptably).

* `--model-report`: Override the OpenRouter model name used for report generation. This shoudl be a large-context model. The default, `anthropic/claude-3-opus`, is relatively expensive but performs well and has a 1 million token context window.
