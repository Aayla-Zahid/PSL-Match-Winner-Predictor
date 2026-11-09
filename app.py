from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from predictor import build_history, predict_match, read_match_zip, train_model

ROOT = Path(__file__).parent
ASSET = ROOT / "assets" / "stadium_cricket.jpg"
TEAMS = [
    "Islamabad United",
    "Karachi Kings",
    "Lahore Qalandars",
    "Multan Sultans",
    "Peshawar Zalmi",
    "Quetta Gladiators",
    "Rawalpindiz",
    "Hyderabad Kingsmen",
]

st.set_page_config(page_title="PSL Match Predictor", page_icon="🏏", layout="wide")


def load_matches(contents: bytes) -> pd.DataFrame:
    return read_match_zip(contents)


@st.cache_data(show_spinner=False)
def cached_matches(contents: bytes) -> pd.DataFrame:
    return load_matches(contents)


def hero_image_css() -> str:
    if not ASSET.exists():
        return ""
    import base64

    encoded = base64.b64encode(ASSET.read_bytes()).decode("ascii")
    return f"url('data:image/jpeg;base64,{encoded}')"


st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');
    :root {{ --pitch:#a6f45c; --ink:#f3f4ed; --muted:#a5aa9f; --panel:#171b18; --edge:#2a302b; }}
    html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif; }}
    .stApp {{ background:radial-gradient(ellipse at 75% 0%,#17241a 0%,#0e110f 45%,#0b0d0b 100%); color:var(--ink); }}
    [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stSidebar"] {{ background:#101410; border-right:1px solid var(--edge); }}
    [data-testid="stSidebar"] * {{ color:var(--ink); }}
    .main .block-container {{ max-width:1320px; padding-top:1.25rem; padding-bottom:4rem; }}
    .brandbar {{ display:flex; align-items:center; justify-content:space-between; margin:0 0 1rem; color:#d9dfd6; font-size:12px; letter-spacing:1.5px; text-transform:uppercase; }}
    .brandmark {{ color:var(--pitch); font-weight:700; }}
    .live-tag {{ border:1px solid #39433a; border-radius:99px; padding:7px 12px; color:#c6d0c3; font-size:10px; letter-spacing:1px; }}
    .hero {{ min-height:354px; display:flex; align-items:center; position:relative; overflow:hidden; border:1px solid #353a34; border-radius:8px; padding:46px 5.2%; background-image:linear-gradient(90deg,rgba(8,12,9,.96) 0%,rgba(8,12,9,.84) 37%,rgba(8,12,9,.14) 100%),{hero_image_css()}; background-size:cover; background-position:center 42%; }}
    .hero-copy {{ max-width:570px; }}
    .eyebrow {{ display:inline-flex; align-items:center; gap:8px; padding:7px 10px; border:1px solid #44533e; border-radius:99px; color:#c8f397; font-size:10px; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; }}
    .eyebrow span {{ width:7px; height:7px; border-radius:50%; background:var(--pitch); box-shadow:0 0 12px var(--pitch); }}
    .hero h1 {{ margin:22px 0 8px; color:#f4f5ed; font-family:'Barlow Condensed',sans-serif; font-size:clamp(52px,7vw,88px); font-weight:800; line-height:.88; letter-spacing:.5px; text-transform:uppercase; }}
    .hero h1 em {{ color:var(--pitch); font-style:normal; }}
    .hero p {{ max-width:420px; margin:18px 0 0; color:#c4c9c0; font-size:14px; line-height:1.7; }}
    .section-head {{ display:flex; align-items:end; justify-content:space-between; gap:16px; margin:34px 0 16px; }}
    .section-head h2 {{ margin:0; color:var(--ink); font-family:'Barlow Condensed',sans-serif; font-size:30px; font-weight:700; letter-spacing:.4px; text-transform:uppercase; }}
    .section-head p {{ margin:4px 0 0; color:var(--muted); font-size:12px; }}
    .metric-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
    .metric {{ padding:17px 19px; border:1px solid var(--edge); border-radius:6px; background:linear-gradient(130deg,#171b18,#111512); }}
    .metric-label {{ color:var(--muted); font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; }}
    .metric-value {{ margin-top:9px; color:#f2f4ec; font-family:'Barlow Condensed',sans-serif; font-size:34px; font-weight:700; line-height:1; }}
    .metric-note {{ margin-top:7px; color:#8f978e; font-size:11px; }}
    .form-wrap {{ padding:24px; border:1px solid var(--edge); border-radius:6px; background:#141815; }}
    .vs {{ display:grid; place-items:center; height:100%; min-height:70px; color:#778075; font-family:'Barlow Condensed',sans-serif; font-size:20px; font-weight:700; }}
    .result {{ padding:24px; border:1px solid #374432; border-radius:6px; background:linear-gradient(110deg,#172019,#121613); }}
    .result-kicker {{ color:#b4c9a3; font-size:10px; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; }}
    .result-winner {{ margin:8px 0 3px; color:var(--pitch); font-family:'Barlow Condensed',sans-serif; font-size:40px; font-weight:700; line-height:1.05; }}
    .result-pct {{ color:#e1e8dc; font-size:13px; }}
    .prob-label {{ display:flex; justify-content:space-between; margin:19px 0 7px; color:#c1c8bc; font-size:11px; }}
    .fineprint {{ color:#929b90; font-size:11px; line-height:1.65; }}
    div[data-testid="stButton"] button {{ min-height:46px; border:0; border-radius:4px; background:var(--pitch); color:#10150c; font-weight:800; }}
    div[data-testid="stButton"] button:hover {{ background:#befb7e; color:#10150c; }}
    div[data-testid="stSelectbox"] label, div[data-testid="stCheckbox"] label {{ color:#cbd0c7; font-size:12px; font-weight:600; }}
    div[data-baseweb="select"] > div {{ border-color:#3a413b; background:#111512; }}
    [data-testid="stAlert"] {{ border-radius:5px; }}
    .footer-note {{ margin-top:30px; padding-top:14px; border-top:1px solid #282d29; color:#7f887e; font-size:10px; }}
    @media (max-width:700px) {{
      .hero {{ min-height:330px; padding:28px 22px; background-position:62% center; }}
      .hero h1 {{ font-size:58px; }}
      .metric-grid {{ grid-template-columns:1fr; }}
      .section-head {{ align-items:flex-start; flex-direction:column; }}
      .form-wrap {{ padding:17px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 🏏 PSL MATCH DESK")
    st.caption("Your historical match file stays in this app session.")
    uploaded = st.file_uploader(
        "Match archive (.zip)",
        type=["zip"],
        help="Choose the ZIP of PSL match JSON files used by the notebook.",
    )
    st.markdown("---")
    st.markdown("**Data needed**")
    st.caption("A ZIP containing one JSON file per match. The notebook itself does not include these match files.")
    st.markdown("---")
    st.caption("Powered by your notebook's Logistic Regression (toss + Elo) model.")

st.markdown(
    """
    <div class="brandbar"><div class="brandmark">◉ &nbsp; PSL / MATCH DESK</div><div class="live-tag">● &nbsp; PRE-MATCH ANALYSIS</div></div>
    <section class="hero"><div class="hero-copy">
      <div class="eyebrow"><span></span> YOUR MATCH. YOUR CALL.</div>
      <h1>Own the<br><em>moment.</em></h1>
      <p>Pick the sides, set the toss winner, and see how past PSL results shape the odds.</p>
    </div></section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-head"><div><h2>The numbers behind the call</h2><p>The results from your notebook's walk-forward evaluation.</p></div></div>
    <div class="metric-grid">
      <div class="metric"><div class="metric-label">Completed matches</div><div class="metric-value">354</div><div class="metric-note">Across the notebook's tested PSL seasons</div></div>
      <div class="metric"><div class="metric-label">Top model accuracy</div><div class="metric-value">59.6%</div><div class="metric-note">Logistic Regression · toss + Elo</div></div>
      <div class="metric"><div class="metric-label">Always pick toss winner</div><div class="metric-value">59.6%</div><div class="metric-note">Same score in that notebook backtest</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploaded is not None:
    try:
        matches = cached_matches(uploaded.getvalue())
    except (ValueError, OSError, Exception) as error:
        st.error(f"That archive could not be read: {error}")
        matches = pd.DataFrame()
else:
    matches = pd.DataFrame()

history = pd.DataFrame()
state = None
model = None
if not matches.empty:
    history, state = build_history(matches)
    try:
        model = train_model(history)
    except ValueError as error:
        st.warning(str(error))

st.markdown(
    "<div class='section-head'><div><h2>Build your match-up</h2><p>Choose the teams and the toss winner.</p></div></div>",
    unsafe_allow_html=True,
)

team_options = sorted(set(TEAMS + (matches["team1"].tolist() + matches["team2"].tolist() if not matches.empty else [])))
with st.container(border=True):
    st.markdown("<div class='form-wrap'>", unsafe_allow_html=True)
    left, middle, right = st.columns([5, 1, 5])
    with left:
        team1 = st.selectbox("HOME SIDE", team_options, index=team_options.index("Lahore Qalandars"))
    with middle:
        st.markdown("<div class='vs'>VS</div>", unsafe_allow_html=True)
    with right:
        team2_default = "Multan Sultans" if "Multan Sultans" != team1 else "Karachi Kings"
        team2 = st.selectbox("AWAY SIDE", team_options, index=team_options.index(team2_default))
    toss_winner = st.selectbox("TOSS WINNER", [team1, team2])
    new_season = st.checkbox("First match of a new PSL season (reset Elo toward 1500)")
    predict_clicked = st.button("PREDICT THIS MATCH", use_container_width=True, disabled=(model is None))
    st.markdown("</div>", unsafe_allow_html=True)

if predict_clicked and model is not None and state is not None:
    try:
        chance = predict_match(model, state, team1, team2, toss_winner, new_season)
        winner = team1 if chance >= 0.5 else team2
        winner_chance = chance if chance >= 0.5 else 1 - chance
        st.markdown("<div class='section-head'><div><h2>Match outlook</h2></div></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result">
              <div class="result-kicker">MODEL PICK · HISTORICAL FORM + TOSS</div>
              <div class="result-winner">{winner}</div>
              <div class="result-pct">{winner_chance:.0%} estimated win probability</div>
              <div class="prob-label"><span>{team1}</span><span>{chance:.0%} &nbsp; / &nbsp; {1-chance:.0%}</span><span>{team2}</span></div>
              <div style="display:flex;height:8px;overflow:hidden;border-radius:99px;background:#384037">
                <div style="width:{chance:.1%};background:#a6f45c"></div><div style="flex:1;background:#515a50"></div>
              </div>
              <p class="fineprint" style="margin:16px 0 0">An estimate from the uploaded historical results, not a guarantee. The selected notebook model uses toss-winner status and Elo difference; it does not include line-ups, injuries, weather, or venue effects.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except ValueError as error:
        st.error(str(error))

if uploaded is None:
    st.info("Upload your PSL match JSON ZIP in the left panel to enable predictions. The uploaded notebook contains the model workflow, but not the match archive.")
elif not matches.empty and model is not None:
    st.markdown(
        f"<div class='footer-note'>Loaded {len(matches)} completed matches · {len(history)} with usable toss data · model retrained from this archive.</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div class='footer-note'>Backtest results are from the uploaded notebook's recorded run. Its toss + Elo model and the toss-winner baseline both scored 59.6%; the notebook did not establish a statistically clear advantage over always picking the chasing side.</div>",
    unsafe_allow_html=True,
)
