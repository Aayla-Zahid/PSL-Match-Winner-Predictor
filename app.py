"""PSL Match Winner Predictor: Streamlit app."""
import base64
import html as _html
from pathlib import Path

import streamlit as st

import predictor

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
AUTHOR = "Laiba Bintay Naeem"          # shown in the footer; change or set to "" to hide

st.set_page_config(page_title="PSL Match Predictor", page_icon="🏏", layout="wide")

# ----------------------------------------------------------------------------
# Team look (approximate team colours; short codes instead of logos)
# ----------------------------------------------------------------------------
TEAM_STYLE = {
    "Lahore Qalandars":   ("#22c55e", "LQ"),
    "Karachi Kings":      ("#3b82f6", "KK"),
    "Islamabad United":   ("#ef4444", "IU"),
    "Multan Sultans":     ("#2dd4bf", "MS"),
    "Peshawar Zalmi":     ("#facc15", "PZ"),
    "Quetta Gladiators":  ("#a855f7", "QG"),
    "Rawalpindiz":        ("#f97316", "RWP"),
    "Hyderabad Kingsmen": ("#ec4899", "HYD"),
}


def team_style(name: str):
    return TEAM_STYLE.get(name, ("#94a3b8", "".join(w[0] for w in name.split()[:3]).upper()))


def esc(text) -> str:
    return _html.escape(str(text))


def flat(markup: str) -> str:
    """Collapse indentation/newlines (keeping a space between lines) so Markdown never
    treats our HTML as a code block and words never get glued together."""
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())


# ----------------------------------------------------------------------------
# Background photo: looks for your image in the repo, falls back to a drawn SVG
# ----------------------------------------------------------------------------
@st.cache_data
def background_css_url() -> str:
    mimes = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
             ".webp": "image/webp", ".svg": "image/svg+xml"}
    candidates = [ROOT / "stadium_cricket.jpg", ASSETS / "stadium_cricket.jpg",
                  ASSETS / "background.jpg", ASSETS / "background.jpeg",
                  ASSETS / "background.png", ASSETS / "background.webp"]
    for folder in (ROOT, ASSETS):                       # any other photo you uploaded
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidates += sorted(folder.glob(f"*{ext}"))
    candidates.append(ASSETS / "stadium_batsman.svg")
    for path in candidates:
        if path.exists():
            b64 = base64.b64encode(path.read_bytes()).decode()
            return f"data:{mimes[path.suffix.lower()]};base64,{b64}"
    return ""


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Poppins', sans-serif; }

/* ---------- background: photo + dark gradient so the text stays readable ---------- */
.stApp {
    background-color: #050d0a;
    background-image:
        linear-gradient(90deg, rgba(4,10,8,.95) 0%, rgba(4,10,8,.88) 36%, rgba(4,10,8,.42) 62%, rgba(4,10,8,.04) 100%),
        linear-gradient(180deg, rgba(4,10,8,.55) 0%, rgba(4,10,8,0) 24%, rgba(4,10,8,.55) 100%),
        url("__BG__");
    background-size: cover; background-position: 75% center; background-attachment: fixed; background-repeat: no-repeat;
}
@media (max-width: 1099px) {
    .stApp {
        background-image: linear-gradient(180deg, rgba(4,10,8,.80), rgba(4,10,8,.88)), url("__BG__");
        background-position: 80% center;
    }
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 2.2rem 2rem 3rem 2rem; max-width: 1100px; }
@media (min-width: 1100px) {                      /* content on the left, batter visible on the right */
    .block-container { max-width: none; margin: 0; padding-left: 4.5vw; padding-right: 38vw; }
}

/* ---------- hero ---------- */
.eyebrow {
    display: inline-block; padding: .3rem .9rem; border-radius: 999px; font-size: .72rem; font-weight: 600;
    letter-spacing: .22em; text-transform: uppercase; color: #86efac;
    background: rgba(34,197,94,.12); border: 1px solid rgba(134,239,172,.3);
}
.hero { margin: 0 0 1.4rem 0; animation: fadeUp .7s ease both; }
.hero h1 {
    font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 6.5vw, 5.6rem);
    letter-spacing: .05em; margin: .6rem 0 0 0; line-height: .95; color: #fff;
    text-shadow: 0 4px 30px rgba(0,0,0,.6);
}
.hero h1 span {
    background: linear-gradient(90deg, #4ade80, #facc15);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: #d6ece1; margin: .7rem 0 0 0; font-size: 1.02rem; max-width: 34rem; }
.pills { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.1rem; }
.pill {
    background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); border-radius: 14px;
    padding: .45rem .9rem; backdrop-filter: blur(8px);
}
.pill .v { font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; color: #fff; letter-spacing: .05em; line-height: 1; }
.pill .k { font-size: .66rem; color: #9fc8b2; letter-spacing: .1em; text-transform: uppercase; }

/* ---------- panels ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(6, 20, 14, .66); border: 1px solid rgba(134,239,172,.2) !important; border-radius: 22px;
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); box-shadow: 0 14px 50px rgba(0,0,0,.4);
    padding: .5rem .7rem;
}
.glass {
    background: rgba(6, 20, 14, .66); border: 1px solid rgba(134,239,172,.2); border-radius: 22px; padding: 1.4rem;
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); box-shadow: 0 14px 50px rgba(0,0,0,.4);
    animation: fadeUp .7s ease both; margin-top: 1.2rem;
}
.step { display: flex; align-items: center; gap: .6rem; margin: .3rem 0 .5rem 0; }
.step .n {
    width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    background: #22c55e; color: #04140c; font-weight: 700; font-size: .8rem;
}
.step .t { font-family: 'Bebas Neue', sans-serif; letter-spacing: .14em; font-size: 1.3rem; color: #e8fff1; }

/* ---------- team chips ---------- */
.team-chip { display: flex; align-items: center; gap: .8rem; margin: .1rem 0 .4rem 0; }
.badge {
    width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex: none;
    font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; letter-spacing: .05em; color: #06130d;
    background: var(--c); box-shadow: 0 0 22px var(--c); border: 2px solid rgba(255,255,255,.55);
}
.badge.sm { width: 30px; height: 30px; font-size: .75rem; box-shadow: 0 0 10px var(--c); border-width: 1px; }
.team-chip .nm { font-weight: 700; font-size: 1.02rem; color: #fff; line-height: 1.1; }
.team-chip .sub { font-size: .76rem; color: #b7d8c6; }
.vs { display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 1.6rem;
      font-family: 'Bebas Neue', sans-serif; font-size: 2.2rem; color: #facc15; letter-spacing: .1em;
      text-shadow: 0 0 18px rgba(250,204,21,.6); }

/* ---------- widgets ---------- */
label, .stRadio label, .stSelectbox label, .stCheckbox label { color: #e6f6ed !important; font-weight: 500; }
[data-baseweb="select"] > div {
    background: rgba(255,255,255,.08) !important; border: 1px solid rgba(134,239,172,.3) !important;
    border-radius: 12px !important; color: #fff !important;
}
.stButton { width: 100%; }
.stButton > button {
    width: 100%; border: 0 !important; outline: none !important; border-radius: 14px; padding: .8rem 1rem;
    font-family: 'Bebas Neue', sans-serif; font-size: 1.6rem; letter-spacing: .16em; color: #04140c;
    background: linear-gradient(90deg, #22c55e, #facc15); box-shadow: 0 8px 28px rgba(34,197,94,.35);
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 34px rgba(250,204,21,.45); color: #04140c; }
.stButton > button:focus, .stButton > button:active { color: #04140c; box-shadow: 0 8px 28px rgba(34,197,94,.35); }

/* ---------- result ---------- */
.res-head { text-align: center; }
.res-head .lbl { color: #b7d8c6; letter-spacing: .25em; font-size: .75rem; text-transform: uppercase; }
.res-head .nm {
    font-family: 'Bebas Neue', sans-serif; font-size: clamp(2.4rem, 5vw, 3.8rem); letter-spacing: .06em;
    color: var(--c); text-shadow: 0 0 30px var(--c); line-height: 1.05;
}
.tag { display: inline-block; margin-top: .25rem; padding: .2rem .85rem; border-radius: 999px; font-size: .78rem;
       background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.22); color: #e6f6ed; }
.versus { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center; margin: 1.3rem 0 1rem 0; }
.tcard { text-align: center; padding: 1rem .6rem; border-radius: 18px; background: rgba(255,255,255,.05);
         border: 1px solid rgba(255,255,255,.1); opacity: .8; }
.tcard.win { opacity: 1; border-color: var(--c); box-shadow: 0 0 30px -6px var(--c), inset 0 0 24px -14px var(--c); }
.tcard .badge { margin: 0 auto .5rem auto; }
.tcard .tn { color: #fff; font-weight: 600; font-size: .95rem; }
.tcard .tp { font-family: 'Bebas Neue', sans-serif; font-size: 3.2rem; line-height: 1; color: var(--c); }
.tcard .te { color: #9fc8b2; font-size: .72rem; letter-spacing: .08em; }
.ring { width: 118px; height: 118px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 30px rgba(255,255,255,.08); animation: spin 1.1s cubic-bezier(.2,.8,.2,1) both; }
.ring-in { width: 84px; height: 84px; border-radius: 50%; background: #06140e; display: flex; align-items: center;
           justify-content: center; font-family: 'Bebas Neue', sans-serif; font-size: 1.6rem; color: #facc15; letter-spacing: .08em; }
.bar { display: flex; height: 12px; border-radius: 999px; overflow: hidden; background: rgba(255,255,255,.08); }
.bar > div { height: 100%; animation: grow 1s cubic-bezier(.2,.8,.2,1) both; }
.meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .7rem; margin-top: 1.1rem; }
.meta { background: rgba(255,255,255,.06); border-radius: 12px; padding: .6rem .8rem; }
.meta .k { color: #9fc8b2; font-size: .68rem; letter-spacing: .1em; text-transform: uppercase; }
.meta .v { color: #fff; font-weight: 600; font-size: .95rem; }
.note { color: #a9cdb9; font-size: .8rem; margin-top: 1rem; line-height: 1.5; }

/* ---------- ratings leaderboard ---------- */
.lb-row { display: grid; grid-template-columns: 34px 150px 1fr 52px; gap: .7rem; align-items: center; margin: .45rem 0; }
.lb-row .n { color: #e6f6ed; font-size: .88rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lb-row .track { height: 9px; border-radius: 99px; background: rgba(255,255,255,.08); overflow: hidden; }
.lb-row .fill { height: 100%; border-radius: 99px; background: var(--c); animation: grow 1s ease both; }
.lb-row .v { color: #fff; font-size: .85rem; text-align: right; font-weight: 600; }
.lb-row.dim { opacity: .55; }
.footer { color: #8fb9a2; font-size: .78rem; margin: 2rem 0 .5rem 0; }

@media (max-width: 700px) {
    .versus { grid-template-columns: 1fr 1fr; } .ring { display: none; }
    .lb-row { grid-template-columns: 30px 1fr 48px; } .lb-row .track { display: none; }
}
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes grow   { from { width: 0 !important; } }
@keyframes spin   { from { transform: rotate(-200deg) scale(.6); opacity: 0; } to { transform: none; opacity: 1; } }
</style>
"""
st.markdown(CSS.replace("__BG__", background_css_url()), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Load the exported model data
# ----------------------------------------------------------------------------
@st.cache_resource
def get_artifacts():
    return predictor.load_artifacts()


try:
    art = get_artifacts()
except predictor.MissingFilesError as exc:
    st.markdown(flat(f"""
    <div class="hero"><span class="eyebrow">Setup</span><h1>PSL <span>MATCH</span> PREDICTOR</h1></div>
    <div class="glass">
      <div class="step"><div class="t">One-time setup needed</div></div>
      <p style="color:#e6f6ed">The app needs <b>{esc(exc)}</b> next to <code>app.py</code>.
      This file is created by your notebook:</p>
      <ol style="color:#e6f6ed">
        <li>Open the notebook in Colab and run <b>Runtime → Run all</b>.</li>
        <li>Paste the code from <code>export_for_app.py</code> into a new last cell and run it. It downloads <code>app_data.json</code>.</li>
        <li>Put that file in the same folder as <code>app.py</code> (and commit it to GitHub if the app is deployed), then reload.</li>
      </ol>
    </div>
    """), unsafe_allow_html=True)
    st.stop()
except Exception as exc:
    st.error(f"Could not load the model: {exc}")
    st.stop()

teams, meta = art["teams"], art.get("meta", {})

# ----------------------------------------------------------------------------
# Hero + headline numbers
# ----------------------------------------------------------------------------
pills = ""
if meta:
    items = [(f"{meta.get('accuracy', 0):.1%}", "Walk-forward accuracy"),
             (str(meta.get("matches_tested", "?")), "Matches tested"),
             (str(len(teams)), "Teams"),
             (str(meta.get("last_match", "?")), "Data up to")]
    pills = '<div class="pills">' + "".join(
        f'<div class="pill"><div class="v">{esc(v)}</div><div class="k">{esc(k)}</div></div>' for v, k in items) + "</div>"

st.markdown(flat(f"""
<div class="hero">
  <span class="eyebrow">🏏 Pakistan Super League</span>
  <h1>PSL <span>MATCH</span><br>PREDICTOR</h1>
  <p>Pick the teams, call the toss and see who the model backs. Built from every PSL match since 2016.</p>
  {pills}
</div>
"""), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Match set-up
# ----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="step"><div class="n">1</div><div class="t">Choose the teams</div></div>', unsafe_allow_html=True)
    left, mid, right = st.columns([5, 1.1, 5])
    with left:
        team1 = st.selectbox("Team 1", teams, index=teams.index("Lahore Qalandars") if "Lahore Qalandars" in teams else 0)
        c1, k1 = team_style(team1)
        st.markdown(flat(f"""
        <div class="team-chip"><div class="badge" style="--c:{c1}">{esc(k1)}</div>
        <div><div class="nm">{esc(team1)}</div><div class="sub">Elo {art['elo'].get(team1, 1500):.0f}</div></div></div>
        """), unsafe_allow_html=True)
    with mid:
        st.markdown('<div class="vs">VS</div>', unsafe_allow_html=True)
    with right:
        default2 = teams.index("Multan Sultans") if "Multan Sultans" in teams else min(1, len(teams) - 1)
        team2 = st.selectbox("Team 2", teams, index=default2)
        c2, k2 = team_style(team2)
        st.markdown(flat(f"""
        <div class="team-chip"><div class="badge" style="--c:{c2}">{esc(k2)}</div>
        <div><div class="nm">{esc(team2)}</div><div class="sub">Elo {art['elo'].get(team2, 1500):.0f}</div></div></div>
        """), unsafe_allow_html=True)

    st.markdown('<div class="step"><div class="n">2</div><div class="t">Match &amp; toss</div></div>', unsafe_allow_html=True)
    venue = st.selectbox("Venue", art["venues"] or ["Not specified"])
    t1, t2 = st.columns(2)
    with t1:
        toss_winner = st.radio("Toss won by", [team1, team2], horizontal=True) if team1 != team2 else None
    with t2:
        decision = st.radio("Elected to", ["Bat first", "Field first"], horizontal=True)
    new_season = st.checkbox("First match of a new season (apply the start-of-season Elo reset)")
    go = st.button("PREDICT WINNER")

# ----------------------------------------------------------------------------
# Result
# ----------------------------------------------------------------------------
if go:
    if team1 == team2:
        st.warning("Please pick two different teams.")
        st.stop()

    p1 = predictor.predict(art, team1, team2, toss_winner, new_season)
    p2 = 1 - p1
    win, wcol = (team1, c1) if p1 >= p2 else (team2, c2)
    edge = abs(p1 - 0.5)
    tag = "Toss-up" if edge < 0.05 else ("Slight edge" if edge < 0.12 else "Clear edge")
    bat_first = toss_winner if decision == "Bat first" else (team2 if toss_winner == team1 else team1)
    e1, e2 = art["elo"].get(team1, 1500), art["elo"].get(team2, 1500)
    w1, w2 = ("win" if p1 >= p2 else ""), ("win" if p2 > p1 else "")

    st.markdown(flat(f"""
    <div class="glass">
      <div class="res-head" style="--c:{wcol}">
        <div class="lbl">Predicted winner</div>
        <div class="nm">{esc(win)}</div>
        <span class="tag">{tag}</span>
      </div>
      <div class="versus">
        <div class="tcard {w1}" style="--c:{c1}">
          <div class="badge" style="--c:{c1}">{esc(k1)}</div>
          <div class="tn">{esc(team1)}</div><div class="tp">{p1:.0%}</div><div class="te">ELO {e1:.0f}</div>
        </div>
        <div class="ring" style="background: conic-gradient({c1} 0 {p1*100:.1f}%, {c2} 0)"><div class="ring-in">VS</div></div>
        <div class="tcard {w2}" style="--c:{c2}">
          <div class="badge" style="--c:{c2}">{esc(k2)}</div>
          <div class="tn">{esc(team2)}</div><div class="tp">{p2:.0%}</div><div class="te">ELO {e2:.0f}</div>
        </div>
      </div>
      <div class="bar"><div style="width:{p1*100:.1f}%; background:{c1}"></div><div style="width:{p2*100:.1f}%; background:{c2}"></div></div>
      <div class="meta-grid">
        <div class="meta"><div class="k">Venue</div><div class="v">{esc(venue)}</div></div>
        <div class="meta"><div class="k">Toss</div><div class="v">{esc(toss_winner)} chose to {'bat' if decision == 'Bat first' else 'field'}</div></div>
        <div class="meta"><div class="k">Bats first</div><div class="v">{esc(bat_first)}</div></div>
        <div class="meta"><div class="k">Elo gap</div><div class="v">{abs(e1 - e2):.0f} pts</div></div>
      </div>
      <div class="note">The model uses two inputs: who won the toss and the Elo rating gap. Venue and the bat/field
      choice are shown for context only. PSL matches are very hard to predict, so treat this as a fun estimate, not a certainty.</div>
    </div>
    """), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Team ratings leaderboard
# ----------------------------------------------------------------------------
ranked = sorted(art["elo"].items(), key=lambda kv: -kv[1])
lo, hi = min(v for _, v in ranked) - 25, max(v for _, v in ranked) + 10
rows = ""
for name, val in ranked:
    col, code = team_style(name)
    width = max(6, (val - lo) / (hi - lo) * 100) if hi > lo else 50
    dim = "" if name in (team1, team2) else " dim"
    rows += (f'<div class="lb-row{dim}" style="--c:{col}"><div class="badge sm" style="--c:{col}">{esc(code)}</div>'
             f'<div class="n">{esc(name)}</div><div class="track"><div class="fill" style="width:{width:.1f}%"></div></div>'
             f'<div class="v">{val:.0f}</div></div>')
st.markdown(flat(f"""
<div class="glass">
  <div class="step"><div class="t">Current team ratings (Elo)</div></div>
  {rows}
</div>
"""), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# About the model
# ----------------------------------------------------------------------------
st.write("")
with st.expander("About the model"):
    if meta:
        st.markdown(
            f"- **Model:** {meta.get('model_name', art['model_name'])}\n"
            f"- **Walk-forward accuracy:** {meta.get('accuracy', 0):.1%} on {meta.get('matches_tested', '?')} matches "
            f"(AUC {meta.get('auc', 0):.2f})\n"
            f"- **Baselines:** always pick the toss winner {meta.get('toss_baseline', 0):.1%}; "
            f"always pick the chasing team {meta.get('chase_baseline', 0):.1%}\n"
            f"- **Trained on:** {meta.get('matches_total', '?')} matches up to {meta.get('last_match', '?')}"
        )
    st.markdown(
        "Every match is predicted by a model trained only on earlier seasons (walk-forward testing). "
        "The toss is the only clear signal found; heavier models and player-level features did not beat simple rules."
    )

credit = f" · by {esc(AUTHOR)}" if AUTHOR else ""
st.markdown(f'<div class="footer">Built with Streamlit · ball-by-ball PSL data{credit}</div>', unsafe_allow_html=True)
