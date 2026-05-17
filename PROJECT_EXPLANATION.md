# IBM Bob — New Skill Unlocked: Code2Paper

## "Bob, Analyse My Codebase and Write Me a Research Paper."

*Yes. You heard that right.*

---

## What is IBM Bob?

**IBM Bob** is IBM's enterprise AI agent — a powerful orchestrator that coordinates skills, tools, and workflows to get complex jobs done. Bob already knows how to analyze code, search documentation, summarize reports, and assist developers.

But at this hackathon, we asked Bob a question nobody had asked before:

> *"Can you turn my research codebase into a publication-ready research paper?"*

The answer — after a lot of engineering, late nights, and some very creative prompt design — is **yes**.

---

## The Problem We Solved

**Imagine this:** You've spent 6 months building a novel machine learning model. The code works. The results look promising. But now comes the part every researcher dreads — writing the paper.

You're staring at a blank document. Your codebase has 10,000 lines of PyTorch. You need to produce a NeurIPS-ready PDF with:
- A polished methodology section with mathematical formulations
- An architecture diagram that explains your model at a glance
- Comparative tables showing your results beat the baselines
- Properly formatted citations from 30+ relevant papers
- Figures with captions that tell the scientific story

That's weeks of work. **I gave it to Bob.**

---

## What I Built: The `code2paper` Mode

I extended IBM Bob with a brand-new orchestration mode — **`code2paper`** — a suite of coordinated AI skills that transforms a research codebase into a complete academic paper.

This isn't "generate some text about my code." This is a full pipeline with **specialized agents** that reason about your research the way a senior scientist would.

---

## How It Works: Bob's New Skill Stack

### 🔍 Skill 1: `codebase-analyzer`
Bob doesn't just read files. It builds a **semantic map** of your research:
- Identifies model architecture, training procedure, loss functions
- Extracts parameter counts, hyperparameters, evaluation settings
- Understands what's novel vs. what's borrowed from prior work

### 📚 Skill 2: `literature-search`
Bob reads the literature so you don't have to:
- Generates targeted search queries from your methodology
- Retrieves, deduplicates, and ranks relevant academic papers
- Identifies the exact foundational works that must be cited
- Writes the novelty statement: *"What gap does this fill?"*

### 🗺️ Skill 3: `figure-planner`
Here's where it gets interesting. Research figures aren't just visuals — they're **semantic reasoning artifacts**. Bob's figure planner decides:
- Which sections need figures and which type (architecture, ablation, Pareto curve)
- What the *intent* of each figure is ("show parameter efficiency", "prove gradient equalization")
- Which mathematical equations should be anchored to which diagram blocks
- What a reviewer is likely to question — and how the figure should preemptively answer it

### 🎨 Skill 4: `figure-drafter` + `figure-critic`
Bob doesn't produce generic flowcharts. It uses **multiple renderers** depending on figure type:
- **CeTZ/fletcher** for vector architecture diagrams in Typst
- **Matplotlib** with venue-specific stylesheets (NeurIPS color palettes, font sizes, aspect ratios)
- **Gemini API** (`gemini-3.1-flash-lite` for planning, `gemini-3-pro-image-preview` for image generation) for complex visual compositions

Then a **critic agent** runs six independent passes on every figure:
1. Legibility — fonts readable at print size?
2. Formula correctness — equations match the text?
3. Color palette — venue-compliant, colorblind-safe?
4. Narrative alignment — does the figure prove what the paper claims?
5. Venue grammar — NeurIPS vs CVPR have different visual conventions
6. Reviewer coverage — does it answer the obvious pushback?

### 📊 Skill 5: `table-generator`
Publication tables are not spreadsheets. Bob generates:
- Comparative tables with proper **bold** best results and _underlined_ second-best
- Ablation studies showing each component's contribution
- Parameter efficiency tables, dataset statistics, domain generalization results
- All following the strict "no vertical rules, no [N/A] cells" conventions of top venues

### ✍️ Skill 6: `section-drafter`
Bob drafts each section knowing what it can and cannot say:
- Introduction cannot quote results numbers (those belong in Section 5)
- Methodology must include the architecture figure reference
- Results must cite every table and figure, no orphaned floats
- Every claim traces back to either code evidence or a literature citation

### 🔧 Skill 7: `paper-assembler`
The final step: Bob compiles everything into a formatted PDF using **Typst** (the modern LaTeX replacement), verifies all cross-references, checks every figure and table is actually cited in prose, and produces a compile report.

---

## The Design Journey: From Docs to Innovation

Before writing a single line of code, I spent days studying **IBM Bob's documentation** — understanding the skill system, rule orchestration, and how Bob coordinates multiple agents. I realized Bob already had the infrastructure to chain skills together, but nobody had applied it to research communication.

I then analyzed **PaperBanana** — an existing AI research paper image-diagram generation system. It had good ideas, but I found critical flaws:
- It produced **generic diagrams** that looked like flowcharts, not scientific figures
- It treated figures as **visual graphics**, not semantic reasoning artifacts
- It lacked **venue awareness** — NeurIPS papers need different visual grammar than just any conference
- It couldn't handle **equation integration** — formulas weren't anchored to diagram blocks
- It missed **reviewer-target coverage** — figures didn't preemptively answer obvious pushback

The core problem: PaperBanana generalized. It tried to make "any paper" and ended up making "no paper."

My solution: **Don't generalize.** Make Bob understand the *specific* rhetoric of research. I designed:
- A literature review pipeline that reads actual papers, not just abstracts
- Figure manifests with `intent`, `narrative`, `reviewer_targets` — treating figures as scientific communication objects
- Venue-specific visual grammars (NeurIPS color palettes, font sizes, aspect ratios)
- Equation anchoring systems that bind math to diagram blocks
- A critic agent that runs six independent passes per figure

The result: Bob doesn't just draw pictures — it produces figures that *argue*.

---

## The Struggles (The Real Story)

This wasn't a clean weekend project. Here are the battles I fought:

**⚡ Typst Compatibility**
The official NeurIPS Typst template (`bloated-neurips:0.5.0`) uses deprecated `locate()` syntax that breaks on Typst 0.14.2. I hand-crafted a NeurIPS-compliant layout from scratch.

**⚡ Gemini Image Format Bug**
Gemini's image generation API returns JPEG bytes but names the file `.png`. Typst tried to decode it as PNG and threw *"Invalid PNG signature"*. I implemented magic-byte detection in `viz_arch.py` to auto-detect the real format and rename before embedding.

**⚡ Headless Matplotlib**
Matplotlib's default backend (`TkAgg`) requires a display. On the server there's none. `_tkinter.TclError: Can't find a usable init.tcl`. I forced `Agg` backend before any import.

**⚡ Label Format Mismatch**
Typst tables had `<tab_foo>` labels. The reference-checking system expected `<tab:foo>`. Eight files, eight inconsistencies. I standardized across the entire pipeline.

**⚡ Figure Intent vs Figure Graphic**
The hardest problem: existing diagram generators produce *graphics*. Research needs *scientific communication objects*. I solved this by introducing a manifest format where every figure has an `intent`, a `narrative`, `reviewer_targets`, and equation `anchors` — making Bob reason about *why* a figure exists, not just *what* it looks like.

---

## The Output: A Real Paper, Fully Generated

Bob was given the **MMRL++** research codebase — a vision-language model for parameter-efficient prompt learning — and produced a complete NeurIPS-style paper:

| What Was Generated | Detail |
|---|---|
| **9 paper sections** | Abstract, Intro, Related Work, Methodology, Experiments, Results, Discussion, Conclusion, Broader Impact |
| **1 architecture diagram** | Gemini-generated, embedded with equations and parameter counts |
| **4 visualization plots** | Pareto frontier, rank ablation, beta sweep, gradient flow analysis |
| **8 comparative tables** | Base-to-novel, few-shot, cross-dataset, ImageNet variants, efficiency, 3× ablation |
| **30+ citations** | Retrieved, ranked, and formatted in IEEE style |
| **1 compiled PDF** | 920KB, publication-formatted, all references verified |

Every number is synthetic-but-realistic. Every figure caption tells the scientific story. Every table bolds the right winner.

---

## Why This Matters

Globally, **2 million+ researchers** publish papers every year. The average time from "working code" to "submitted paper" is **4–8 weeks** of writing, figure-making, and formatting work.

Bob's `code2paper` mode compresses that to **hours**.

And unlike generic AI writing assistants, Bob doesn't just rephrase your README. It understands:
- Scientific rhetoric and argumentation structure
- Venue-specific visual grammar (NeurIPS looks different from CVPR)
- Mathematical notation and equation integration
- The difference between a claim and evidence
- What reviewers will push back on — and how to preempt it

---

## Technical Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | IBM Bob (custom `code2paper` mode) |
| Document Compilation | Typst 0.14.2 |
| Vector Diagrams | CeTZ + Fletcher (Typst packages) |
| Plots | Matplotlib (Agg backend, venue stylesheets) |
| AI Image Generation | Gemini-3.1-flash-lite + gemini-3-pro-image-preview |
| Literature Pipeline | Semantic search → dedup → rank → BibTeX |
| Reference Verification | Custom `check_refs.py` |

---

## The Bottom Line

> IBM Bob already knew how to work with your code.  
> Now Bob knows how to **write the paper too.**

Give Bob a GitHub repo. Get back a research paper.

**The code is real. The paper is generated. Bob did it.**

---

*Hackathon Submission — IBM Bob: Code2Paper Mode — May 2026*
