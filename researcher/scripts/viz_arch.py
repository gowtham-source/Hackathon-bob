"""Multi-agent architecture diagram generator.

Pipeline (inspired by PaperBanana https://github.com/dwzhu-pku/PaperBanana but
specialized for venue-quality architecture figures):

  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │ Planner Agent   │──▶│ Renderer Agent   │──▶│ Critic Agent     │
  │ gemini-3.1-     │   │ gemini-3-pro-    │   │ gemini-3.1-      │
  │ flash-lite      │   │ image-preview    │   │ flash-lite       │
  │ (text)          │   │ (image)          │   │ (multimodal)     │
  └─────────────────┘   └──────────────────┘   └──────────────────┘
       │                       │                        │
       ▼                       ▼                        ▼
  blueprint.json           diagram.png             critique.json
                          + diagram.typ (CeTZ fallback)

The PLANNER ingests the figure spec + paper/analysis.json and produces a
structured *diagram blueprint*:
  - canonical module list with semantic roles (input/frozen/learnable/fusion/output/loss)
  - spatial layout (rows, columns, parallel branches)
  - color assignments from the venue palette
  - equations pinned to specific blocks
  - data-flow arrows with labels
  - reviewer-targeted annotations (e.g. parameter counts on blocks)
  - per-element typography (block label, equation, annotation)

The RENDERER takes the blueprint and emits TWO artifacts:
  (a) A Typst CeTZ/fletcher .typ file (deterministic, vector, fully editable)
  (b) Optionally a PNG/SVG via gemini-3-pro-image-preview when high-fidelity
      illustration is requested (qualitative samples, schematic art)

The CRITIC reads the rendered artifact + the blueprint and returns a
structured critique covering: legibility, formula anchoring, palette
compliance, narrative alignment, venue grammar, reviewer-target coverage.

Up to 3 refine iterations.

All Gemini calls are wrapped in `_gemini_call(...)` which:
  - reads GEMINI_API_KEY from env
  - falls back to a deterministic rule-based stub if the API is unavailable
  - logs every call to paper/figures/<fig_id>.agent_log.jsonl

The CeTZ/fletcher emitter (the rule-based fallback) is preserved from the
original viz_arch.py and used when the LLM blueprint is empty or invalid.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


def _load_dotenv(start: Path = Path.cwd()) -> None:
    """Minimal .env loader (no python-dotenv dependency).

    Walks up from `start` looking for a `.env` file and injects its
    KEY=VALUE pairs into os.environ if not already present. Lines starting
    with `#` and blank lines are skipped. Surrounding quotes are stripped.
    """
    for parent in [start, *start.parents]:
        env_file = parent / ".env"
        if env_file.exists():
            try:
                for raw in env_file.read_text(encoding="utf-8").splitlines():
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
            except OSError:
                pass
            return


_load_dotenv()


# ---------------------------------------------------------------------------
# Constants and palettes
# ---------------------------------------------------------------------------

SEMANTIC_TINTS = {
    "input": "#E0E0E0",
    "frozen": "#CFD8DC",
    "learnable": "#FFE0B2",
    "fusion": "#BBDEFB",
    "loss": "#FFCDD2",
    "output": "#C8E6C9",
    "regularizer": "#F8BBD0",
}

VENUE_PALETTES = {
    "neurips": ["#000000", "#0072B2", "#D55E00", "#009E73", "#CC79A7"],
    "cvpr":    ["#000000", "#0072B2", "#D55E00", "#009E73", "#F0E442"],
    "ieee":    ["#000000", "#444444", "#888888", "#0072B2"],
    "springer":["#000000", "#0072B2", "#D55E00", "#009E73"],
    "nature":  ["#222222", "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728"],
}

PLANNER_MODEL = "gemini-3.1-flash-lite"
RENDERER_IMAGE_MODEL = "gemini-3-pro-image-preview"
CRITIC_MODEL = "gemini-3.1-flash-lite"


# ---------------------------------------------------------------------------
# Gemini API thin wrapper
# ---------------------------------------------------------------------------

@dataclass
class AgentLog:
    fig_id: str
    log_path: Path
    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(self, agent: str, model: str, prompt: str, response: Any, latency_ms: int, error: Optional[str] = None) -> None:
        entry = {
            "ts": time.time(),
            "agent": agent,
            "model": model,
            "prompt_preview": prompt[:400],
            "response_preview": (json.dumps(response)[:1000] if not isinstance(response, str) else response[:1000]),
            "latency_ms": latency_ms,
            "error": error,
        }
        self.entries.append(entry)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def _gemini_text(prompt: str, model: str, *, response_schema: Optional[dict] = None, log: Optional[AgentLog] = None, agent_name: str = "") -> tuple[Any, Optional[str]]:
    """Call a Gemini text model. Returns (parsed_response, error_or_None).

    Falls back to (None, "no_api_key") when GEMINI_API_KEY is not set OR the
    google-genai package is not installed. Callers are expected to provide a
    rule-based fallback in that case.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        if log:
            log.record(agent_name, model, prompt, None, 0, "no_api_key")
        return None, "no_api_key"
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
    except ImportError:
        if log:
            log.record(agent_name, model, prompt, None, 0, "google-genai not installed")
        return None, "google-genai not installed (uv add google-genai)"

    t0 = time.time()
    try:
        client = genai.Client(api_key=api_key)
        config_args: dict[str, Any] = {"response_mime_type": "application/json"} if response_schema else {}
        if response_schema:
            config_args["response_schema"] = response_schema
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_args) if config_args else None,
        )
        text = resp.text or ""
        parsed: Any = text
        if response_schema:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", text, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
        latency = int((time.time() - t0) * 1000)
        if log:
            log.record(agent_name, model, prompt, parsed, latency)
        return parsed, None
    except Exception as e:  # pragma: no cover
        latency = int((time.time() - t0) * 1000)
        if log:
            log.record(agent_name, model, prompt, None, latency, str(e))
        return None, str(e)


def _gemini_image(prompt: str, model: str, *, log: Optional[AgentLog] = None) -> tuple[Optional[bytes], Optional[str]]:
    """Generate an image with Gemini. Returns (png_bytes, error_or_None)."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        if log:
            log.record("renderer", model, prompt, None, 0, "no_api_key")
        return None, "no_api_key"
    try:
        from google import genai  # type: ignore
    except ImportError:
        if log:
            log.record("renderer", model, prompt, None, 0, "google-genai not installed")
        return None, "google-genai not installed"
    t0 = time.time()
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model=model, contents=prompt)
        for part in (resp.candidates or [None])[0].content.parts if resp.candidates else []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                data = inline.data
                if isinstance(data, str):
                    data = base64.b64decode(data)
                latency = int((time.time() - t0) * 1000)
                if log:
                    log.record("renderer", model, prompt, f"<image:{len(data)} bytes>", latency)
                return data, None
        latency = int((time.time() - t0) * 1000)
        if log:
            log.record("renderer", model, prompt, None, latency, "no inline image in response")
        return None, "no inline image in response"
    except Exception as e:  # pragma: no cover
        latency = int((time.time() - t0) * 1000)
        if log:
            log.record("renderer", model, prompt, None, latency, str(e))
        return None, str(e)


# ---------------------------------------------------------------------------
# Planner agent
# ---------------------------------------------------------------------------

BLUEPRINT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "layout": {"type": "string", "enum": ["linear", "parallel_branches", "encoder_decoder", "graph"]},
        "blocks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "role": {"type": "string", "enum": ["input", "frozen", "learnable", "fusion", "output", "loss", "regularizer"]},
                    "row": {"type": "integer"},
                    "col": {"type": "integer"},
                    "shape": {"type": "string", "enum": ["rect", "diamond", "circle", "rounded"]},
                    "annotation": {"type": "string"},
                    "equation": {"type": "string"},
                    "param_count": {"type": "string"},
                },
                "required": ["id", "label", "role", "row", "col"],
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "label": {"type": "string"},
                    "style": {"type": "string", "enum": ["solid", "dashed", "bold"]},
                    "bend_deg": {"type": "number"},
                },
                "required": ["from", "to"],
            },
        },
        "legend": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"role": {"type": "string"}, "description": {"type": "string"}},
                "required": ["role", "description"],
            },
        },
        "caption": {"type": "string"},
    },
    "required": ["title", "layout", "blocks", "edges", "caption"],
}


def _planner_prompt(spec: dict[str, Any], analysis: dict[str, Any], shared: dict[str, Any]) -> str:
    novelty_claims = spec.get("narrative", "")
    modules = analysis.get("model", {}).get("modules", [])
    return f"""You are a senior research illustrator preparing a venue-quality architecture diagram
for a top-tier ML paper. Your job is NOT to draw — your job is to produce a precise structured
BLUEPRINT (JSON) that a downstream renderer will turn into Typst CeTZ/fletcher code.

The figure must be a SCIENTIFIC COMMUNICATION OBJECT — not a generic flowchart. Decisions to make:
- Which modules to show (frozen pretrained vs. learnable adapter vs. fusion vs. loss/regularizer vs. output head)
- Spatial layout that conveys data flow direction at a glance
- Which equations to pin to which block (NEVER floating)
- Parameter-count annotations on learnable blocks (defends reviewer attacks)
- Arrow labels (≤3 words each) that disambiguate parallel paths
- Color roles from the venue palette {VENUE_PALETTES.get(spec.get('venue', 'neurips'), [])}

Figure intent: {spec.get('intent', '')}
Narrative claim it must support: {novelty_claims}
Reviewer targets to address visually: {spec.get('reviewer_targets', [])}
Equations to anchor: {json.dumps(spec.get('equations', []))}
Model modules detected in the codebase: {json.dumps(modules)[:2000]}
Cross-figure shared color/name decisions (must respect these): {json.dumps(shared)}

Output a JSON BLUEPRINT matching this schema (fields: title, layout, blocks[id,label,role,row,col,shape,annotation?,equation?,param_count?],
edges[from,to,label?,style?,bend_deg?], legend, caption).

Rules:
- "frozen" blocks are pretrained encoders (gray tints)
- "learnable" blocks are trainable adapters (warm tints, MUST include param_count)
- "fusion" blocks combine multiple paths (diamond shape, accent color)
- "loss" blocks attach to outputs (red tint)
- For every equation in `equations`, place it in the `equation` field of the block whose id matches its anchor_in_diagram
- Edges should show data flow direction; parallel branches use the same row, sequential stages use the same column
- Caption should be 2-3 sentences, self-contained for readers who skim
- Use the EXACT block ids referenced in the input equations' anchor_in_diagram"""


def _planner_fallback(spec: dict[str, Any], analysis: dict[str, Any], shared: dict[str, Any]) -> dict[str, Any]:
    """Rule-based fallback blueprint when Gemini is unavailable."""
    modules = analysis.get("model", {}).get("modules", [])
    module_names = shared.get("module_names") or [m.get("name", f"M{i}") for i, m in enumerate(modules)]
    if not module_names:
        module_names = ["Image Encoder", "Text Encoder", "Representation Learner", "Weighted Fusion", "Classifier"]

    blocks = []
    edges = []
    fusion_blocks: list[str] = []
    other_blocks: list[str] = []
    for name in module_names:
        n = name.lower()
        if "fusion" in n or "weighted" in n:
            fusion_blocks.append(name)
        else:
            other_blocks.append(name)

    def role_of(name: str) -> str:
        n = name.lower()
        if "fusion" in n or "weighted" in n:
            return "fusion"
        if "image" in n or "text" in n or "input" in n:
            return "input"
        if "frozen" in n:
            return "frozen"
        if "head" in n or "classifier" in n or "output" in n:
            return "output"
        if "loss" in n:
            return "loss"
        return "learnable"

    eq_for_block = {e.get("anchor_in_diagram", "").lower(): e for e in spec.get("equations", []) or []}

    for i, name in enumerate(other_blocks):
        col = i // 2
        row = i % 2
        bid = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        role = role_of(name)
        eq = eq_for_block.get(bid) or eq_for_block.get(name.lower())
        blocks.append({
            "id": bid,
            "label": name,
            "role": role,
            "row": row,
            "col": col,
            "shape": "rect",
            "annotation": "frozen" if role == "frozen" else ("~5M params" if role == "learnable" else ""),
            "equation": eq["tex"] if eq else "",
        })
    fx = max((b["col"] for b in blocks), default=0) + 1
    for j, name in enumerate(fusion_blocks):
        bid = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        eq = eq_for_block.get(bid) or eq_for_block.get(name.lower())
        blocks.append({
            "id": bid,
            "label": name,
            "role": "fusion",
            "row": j,
            "col": fx,
            "shape": "diamond",
            "annotation": "",
            "equation": eq["tex"] if eq else "",
        })
        for src in other_blocks:
            sid = re.sub(r"[^a-z0-9]+", "_", src.lower()).strip("_")
            edges.append({"from": sid, "to": bid, "label": "", "style": "solid"})

    return {
        "title": spec.get("intent", "Architecture"),
        "layout": "parallel_branches" if fusion_blocks else "linear",
        "blocks": blocks,
        "edges": edges,
        "legend": [
            {"role": "frozen", "description": "Pretrained, non-trainable"},
            {"role": "learnable", "description": "Trainable adapter"},
            {"role": "fusion", "description": "Multi-path combination"},
        ],
        "caption": spec.get("narrative", "Architecture overview."),
    }


def plan(spec: dict[str, Any], analysis: dict[str, Any], shared: dict[str, Any], log: AgentLog) -> dict[str, Any]:
    prompt = _planner_prompt(spec, analysis, shared)
    blueprint, err = _gemini_text(prompt, PLANNER_MODEL, response_schema=BLUEPRINT_SCHEMA, log=log, agent_name="planner")
    if blueprint and isinstance(blueprint, dict) and blueprint.get("blocks"):
        return blueprint
    print(f"[planner] using fallback (reason: {err or 'invalid response'})", file=sys.stderr)
    return _planner_fallback(spec, analysis, shared)


# ---------------------------------------------------------------------------
# CeTZ/fletcher renderer (deterministic, always available)
# ---------------------------------------------------------------------------

def render_cetz(blueprint: dict[str, Any], fig_id: str, venue: str = "neurips") -> str:
    palette = VENUE_PALETTES.get(venue, VENUE_PALETTES["neurips"])
    blocks = blueprint.get("blocks", [])
    edges = blueprint.get("edges", [])
    caption = blueprint.get("caption", "Architecture overview.")

    def safe(s: str) -> str:
        return s.replace('"', "'").replace("\\", "/")

    node_lines: list[str] = []
    for b in blocks:
        fill = SEMANTIC_TINTS.get(b.get("role", "learnable"), "#FFFFFF")
        label_parts = [f"*{safe(b['label'])}*"]
        if b.get("annotation"):
            label_parts.append(f"_{safe(b['annotation'])}_")
        if b.get("equation"):
            label_parts.append(f"${b['equation']}$")
        if b.get("param_count"):
            label_parts.append(f"_{safe(b['param_count'])}_")
        body = "\\ ".join(label_parts)
        shape = b.get("shape", "rect")
        x = float(b.get("col", 0))
        y = float(b.get("row", 0))
        node_lines.append(
            f'  node(({x:.1f}, {y:.1f}), [{body}], shape: fletcher.shapes.{shape}, '
            f'fill: rgb("{fill}"), stroke: 0.6pt, name: <{b["id"]}>),'
        )

    edge_lines: list[str] = []
    for e in edges:
        label = safe(e.get("label", ""))
        bend = e.get("bend_deg", 0)
        style_attr = ""
        if e.get("style") == "dashed":
            style_attr = ", stroke: (paint: black, thickness: 0.6pt, dash: \"dashed\")"
        elif e.get("style") == "bold":
            style_attr = ", stroke: 1.2pt"
        bend_attr = f", bend: {bend}deg" if bend else ""
        label_attr = f', label: [{label}]' if label else ""
        edge_lines.append(f'  edge(<{e["from"]}>, <{e["to"]}>, "->"{label_attr}{bend_attr}{style_attr}),')

    legend_block = ""
    if blueprint.get("legend"):
        legend_items = " ".join(
            f'box(fill: rgb("{SEMANTIC_TINTS.get(item["role"], "#FFFFFF")}"), width: 8pt, height: 8pt) #h(0.3em) #text(7pt)[{safe(item["description"])}] #h(0.8em)'
            for item in blueprint["legend"]
        )
        legend_block = f"\n#align(center)[#text(size: 7pt)[#stack(dir: ltr, spacing: 0.6em, {legend_items})]]\n"

    body_text = "\n".join(node_lines + edge_lines)
    return (
        '#import "@preview/fletcher:0.5.1" as fletcher: node, edge\n\n'
        f"#figure(\n"
        f"  fletcher.diagram(\n"
        f"    node-stroke: 0.6pt,\n"
        f"    spacing: (14mm, 11mm),\n"
        f"{body_text}\n"
        f"  ),\n"
        f"  caption: [{safe(caption)}],\n"
        f") <{fig_id.replace(':', '_')}>\n"
        f"{legend_block}"
    )


# ---------------------------------------------------------------------------
# Image renderer (Gemini image preview)
# ---------------------------------------------------------------------------

def _renderer_prompt(blueprint: dict[str, Any], venue: str) -> str:
    return f"""Generate a clean, publication-quality architecture diagram suitable for a {venue.upper()} paper figure.

Style requirements:
- Vector-clean appearance, minimalist, white background
- Black or dark-gray strokes (~0.8pt)
- Block fills follow these semantic role tints:
  input=#E0E0E0, frozen=#CFD8DC, learnable=#FFE0B2, fusion=#BBDEFB, loss=#FFCDD2, output=#C8E6C9
- Block labels in serif font (Times-equivalent), 10pt
- Equations rendered in LaTeX-style math, placed INSIDE the block they describe
- Parameter-count annotations directly under learnable blocks (e.g. "~5M params")
- Arrows show data flow direction with small text labels (≤3 words)
- No decorative shadows, no gradients, no 3D effects
- Aspect ratio ~ 16:9, target width 5.5 inches at 300dpi

Blueprint to render:
{json.dumps(blueprint, indent=2)[:6000]}

Produce a single PNG image of the diagram only — no surrounding caption text, no title bar."""


def render_image(blueprint: dict[str, Any], venue: str, log: AgentLog) -> tuple[Optional[bytes], Optional[str]]:
    prompt = _renderer_prompt(blueprint, venue)
    return _gemini_image(prompt, RENDERER_IMAGE_MODEL, log=log)


# ---------------------------------------------------------------------------
# Critic agent
# ---------------------------------------------------------------------------

CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "passes": {
            "type": "object",
            "properties": {
                "legibility": {"type": "object", "properties": {"status": {"type": "string"}, "issues": {"type": "array", "items": {"type": "string"}}}},
                "formulas":   {"type": "object", "properties": {"status": {"type": "string"}, "issues": {"type": "array", "items": {"type": "string"}}}},
                "palette":    {"type": "object", "properties": {"status": {"type": "string"}, "issues": {"type": "array", "items": {"type": "string"}}}},
                "narrative":  {"type": "object", "properties": {"status": {"type": "string"}, "issues": {"type": "array", "items": {"type": "string"}}}},
                "venue":      {"type": "object", "properties": {"status": {"type": "string"}, "issues": {"type": "array", "items": {"type": "string"}}}},
                "reviewer_targets": {"type": "object", "properties": {"status": {"type": "string"}, "issues": {"type": "array", "items": {"type": "string"}}}},
            },
        },
        "overall": {"type": "string", "enum": ["ok", "warn", "fail"]},
        "actionable_items": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["passes", "overall", "actionable_items"],
}


def critique(blueprint: dict[str, Any], typ_code: str, spec: dict[str, Any], log: AgentLog) -> dict[str, Any]:
    prompt = f"""You are a strict reviewer assessing a generated architecture figure for a top-tier ML venue.

Score the figure on six independent passes:
1. legibility (label sizes, no overlaps, no truncation)
2. formulas (every spec equation present, anchored to the correct block, parseable)
3. palette (colors are from the venue palette, monochrome-safe contrast)
4. narrative alignment (does it visually support the narrative claim?)
5. venue grammar (caption length, arrow conventions, no logos/identifying marks if double-blind)
6. reviewer_targets coverage (are the spec's reviewer_targets visually addressed?)

For each pass return status in {{"ok", "warn", "fail"}} and a list of concrete issues.
Then aggregate to overall and produce a short list of actionable_items.

Spec:
{json.dumps(spec, indent=2)[:2000]}

Blueprint:
{json.dumps(blueprint, indent=2)[:3000]}

Generated Typst CeTZ code:
{typ_code[:3000]}
"""
    res, err = _gemini_text(prompt, CRITIC_MODEL, response_schema=CRITIQUE_SCHEMA, log=log, agent_name="critic")
    if res:
        return res
    # Heuristic fallback critic
    issues_formulas = []
    spec_eqs = spec.get("equations", []) or []
    for eq in spec_eqs:
        anchor = eq.get("anchor_in_diagram", "")
        if anchor and anchor not in typ_code:
            issues_formulas.append(f"equation anchored to {anchor} not found in render")
    return {
        "passes": {
            "legibility": {"status": "ok", "issues": []},
            "formulas":   {"status": "fail" if issues_formulas else "ok", "issues": issues_formulas},
            "palette":    {"status": "ok", "issues": []},
            "narrative":  {"status": "ok", "issues": []},
            "venue":      {"status": "ok", "issues": []},
            "reviewer_targets": {"status": "ok", "issues": []},
        },
        "overall": "fail" if issues_formulas else "ok",
        "actionable_items": [f"add equation block for {i}" for i in issues_formulas],
        "_fallback": True,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def orchestrate(spec: dict[str, Any], shared: dict[str, Any], analysis: dict[str, Any], out_typ: Path, out_png: Optional[Path], venue: str, max_refines: int = 3) -> dict[str, Any]:
    fig_id = spec["fig_id"]
    log = AgentLog(fig_id=fig_id, log_path=out_typ.parent / f"{fig_id.replace(':', '_')}.agent_log.jsonl")
    print(f"[viz_arch] orchestrating fig_id={fig_id}, model={PLANNER_MODEL}/{RENDERER_IMAGE_MODEL}", file=sys.stderr)

    blueprint = plan(spec, analysis, shared, log)
    blueprint_path = out_typ.parent / f"{fig_id.replace(':', '_')}.blueprint.json"
    blueprint_path.parent.mkdir(parents=True, exist_ok=True)
    blueprint_path.write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
    print(f"[planner] wrote {blueprint_path}", file=sys.stderr)

    last_critique: dict[str, Any] = {}
    typ_code = ""
    for it in range(max_refines):
        typ_code = render_cetz(blueprint, fig_id, venue)
        out_typ.write_text(typ_code, encoding="utf-8")
        print(f"[renderer] wrote {out_typ} (iteration {it+1})", file=sys.stderr)

        if out_png:
            png_bytes, img_err = render_image(blueprint, venue, log)
            if png_bytes:
                # Detect true format from magic bytes; Gemini may return JPEG
                # despite a `.png` filename.
                if png_bytes[:3] == b"\xff\xd8\xff":
                    out_png = out_png.with_suffix(".jpg")
                elif png_bytes[:4] == b"GIF8":
                    out_png = out_png.with_suffix(".gif")
                elif png_bytes[:8] != b"\x89PNG\r\n\x1a\n" and out_png.suffix.lower() == ".png":
                    out_png = out_png.with_suffix(".bin")
                out_png.parent.mkdir(parents=True, exist_ok=True)
                out_png.write_bytes(png_bytes)
                print(f"[renderer] wrote {out_png} via {RENDERER_IMAGE_MODEL}", file=sys.stderr)
            else:
                print(f"[renderer] image generation skipped: {img_err}", file=sys.stderr)

        last_critique = critique(blueprint, typ_code, spec, log)
        crit_path = out_typ.parent / f"{fig_id.replace(':', '_')}.critique.json"
        crit_path.write_text(json.dumps(last_critique, indent=2), encoding="utf-8")
        overall = last_critique.get("overall", "ok")
        print(f"[critic] iteration {it+1} overall={overall}", file=sys.stderr)
        if overall in ("ok", "warn"):
            break

        # Refine blueprint with actionable items by re-asking the planner
        actionables = last_critique.get("actionable_items", []) or []
        if not actionables:
            break
        refine_prompt = _planner_prompt(spec, analysis, shared) + "\n\nPREVIOUS BLUEPRINT WAS REJECTED. Address these actionable items in the new blueprint:\n- " + "\n- ".join(actionables) + "\n\nReturn ONLY a corrected JSON blueprint."
        refined, err = _gemini_text(refine_prompt, PLANNER_MODEL, response_schema=BLUEPRINT_SCHEMA, log=log, agent_name="planner_refine")
        if refined and isinstance(refined, dict) and refined.get("blocks"):
            blueprint = refined
        else:
            break

    return {
        "fig_id": fig_id,
        "blueprint_path": str(blueprint_path),
        "typ_path": str(out_typ),
        "png_path": str(out_png) if out_png else None,
        "critique": last_critique,
        "iterations": it + 1,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Multi-agent architecture diagram generator (planner + renderer + critic)")
    ap.add_argument("--spec", type=Path, required=True, help="Path to figures/_manifest.json")
    ap.add_argument("--fig-id", required=True)
    ap.add_argument("--analysis", type=Path, default=Path("paper/analysis.json"))
    ap.add_argument("--out", type=Path, required=True, help="Output Typst .typ file")
    ap.add_argument("--out-png", type=Path, default=None, help="Optional output PNG via gemini-3-pro-image-preview")
    ap.add_argument("--venue", default="neurips")
    ap.add_argument("--max-refines", type=int, default=3)
    args = ap.parse_args()

    manifest = json.loads(args.spec.read_text(encoding="utf-8"))
    shared = manifest.get("shared", {})
    spec = next((f for f in manifest.get("figures", []) if f.get("fig_id") == args.fig_id), None)
    if spec is None:
        raise SystemExit(f"figure {args.fig_id} not found in manifest")
    analysis: dict[str, Any] = {}
    if args.analysis.exists():
        analysis = json.loads(args.analysis.read_text(encoding="utf-8"))

    result = orchestrate(spec, shared, analysis, args.out, args.out_png, args.venue, args.max_refines)
    report = args.out.parent / f"{args.fig_id.replace(':', '_')}.render.json"
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[viz_arch] done. report -> {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
