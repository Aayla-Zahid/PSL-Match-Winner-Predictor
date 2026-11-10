"""PSL Match Winner Predictor: Streamlit app."""
import base64
import html as _html
from pathlib import Path

import streamlit as st

import predictor

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

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
    colour, code = TEAM_STYLE.get(name, ("#94a3b8", "".join(w[0] for w in name.split()[:3]).upper()))
    return colour, code


def esc(text: str) -> str:
    return _html.escape(str(text))


def flat(markup: str) -> str:
    """Remove indentation/newlines so Markdown never treats our HTML as a code block."""
    return "".join(line.strip() for line in markup.splitlines())


# ----------------------------------------------------------------------------
# Background: your own photo (assets/background.jpg|png|webp) or the built-in SVG
# ----------------------------------------------------------------------------
@st.cache_data
def background_css_url() -> str:
    for name, mime in [("background.jpg", "image/jpeg"), ("background.jpeg", "image/jpeg"),
                       ("background.png", "image/png"), ("background.webp", "image/webp"),
                       ("stadium_batsman.svg", "image/svg+xml")]:
        path = ASSETS / name
        if path.exists():
            b64 = base64.b64encode(path.read_bytes()).decode()
            return f"data:{mime};base64,{b64}"
    return ""


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Poppins', sans-serif; }

.stApp {
    background:
        linear-gradient(180deg, rgba(2,12,8,0.18) 0%, rgba(2,12,8,0.55) 100%),
        url("__BG__") center center / cover no-repeat fixed,
        #06251a;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }

/* ---------- hero ---------- */
.hero { text-align: center; margin: 0 0 1.6rem 0; animation: fadeUp .7s ease both; }
.hero .ball { font-size: 2.6rem; filter: drop-shadow(0 0 14px rgba(255,80,80,.7)); }
.hero h1 {
    font-family: 'Bebas Neue', sans-serif; font-size: clamp(2.6rem, 7vw, 5rem);
    letter-spacing: .08em; margin: 0; line-height: 1;
    background: linear-gradient(90deg, #ffffff 0%, #86efac 45%, #facc15 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    text-shadow: 0 0 40px rgba(34,197,94,.25);
}
.hero p { color: #cfe9dc; margin: .5rem 0 0 0; font-size: 1.02rem; letter-spacing: .04em; }

/* ---------- glass cards ---------- */
.glass {
    background: rgba(8, 28, 20, 0.58);
    border: 1px solid rgba(134, 239, 172, 0.18);
    border-radius: 20px; padding: 1.2rem 1.4rem;
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 10px 40px rgba(0,0,0,.35);
    animation: fadeUp .7s ease both;
}
.section-title {
    font-family: 'Bebas Neue', sans-serif; letter-spacing: .12em; font-size: 1.35rem;
    color: #86efac; margin: 0 0 .4rem 0;
}

/* ---------- team badges ---------- */
.team-chip { display:flex; align-items:center; gap:.8rem; margin: .2rem 0 .6rem 0; }
.badge {
    width: 54px; height: 54px; border-radius: 50%; display:flex; align-items:center; justify-content:center;
    font-family: 'Bebas Neue', sans-serif; font-size: 1.25rem; letter-spacing:.05em; color:#06130d;
    box-shadow: 0 0 22px var(--c); background: var(--c); border: 2px solid rgba(255,255,255,.55);
}
.team-chip .nm { font-weight: 700; font-size: 1.05rem; color: #fff; line-height: 1.1; }
.team-chip .sub { font-size: .78rem; color: #b7d8c6; }
.vs {
    display:flex; align-items:center; justify-content:center; height: 100%;
    font-family:'Bebas Neue',sans-serif; font-size: 2.4rem; color:#facc15; letter-spacing:.1em;
    text-shadow: 0 0 18px rgba(250,204,21,.6);
}

/* ---------- widgets ---------- */
label, .stRadio label, .stSelectbox label, .stCheckbox label { color: #e6f6ed !important; font-weight: 500; }
[data-baseweb="select"] > div {
    background: rgba(255,255,255,.08) !important; border: 1px solid rgba(134,239,172,.3) !important;
    border-radius: 12px !important; color: #fff !important;
}
.stButton { width: 100%; }
.stButton > button {
    width: 100%; border: 0; border-radius: 14px; padding: .85rem 1rem;
    font-family: 'Bebas Neue', sans-serif; font-size: 1.6rem; letter-spacing: .14em;
    color: #06130d; background: linear-gradient(90deg, #22c55e, #facc15);
    box-shadow: 0 8px 28px rgba(34,197,94,.35); transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 12px 34px rgba(250,204,21,.45); color:#06130d; }
.stButton > button:active { transform: scale(.99); }

/* ---------- result ---------- */
.winner-banner { text-align:center; margin-bottom: 1rem; }
.winner-banner .lbl { color:#b7d8c6; letter-spacing:.2em; font-size:.8rem; text-transform:uppercase; }
.winner-banner .nm {
    font-family:'Bebas Neue',sans-serif; font-size: clamp(2.2rem, 6vw, 3.8rem); letter-spacing:.06em;
    color: var(--c); text-shadow: 0 0 30px var(--c); line-height:1.05;
}
.winner-banner .tag {
    display:inline-block; margin-top:.3rem; padding:.2rem .8rem; border-radius:999px; font-size:.8rem;
    background: rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); color:#e6f6ed;
}
.prob-row { display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:.4rem; }
.prob-row .side { color:#fff; font-weight:600; }
.prob-row .pct { font-family:'Bebas Neue',sans-serif; font-size:2.4rem; line-height:1; }
.bar { display:flex; height: 20px; border-radius: 999px; overflow:hidden; background: rgba(255,255,255,.08); }
.bar > div { height:100%; animation: grow 1s cubic-bezier(.2,.8,.2,1) both; }
.meta-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:.7rem; margin-top:1rem; }
.meta { background: rgba(255,255,255,.06); border-radius:12px; padding:.6rem .8rem; }
.meta .k { color:#9fc8b2; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; }
.meta .v { color:#fff; font-weight:600; font-size:.98rem; }
.note { color:#b7d8c6; font-size:.82rem; margin-top:.9rem; }
.warn {
    background: rgba(250,204,21,.12); border:1px solid rgba(250,204,21,.4); color:#fde68a;
    border-radius:12px; padding:.6rem .9rem; font-size:.88rem; margin-bottom:1rem;
}
.footer { text-align:center; color:#8fb9a2; font-size:.78rem; margin: 2rem 0 .5rem 0; }

@keyframes fadeUp { from { opacity:0; transform: translateY(14px); } to { opacity:1; transform:none; } }
@keyframes grow   { from { width: 0 !important; } }
</style>
"""
st.markdown(CSS.replace("__BG__", background_css_url()), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Load model + data
# ----------------------------------------------------------------------------
@st.cache_resource
def get_artifacts():
    return predictor.load_artifacts()


try:
    art = get_artifacts()
except predictor.MissingFilesError as exc:
    st.markdown(flat(f"""
    <div class="hero"><div class="ball">🏏</div><h1>PSL Match Predictor</h1></div>
    <div class="glass">
      <div class="section-title">One-time setup needed</div>
      <p style="color:#e6f6ed">The app needs <b>{esc(exc)}</b> next to <code>app.py</code>.
      This file is created by your notebook:</p>
      <ol style="color:#e6f6ed">
        <li>Open the notebook in Colab and run <b>Runtime → Run all</b>.</li>
        <li>Paste the code from <code>export_for_app.py</code> into a new last cell and run it.
            It downloads <code>app_data.json</code>.</li>
        <li>Put that file in the same folder as <code>app.py</code> (and commit it to GitHub if the app is deployed), then reload.</li>
      </ol>
    </div>
    """), unsafe_allow_html=True)
    st.stop()
except Exception as exc:                      # e.g. wrong model type or version mismatch
    st.error(f"Could not load the model: {exc}")
    st.stop()

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(flat("""
<div class="hero">
  <div class="ball">🏏</div>
  <h1>PSL Match Predictor</h1>
  <p>Pick the teams, call the toss, and see who the model backs at the Pakistan Super League.</p>
</div>
"""), unsafe_allow_html=True)

teams = art["teams"]

# ----------------------------------------------------------------------------
# Match set-up
# ----------------------------------------------------------------------------
left, mid, right = st.columns([5, 1.2, 5])
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

st.markdown('<div class="section-title">Match details</div>', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1:
    venue = st.selectbox("Venue", art["venues"])
with d2:
    toss_winner = st.radio("Toss won by", [team1, team2], horizontal=True) if team1 != team2 else None
with d3:
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

    st.markdown(flat(f"""
    <div class="glass" style="margin-top:1.2rem">
      <div class="winner-banner" style="--c:{wcol}">
        <div class="lbl">Predicted winner</div>
        <div class="nm">{esc(win)}</div>
        <span class="tag">{tag}</span>
      </div>
      <div class="prob-row">
        <div><div class="side">{esc(team1)}</div><div class="pct" style="color:{c1}">{p1:.0%}</div></div>
        <div style="text-align:right"><div class="side">{esc(team2)}</div><div class="pct" style="color:{c2}">{p2:.0%}</div></div>
      </div>
      <div class="bar">
        <div style="width:{p1*100:.1f}%; background:{c1}"></div>
        <div style="width:{p2*100:.1f}%; background:{c2}"></div>
      </div>
      <div class="meta-grid">
        <div class="meta"><div class="k">Venue</div><div class="v">{esc(venue)}</div></div>
        <div class="meta"><div class="k">Toss</div><div class="v">{esc(toss_winner)} chose to {'bat' if decision == 'Bat first' else 'field'}</div></div>
        <div class="meta"><div class="k">Bats first</div><div class="v">{esc(bat_first)}</div></div>
      </div>
      <div class="note">The saved model uses two inputs: who won the toss and the Elo rating gap.
      Venue and bat/field choice are shown for context only. PSL matches are very hard to predict,
      so treat this as a fun estimate, not a certainty.</div>
    </div>
    """), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# About the model
# ----------------------------------------------------------------------------
with st.expander("About the model"):
    meta = art.get("meta", {})
    if meta:
        st.markdown(
            f"- **Model:** {meta.get('model_name', art['model_name'])}\n"
            f"- **Walk-forward accuracy:** {meta.get('accuracy', 0):.1%} on {meta.get('matches_tested', '?')} matches "
            f"(AUC {meta.get('auc', 0):.2f})\n"
            f"- **Baselines:** always pick the toss winner {meta.get('toss_baseline', 0):.1%}; "
            f"always pick the chasing team {meta.get('chase_baseline', 0):.1%}\n"
            f"- **Trained on:** {meta.get('matches_total', '?')} matches up to {meta.get('last_match', '?')}"
        )
    else:
        st.markdown("Add `app_data.json` (see README) to show the model's test results here.")
    st.markdown(
        "Every match is predicted by a model trained only on earlier seasons (walk-forward testing). "
        "The toss is the only clear signal found; heavier models and player-level features did not beat simple rules."
    )

st.markdown('<div class="footer">Built with Streamlit · scikit-learn · ball-by-ball PSL data</div>', unsafe_allow_html=True)
