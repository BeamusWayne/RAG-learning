# -*- coding: utf-8 -*-
"""MultiLevelRAG — 多层级 RAG 对比平台 (Streamlit)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st, time

st.set_page_config(
    page_title="MultiLevelRAG",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── tokens (light) ── */
:root {
  --bg:      #F4F6FA;
  --bg1:     #FFFFFF;
  --bg2:     #FFFFFF;
  --bg3:     #F1F5F9;
  --bg4:     #EFF6FF;
  --border:  #E2E8F0;
  --border2: #CBD5E1;
  --text:    #0F172A;
  --text2:   #475569;
  --text3:   #94A3B8;
  --cyan:    #2563EB;
  --cyan2:   #1D4ED8;
  --glow:    rgba(37,99,235,0.10);

  --c-baseline:#3B82F6; --c-hyde:#7C3AED;
  --c-fusion:  #0891B2; --c-crag:#D97706; --c-graph:#059669;
}

/* ── reset ── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
section.main,
.main .block-container {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
.block-container { padding: 1.25rem 1.5rem !important; max-width: 100% !important; }

/* ── sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
  background: var(--bg1) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 1px 0 8px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: var(--text) !important; }

/* ── inputs ── */
input, textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
div[class*="InputContainer"] input {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  border: 1px solid var(--border2) !important;
  border-radius: 7px !important;
  color: var(--text) !important;
  caret-color: var(--cyan) !important;
  font-family: 'Inter', sans-serif !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
input:focus, textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px var(--glow) !important;
  outline: none !important;
}
input::placeholder, textarea::placeholder { color: var(--text3) !important; }

/* ── selectbox / multiselect ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
div[data-baseweb="select"] > div,
div[data-baseweb="select"] div[role="combobox"] {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  border: 1px solid var(--border2) !important;
  border-radius: 7px !important;
  color: var(--text) !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
div[data-baseweb="popover"] div,
div[data-baseweb="menu"] div,
div[class*="menu"] { background: #FFFFFF !important; color: var(--text) !important; box-shadow: 0 4px 16px rgba(0,0,0,0.10) !important; }
li[role="option"]:hover, div[aria-selected="true"] { background: var(--bg4) !important; color: var(--cyan) !important; }

/* ── file uploader ── */
[data-testid="stFileUploader"],
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzoneInstructions"] {
  background: #FFFFFF !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 8px !important;
  color: var(--text2) !important;
}
[data-testid="stFileUploaderDropzone"] svg { stroke: var(--cyan) !important; }
[data-testid="stFileUploaderDropzone"] button {
  background: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--cyan) !important; border-radius: 6px !important;
}

/* ── radio (fallback, strip ugly blue block) ── */
[data-testid="stRadio"] div[role="radiogroup"] label { color: var(--text) !important; }
[data-testid="stRadio"] div[role="radiogroup"] > div { background: transparent !important; }
[data-testid="stRadio"] label[data-checked="true"],
[data-testid="stRadio"] label[aria-checked="true"] { background: transparent !important; }

/* ── segmented control (Mode toggle) ── */
[data-testid="stSegmentedControl"] {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 3px !important;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.06) !important;
}
[data-testid="stSegmentedControl"] button {
  border-radius: 8px !important;
  font-size: 12px !important;
  font-family: 'Fira Code', monospace !important;
  color: var(--text2) !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 5px 14px !important;
  transition: all 0.15s ease !important;
  transform: none !important;
}
[data-testid="stSegmentedControl"] button:hover {
  color: var(--cyan) !important;
  background: rgba(37,99,235,0.06) !important;
  transform: none !important;
  box-shadow: none !important;
}
[data-testid="stSegmentedControl"] button[aria-checked="true"] {
  background: #FFFFFF !important;
  color: var(--cyan) !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.10) !important;
  transform: none !important;
}

/* ── checkbox ── */
[data-testid="stCheckbox"] label { color: var(--text) !important; }

/* ── expander ── */
[data-testid="stExpander"] {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
[data-testid="stExpander"] summary { background: #FFFFFF !important; color: var(--text2) !important; }
[data-testid="stExpander"] summary:hover { color: var(--cyan) !important; }
[data-testid="stExpander"] summary svg { color: var(--text2) !important; }
[data-testid="stExpander"] > div > div { background: #FFFFFF !important; }

/* ── buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 8px !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 12px !important; letter-spacing: 0.4px !important;
  font-weight: 500 !important;
  transition: all 0.18s ease !important;
  box-shadow: 0 1px 4px rgba(37,99,235,0.25) !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
  box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active { transform: scale(0.98) translateY(0) !important; }

/* ── tabs ── */
[data-testid="stTabs"] { background: transparent !important; }
[data-testid="stTabs"] > div:first-child { border-bottom: 2px solid var(--border) !important; gap: 0 !important; }
[data-testid="stTabs"] button[role="tab"] {
  background: transparent !important; border: none !important;
  color: var(--text2) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 12px !important; letter-spacing: 0.5px !important;
  padding: 8px 18px !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -2px !important;
  transition: color 0.15s !important;
}
[data-testid="stTabs"] button[role="tab"]:hover { color: var(--cyan) !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom-color: var(--cyan) !important;
  font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tabpanel"] { background: transparent !important; padding-top: 16px !important; }

/* ── alerts ── */
[data-testid="stSuccess"] { background: #F0FDF4 !important; border-color: #16A34A !important; color: #15803D !important; }
[data-testid="stError"]   { background: #FEF2F2 !important; border-color: #DC2626 !important; color: #B91C1C !important; }
[data-testid="stInfo"]    { background: #EFF6FF !important; border-color: var(--cyan) !important; color: var(--cyan) !important; }

/* ── markdown ── */
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li,
[data-testid="stMarkdown"] h1,
[data-testid="stMarkdown"] h2,
[data-testid="stMarkdown"] h3 { color: var(--text) !important; }
[data-testid="stMarkdown"] code {
  background: #EFF6FF !important; color: var(--cyan) !important;
  border-radius: 4px !important; padding: 1px 5px !important;
}

/* ── scrollbars ── */
* { scrollbar-width: thin; scrollbar-color: var(--border2) transparent; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── hide chrome ── */
#MainMenu, footer, header,
[data-testid="stDecoration"] { display: none !important; }

/* ═══════════════ CUSTOM COMPONENTS ═══════════════ */

/* Header */
.mlr-header {
  background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 55%, #1E40AF 100%);
  border-radius: 10px; padding: 22px 30px 20px;
  margin-bottom: 20px; position: relative; overflow: hidden;
  box-shadow: 0 4px 20px rgba(37,99,235,0.25);
}
.mlr-header::before {
  content: '';
  position: absolute; top: 0; right: 0; width: 240px; height: 100%;
  background: linear-gradient(135deg, transparent, rgba(255,255,255,0.07));
  pointer-events: none;
}
.mlr-title {
  font-family: 'Fira Code', monospace;
  font-size: 22px; font-weight: 700; letter-spacing: -0.3px;
  color: #FFFFFF; margin: 0 0 4px;
  text-shadow: 0 1px 8px rgba(0,0,0,0.2);
}
.mlr-sub {
  font-size: 12px; color: rgba(255,255,255,0.6);
  font-family: 'Fira Code', monospace; letter-spacing: 0.2px;
}

/* Section heading */
.sec-hd {
  font-family: 'Fira Code', monospace;
  font-size: 10px; font-weight: 600; letter-spacing: 2px;
  color: var(--cyan); text-transform: uppercase;
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
}
.sec-hd::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border2), transparent);
}

/* Badges */
.badge {
  display: inline-flex; align-items: center;
  padding: 2px 9px; border-radius: 20px;
  font-family: 'Fira Code', monospace;
  font-size: 10px; font-weight: 600; letter-spacing: 0.4px;
  border: 1px solid;
}
.b-baseline{background:#EFF6FF;color:#2563EB;border-color:#BFDBFE}
.b-hyde    {background:#F5F3FF;color:#6D28D9;border-color:#DDD6FE}
.b-fusion  {background:#ECFEFF;color:#0E7490;border-color:#A5F3FC}
.b-crag    {background:#FFFBEB;color:#B45309;border-color:#FDE68A}
.b-graph   {background:#F0FDF4;color:#047857;border-color:#A7F3D0}
.b-auto    {background:#EFF6FF;color:#2563EB;border-color:#BFDBFE}

/* Question bubble */
.qa-question {
  background: linear-gradient(135deg, #EFF6FF 0%, #F0F9FF 100%);
  border: 1px solid #BFDBFE;
  border-radius: 10px 10px 4px 10px;
  padding: 14px 18px; margin-bottom: 16px;
  font-size: 15px; color: var(--text);
  line-height: 1.6;
  box-shadow: 0 1px 4px rgba(37,99,235,0.08);
}
.qa-meta {
  font-family: 'Fira Code', monospace;
  font-size: 10px; color: var(--text3);
  margin-top: 6px; display: flex; gap: 10px; align-items: center;
}

/* Answer card */
.ans-card {
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: 4px 10px 10px 10px;
  padding: 16px 20px 14px; margin-bottom: 6px;
  transition: border-color .2s, box-shadow .2s;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.ans-card:hover { border-color: #BFDBFE; box-shadow: 0 4px 14px rgba(37,99,235,0.10); }
.ans-hd {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 12px;
  flex-wrap: wrap; gap: 6px;
}
.ans-body {
  font-size: 14px; line-height: 1.85;
  color: var(--text); white-space: pre-wrap;
}

/* Timeline */
.timeline {
  display: flex; align-items: center;
  flex-wrap: wrap; gap: 0; margin-top: 14px;
  overflow-x: auto; padding-bottom: 2px;
}
.tl-step {
  display: flex; align-items: center;
  font-family: 'Fira Code', monospace;
  font-size: 10px; color: var(--text3);
}
.tl-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--cyan); flex-shrink: 0;
  box-shadow: 0 0 4px rgba(37,99,235,0.4);
}
.tl-label {
  background: #F8FAFC; border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 8px;
  margin: 0 4px; white-space: nowrap; color: var(--text2);
}
.tl-arrow { color: var(--text3); font-size: 10px; margin: 0 2px; }

/* Sources */
.src-list { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
.src-chip {
  font-family: 'Fira Code', monospace;
  font-size: 10px; padding: 2px 8px; border-radius: 4px;
  background: #EFF6FF; border: 1px solid #BFDBFE; color: #3B82F6;
}

/* Context box */
.ctx-box {
  background: #F8FAFC; border: 1px solid var(--border);
  border-radius: 6px; padding: 12px;
  font-family: 'Fira Code', monospace;
  font-size: 11px; line-height: 1.7; color: var(--text2);
  max-height: 180px; overflow-y: auto; white-space: pre-wrap;
  margin-top: 8px;
}

/* Elapsed pill */
.el-pill {
  font-family: 'Fira Code', monospace;
  font-size: 10px; padding: 2px 8px;
  border-radius: 10px;
  background: #F1F5F9; border: 1px solid var(--border2);
  color: var(--text3);
}

/* Action pills */
.act-correct  {background:#F0FDF4;color:#15803D;border:1px solid #86EFAC;padding:2px 8px;border-radius:10px;font-size:10px;font-family:'Fira Code',monospace}
.act-incorrect{background:#FEF2F2;color:#B91C1C;border:1px solid #FECACA;padding:2px 8px;border-radius:10px;font-size:10px;font-family:'Fira Code',monospace}
.act-ambiguous{background:#FFFBEB;color:#92400E;border:1px solid #FDE68A;padding:2px 8px;border-radius:10px;font-size:10px;font-family:'Fira Code',monospace}

/* Compare metric card */
.mc-box {
  background: #FFFFFF; border: 1px solid var(--border);
  border-radius: 8px; padding: 12px; text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.mc-val { font-family: 'Fira Code', monospace; font-size: 20px; font-weight: 700; color: var(--cyan); line-height: 1; }
.mc-unit { font-size: 11px; color: var(--text3); }
.mc-lbl  { font-size: 9px; color: var(--text3); letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }

/* Status dot */
.sdot { width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:5px;vertical-align:middle; }
.sdot-ok  {background:#16A34A;box-shadow:0 0 5px rgba(22,163,74,.4)}
.sdot-err {background:#DC2626;box-shadow:0 0 5px rgba(220,38,38,.4)}
.sdot-idle{background:#CBD5E1}

/* Divider */
.vdiv { height:1px;background:var(--border);margin:14px 0; }

/* KB bar */
.kb-bar {
  display:flex;align-items:center;gap:8px;
  background:#F8FAFC;border:1px solid var(--border);
  border-radius:6px;padding:6px 12px;margin-top:8px;
  font-size:11px;color:var(--text2);
  font-family:'Fira Code',monospace;
}

/* ── Chat form card (real DOM container via st.form) ── */
[data-testid="stForm"] {
  border: 1.5px solid #CBD5E1 !important;
  border-radius: 16px !important;
  padding: 14px 16px 10px !important;
  background: #FFFFFF !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
  margin-top: 10px !important;
}
[data-testid="stForm"]:focus-within {
  border-color: #2563EB !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.09) !important;
}
[data-testid="stForm"] textarea {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  font-size: 15px !important;
  line-height: 1.55 !important;
  resize: none !important;
  color: var(--text) !important;
}
[data-testid="stForm"] textarea:focus {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}
/* 发送 button — outlined, NOT filled */
[data-testid="stFormSubmitButton"] > button {
  background: transparent !important;
  border: 1.5px solid #2563EB !important;
  color: #2563EB !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
  box-shadow: none !important;
  transform: none !important;
  padding: 6px 18px !important;
  transition: all .15s ease !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  background: #EFF6FF !important;
  border-color: #1D4ED8 !important;
  color: #1D4ED8 !important;
  transform: none !important;
  box-shadow: 0 2px 6px rgba(37,99,235,0.15) !important;
}
[data-testid="stFormSubmitButton"] > button:active {
  background: #DBEAFE !important;
  transform: scale(0.98) !important;
  box-shadow: none !important;
}

/* ── st.pills (global — no dead parent selector) ── */
[data-testid="stPills"] button {
  font-size: 11px !important;
  padding: 3px 11px !important;
  border-radius: 12px !important;
  background: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text2) !important;
  box-shadow: none !important;
  transform: none !important;
  font-family: 'Fira Code', monospace !important;
  font-weight: 500 !important;
  transition: all .15s ease !important;
}
[data-testid="stPills"] button:hover {
  background: var(--bg4) !important;
  border-color: var(--cyan) !important;
  color: var(--cyan) !important;
  transform: none !important;
}
[data-testid="stPills"] button[aria-checked="true"] {
  background: #EFF6FF !important;
  border-color: #2563EB !important;
  color: #2563EB !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 4px rgba(37,99,235,0.15) !important;
}

/* ── source chips (max-width + ellipsis) ── */
.src-chip {
  max-width: 160px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

/* ── clear / secondary button ── */
.clear-btn .stButton > button {
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--text2) !important;
  font-size: 11px !important;
  box-shadow: none !important;
  transform: none !important;
}
.clear-btn .stButton > button:hover {
  background: var(--bg3) !important;
  transform: none !important;
  box-shadow: none !important;
}
</style>""", unsafe_allow_html=True)


# ── helpers ──────────────────────────────────────────────────────────────────
SMETA = {
    "baseline": ("Baseline RAG", "b-baseline"),
    "hyde":     ("HyDE RAG",     "b-hyde"),
    "fusion":   ("RAG Fusion",   "b-fusion"),
    "crag":     ("CRAG",         "b-crag"),
    "graph":    ("GraphRAG",     "b-graph"),
    "auto":     ("Auto",         "b-auto"),
}

def badge(name: str) -> str:
    lbl, cls = SMETA.get(name, (name, "b-auto"))
    return f'<span class="badge {cls}">{lbl}</span>'


def timeline_html(steps: list[str]) -> str:
    if not steps:
        return ""
    parts = ['<div class="timeline">']
    for i, s in enumerate(steps):
        if i:
            parts.append('<span class="tl-arrow">›</span>')
        parts.append(f'<span class="tl-step"><span class="tl-dot"></span><span class="tl-label">{s}</span></span>')
    parts.append('</div>')
    return "".join(parts)


def render_answer(result: dict):
    import html as _h
    import os.path as _op

    name     = result.get("strategy", "?")
    elapsed  = result.get("elapsed_ms", 0)
    answer   = str(result.get("answer", ""))
    steps    = result.get("steps", [])
    sources  = result.get("sources", [])
    ctx      = result.get("context_used", "")
    action   = result.get("action", "")
    sub_q    = result.get("sub_queries", [])
    entities = result.get("entities", [])
    hypo     = result.get("hypothetical_doc", "")
    gn       = result.get("graph_node_count", 0)
    lbl, cls = SMETA.get(name, (name, "b-auto"))

    act_html = f'<span class="act-{action}">{action.upper()}</span>' if action else ""

    extra_info = ""
    if sub_q:
        qs = "  ·  ".join(_h.escape(q) for q in sub_q[:3])
        extra_info += f'<div style="font-size:10px;color:var(--text3);margin-top:6px;font-family:Fira Code,monospace">↳ 子查询: {qs}</div>'
    if entities:
        ent = "".join(f'<span class="src-chip">{_h.escape(str(e))}</span>' for e in entities[:5])
        extra_info += f'<div class="src-list" style="margin-top:6px">{ent}</div>'
    if gn:
        extra_info += f'<div style="font-size:10px;color:var(--text3);margin-top:4px;font-family:Fira Code,monospace">图谱节点: {gn}</div>'
    if sources:
        chips = "".join(
            f'<span class="src-chip" title="{_h.escape(s.get("source","?"))}">'
            f'{_h.escape(_op.basename(s.get("source","?")))}</span>'
            for s in sources[:5]
        )
        extra_info += f'<div class="src-list">{chips}</div>'

    # Header + timeline + meta as HTML; answer body via st.markdown for safe rendering
    st.markdown(f"""
<div class="ans-card">
  <div class="ans-hd">
    <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
      <span class="badge {cls}">{lbl}</span>
      {act_html}
    </div>
    <span class="el-pill">{elapsed} ms</span>
  </div>""", unsafe_allow_html=True)

    st.markdown(answer)  # safe markdown rendering, no XSS risk

    if steps or extra_info:
        st.markdown(f"{timeline_html(steps)}{extra_info}", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("检索上下文", expanded=False):
        if hypo:
            st.markdown("**HyDE 假设文档**")
            st.markdown(f'<div class="ctx-box">{_h.escape(hypo[:600])}</div>', unsafe_allow_html=True)
        if ctx:
            st.markdown(f'<div class="ctx-box">{_h.escape(ctx[:1000])}</div>', unsafe_allow_html=True)


# ── sidebar ───────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div class="mlr-title" style="font-size:16px;margin-bottom:4px">◈ MultiLevelRAG</div>', unsafe_allow_html=True)
        st.markdown('<div class="mlr-sub">intent-aware routing · v1.0</div>', unsafe_allow_html=True)
        st.markdown('<div class="vdiv"></div>', unsafe_allow_html=True)

        # ── KB ──
        st.markdown('<div class="sec-hd">Knowledge Base</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "上传文档", type=["txt","pdf","md"],
            accept_multiple_files=True, label_visibility="collapsed",
        )
        if uploaded:
            if st.button("向量化 & 索引", use_container_width=True):
                with st.spinner("索引中..."):
                    try:
                        import tempfile
                        from knowledge_loader import load_file
                        from core.vector_store import add_documents
                        from strategies.graph_rag import index_documents
                        all_docs, total = [], 0
                        for uf in uploaded:
                            suf = "." + uf.name.rsplit(".",1)[-1]
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suf) as t:
                                t.write(uf.read()); tp = t.name
                            docs = load_file(tp)
                            for d in docs: d.metadata["source"] = uf.name
                            all_docs.extend(docs); total += add_documents(docs)
                            os.unlink(tp)
                        index_documents(all_docs)
                        st.success(f"✓ {total} chunks 已索引")
                        st.session_state.kb_ready = True
                    except Exception as e:
                        st.error(str(e))

        if st.button("示例知识库", use_container_width=True):
            with st.spinner("加载..."):
                try:
                    from knowledge_loader import load_directory, load_file
                    from strategies.graph_rag import index_documents
                    import config as cfg
                    n = load_directory()
                    all_docs = []
                    for f in os.listdir(cfg.DATA_DIR):
                        if f.endswith((".txt",".md",".pdf")):
                            all_docs.extend(load_file(os.path.join(cfg.DATA_DIR, f)))
                    index_documents(all_docs)
                    st.success(f"✓ {n} chunks，图谱已构建")
                    st.session_state.kb_ready = True
                except Exception as e:
                    st.error(str(e))

        # KB status
        try:
            from core.vector_store import collection_count
            cnt = collection_count()
            dot = "sdot-ok" if cnt > 0 else "sdot-idle"
            st.markdown(
                f'<div class="kb-bar"><span class="sdot {dot}"></span>{cnt} chunks in vector store</div>',
                unsafe_allow_html=True,
            )
        except Exception: pass

        st.markdown('<div class="vdiv"></div>', unsafe_allow_html=True)

        # ── Compare default strategy ──
        st.markdown('<div class="sec-hd">Compare Default</div>', unsafe_allow_html=True)
        strategy_pick = st.pills(
            "对比默认策略",
            options=["auto", "baseline", "hyde", "fusion", "crag", "graph"],
            format_func=lambda x: {
                "auto": "Auto", "baseline": "Baseline", "hyde": "HyDE",
                "fusion": "Fusion", "crag": "CRAG", "graph": "GraphRAG",
            }[x],
            selection_mode="single",
            default="auto",
            label_visibility="collapsed",
            key="sb_strategy",
        )
        strategy = strategy_pick or "auto"

        st.markdown('<div class="vdiv"></div>', unsafe_allow_html=True)

        # ── Mode ──
        st.markdown('<div class="sec-hd">Mode</div>', unsafe_allow_html=True)
        mode = st.segmented_control(
            "模式",
            options=["单策略问答", "全策略对比"],
            default="单策略问答",
            label_visibility="collapsed",
            key="sb_mode",
        ) or "单策略问答"

        st.markdown('<div class="vdiv"></div>', unsafe_allow_html=True)

        # ── Config (no API keys shown) ──
        st.markdown('<div class="sec-hd">Config</div>', unsafe_allow_html=True)
        with st.expander("运行时配置", expanded=False):
            import config as cfg
            provider = st.selectbox(
                "LLM Provider",
                ["openai","dashscope","ollama"],
                index=["openai","dashscope","ollama"].index(
                    os.environ.get("MULTI_RAG_LLM_PROVIDER", cfg.LLM_PROVIDER)),
            )
            os.environ["MULTI_RAG_LLM_PROVIDER"] = provider
            model = st.text_input("Model", value=os.environ.get("MULTI_RAG_LLM_MODEL", cfg.LLM_MODEL))
            if model: os.environ["MULTI_RAG_LLM_MODEL"] = model
            st.caption("API Key / Base URL 通过 .env 文件配置，不在此处显示。")

    return strategy, mode


# ── QA tab ────────────────────────────────────────────────────────────────────
def qa_tab(_strategy_ignored: str):
    # ── conversation history ──────────────────────────────────────────────────
    history = st.session_state.get("qa_history", [])

    if not history:
        st.markdown(
            '<div style="text-align:center;color:var(--text3);'
            'padding:60px 0 20px;font-size:14px;line-height:2.2">'
            '<div style="font-size:32px;margin-bottom:6px;opacity:.4">◈</div>'
            '向知识库提问，系统自动路由到最适合的 RAG 策略<br>'
            '<span style="font-size:12px">Baseline · HyDE · RAG Fusion · CRAG · GraphRAG</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for item in history:
            q, r = item["q"], item["r"]
            import html as _h
            routed = r.get("routed_strategy", r.get("strategy", "?"))
            st.markdown(
                f'<div class="qa-question">{_h.escape(q)}'
                f'<div class="qa-meta">'
                f'<span>路由 → {badge(routed)}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            render_answer(r)
            st.markdown('<div class="vdiv"></div>', unsafe_allow_html=True)

        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("清空对话", key="clear_hist"):
            st.session_state.qa_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── chat input form (real DOM card — CSS works here) ─────────────────────
    with st.form("qa_form", clear_on_submit=True, border=False):
        q_input = st.text_area(
            "q",
            placeholder="输入问题，系统自动路由到最适合的 RAG 策略…",
            height=80,
            label_visibility="collapsed",
            key="qa_input_text",
        )
        pill_col, send_col = st.columns([8, 2])
        with pill_col:
            strategy_pick = st.pills(
                "s",
                options=["auto", "baseline", "hyde", "fusion", "crag", "graph"],
                format_func=lambda x: SMETA.get(x, (x, ""))[0],
                selection_mode="single",
                default="auto",
                label_visibility="collapsed",
                key="qa_strategy_form",
            )
        with send_col:
            submitted = st.form_submit_button("发送", use_container_width=True)

    if submitted and q_input and q_input.strip():
        chosen_final = strategy_pick or "auto"
        with st.spinner("检索生成中…"):
            t0 = time.time()
            try:
                from router import dispatch
                r = dispatch(q_input.strip(), chosen_final)
                r["elapsed_ms"] = round((time.time() - t0) * 1000)
                if "qa_history" not in st.session_state:
                    st.session_state.qa_history = []
                st.session_state.qa_history.append({"q": q_input.strip(), "r": r})
                st.rerun()
            except Exception as e:
                st.error(str(e))


# ── Compare tab ───────────────────────────────────────────────────────────────
def compare_tab():
    st.markdown('<div class="sec-hd">全策略并发对比</div>', unsafe_allow_html=True)

    cq = st.text_input("对比问题", placeholder="输入问题，同时测试所有策略…",
                       label_visibility="collapsed", key="cmp_q")
    sel = st.multiselect("参与策略",
                         ["baseline","hyde","fusion","crag","graph"],
                         default=["baseline","crag","graph"],
                         label_visibility="collapsed")

    if st.button("▶ 并发执行", key="cmp_run") and cq.strip() and sel:
        with st.spinner(f"并发执行 {len(sel)} 个策略…"):
            try:
                from evaluation.comparator import compare_all
                results = compare_all(cq, sel)
                st.session_state.cmp = {"q": cq, "results": results}
            except Exception as e:
                st.error(str(e))

    if "cmp" not in st.session_state:
        return

    cdata = st.session_state.cmp
    results = cdata["results"]

    # Question bubble
    st.markdown(
        f'<div class="qa-question">{cdata["q"]}'
        f'<div class="qa-meta"><span>{len(results)} 个策略并发执行</span></div></div>',
        unsafe_allow_html=True,
    )

    # Metrics row
    cols = st.columns(len(results))
    for i, r in enumerate(results):
        nm = r.get("strategy","?")
        lbl, cls = SMETA.get(nm,(nm,"b-auto"))
        with cols[i]:
            st.markdown(
                f'<div class="mc-box">'
                f'<div class="mc-val">{r.get("elapsed_ms","?")}<span class="mc-unit">ms</span></div>'
                f'<div class="mc-lbl"><span class="badge {cls}" style="font-size:9px">{lbl}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="vdiv"></div>', unsafe_allow_html=True)

    # Cards (2 col grid)
    n = len(results)
    if n <= 2:
        cols2 = st.columns(n)
        for i, r in enumerate(results):
            with cols2[i]: render_answer(r)
    else:
        half = (n + 1) // 2
        col_a, col_b = st.columns(2)
        for i, r in enumerate(results):
            with (col_a if i < half else col_b):
                render_answer(r)


# ── About tab ──────────────────────────────────────────────────────────────────
def about_tab():
    st.markdown("""
<div style="max-width:840px;color:var(--text)">

## MultiLevelRAG 系统架构

意图感知的多层级 RAG 路由架构，集成 5 种检索增强策略。

### 架构图

```
用户问题
    │
    ▼
┌──────────────────────────────────────────┐
│           Intent Router                  │
│  (LLM 分类 → 路由到最佳策略)              │
└──────┬───────┬────────┬────────┬─────────┘
  Baseline  HyDE   Fusion   CRAG  GraphRAG
       └───────┴────────┴────────┴─────────┘
                    统一结果格式
                    Streamlit UI
```

### 策略对比

| 策略 | 核心机制 | 适用场景 | 复杂度 |
|------|---------|---------|--------|
| Baseline | 向量检索→生成 | 精确事实查询 | ★☆☆☆ |
| HyDE | 假设文档→检索 | 专业/语义扩展 | ★★☆☆ |
| Fusion | 多查询+RRF | 开放/模糊问题 | ★★☆☆ |
| CRAG | 评估→纠正→生成 | 不确定性高 | ★★★☆ |
| GraphRAG | 图谱+向量双路 | 多跳关系推理 | ★★★★ |

### 与业界最佳实践差距

| 能力 | 本项目 | 生产标准 |
|------|--------|---------|
| 检索 | 纯向量 | BM25 + 向量混合 |
| 重排序 | 无 | Cross-encoder |
| 图谱 | NetworkX | Neo4j / Amazon Neptune |
| 评估 | 耗时 | RAGAS (忠实度/相关性) |
| 流式 | 无 | SSE streaming |

### 快速开始

```bash
cd RAG-learning
# 配置见 Projects/MultiLevelRAG/.env
uv run streamlit run Projects/MultiLevelRAG/app.py
```
</div>
    """, unsafe_allow_html=True)


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    strategy, mode = sidebar()

    # Header
    st.markdown("""
<div class="mlr-header">
  <div class="mlr-title">◈ MultiLevelRAG Platform</div>
  <div class="mlr-sub">// intent-aware routing · baseline · hyde · fusion · crag · graphrag</div>
</div>""", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["问答", "策略对比", "系统说明"])
    with t1: qa_tab(strategy)
    with t2: compare_tab()
    with t3: about_tab()


if __name__ == "__main__":
    main()
