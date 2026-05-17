---
name: literature-search
description: Search arXiv, CrossRef, IEEE, Elsevier, Springer, NCBI PubMed, CORE, Wiley, and Scholarly for related work; deduplicate, score, and emit literature/shortlist.json + paper/refs.bib
---

Run a federated literature search across nine academic sources, deduplicate,
rank by relevance × recency × citation count, and produce a shortlist + BibTeX
ready for Bob to cite.

<Steps>
<Step>
**Generate queries** from `paper/analysis.json`. Write 4–6 queries to
`paper/queries.json` covering:
- Problem domain (e.g. "few-shot image classification with vision transformers")
- Method family (e.g. "LoRA fine-tuning")
- Dataset (e.g. "ImageNet-1k benchmark")
- Evaluation protocol (e.g. "mean average precision retrieval")
</Step>

<Step>
**Foundational-paper seeds (mandatory)**. Inspect `analysis.json.model.backbone`,
`analysis.model.framework`, and `analysis.related_work_context.base_methods`.
For each foundational concept the paper will cite at first mention, append a
dedicated single-result seed query to `paper/queries.json` with `dimension: "foundation"`:

| Detected | Seed query text |
|----------|-----------------|
| CLIP / ViT-B | "Learning Transferable Visual Models From Natural Language Supervision Radford" |
| Transformer | "Attention Is All You Need Vaswani 2017" |
| ViT | "An Image is Worth 16x16 Words Dosovitskiy 2020" |
| ResNet | "Deep Residual Learning for Image Recognition He 2015" |
| BERT | "BERT Pre-training of Deep Bidirectional Transformers" |
| LoRA | "LoRA: Low-Rank Adaptation of Large Language Models Hu 2021" |
| CoOp | "Learning to Prompt for Vision-Language Models Zhou 2022" |
| MaPLe | "MaPLe Multi-modal Prompt Learning Khattak 2023" |

If a seed paper does NOT appear in the final shortlist after dedupe + rank,
re-run a targeted single-query search with `--top 1` and `--append paper/refs.bib`
so the foundational citation is guaranteed to resolve.

`paper/queries.json` schema:
```json
{
  "queries": [
    {"id": "q1", "text": "...", "dimension": "problem|method|dataset|evaluation", "max_results": 30}
  ],
  "year_min": 2018,
  "sources": ["arxiv", "crossref", "openalex", "ncbi_pubmed", "core", "ieee", "springer", "elsevier", "wiley"]
}
```
</Step>

<Step>
**Run the federated search**:
```
uv run python -m literature.search --queries paper/queries.json --out literature/raw/
```
This invokes one searcher per source. Searchers requiring API keys (IEEE,
Elsevier, Wiley) will skip with a logged warning if the env var is missing
(`IEEE_API_KEY`, `ELSEVIER_API_KEY`, `WILEY_TDM_TOKEN`). Open sources
(arXiv, CrossRef, OpenAlex/Scholarly, NCBI, CORE, Springer Open Access) work
without keys.
</Step>

<Step>
**Deduplicate** by DOI first, then by normalized title (lowercase, strip
punctuation, collapse whitespace, Levenshtein < 5):
```
uv run python -m literature.dedupe --in literature/raw/ --out literature/dedup.json
```
</Step>

<Step>
**Rank** with the formula `score = 0.5*relevance + 0.3*recency + 0.2*log(citations+1)`:
```
uv run python -m literature.rank --in literature/dedup.json --top 30 --out literature/shortlist.json
```
- `relevance` = max cosine similarity between query embedding and abstract
  embedding (uses `sentence-transformers/all-MiniLM-L6-v2`, downloaded once).
- `recency` = exp(-(current_year - paper_year) / 5).
- `citations` = OpenAlex citation count where available, else 0.
</Step>

<Step>
**Generate BibTeX** for the shortlist:
```
uv run python -m literature.to_bibtex --in literature/shortlist.json --out paper/refs.bib
```
Each entry uses key format `<firstauthor><year><firstword>`, lowercase.
</Step>

<Step>
**Hand back** to Bob a markdown table summarizing the shortlist (title, year,
venue, one-line "why relevant"). Bob will surface this at Checkpoint 2.
</Step>
</Steps>

Never fabricate a paper. If a source returns nothing, log it and continue.
If fewer than 10 papers survive the shortlist, ask the scientist to broaden
queries before proceeding.
