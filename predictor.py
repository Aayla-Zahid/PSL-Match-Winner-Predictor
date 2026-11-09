"""Prediction logic for the PSL Match Winner Predictor.

Kept separate from the Streamlit UI so it can be tested without Streamlit.
It mirrors `predict_match()` from the notebook (Step 11):
  1. take each team's current Elo rating,
  2. ask the saved model twice (each team as "team1") and average,
     which removes any bias from the arbitrary team order.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "psl_best_model.pkl"   # saved by the notebook (Step 10)
DATA_PATH = ROOT / "app_data.json"         # exported by export_for_app.py

BASE_ELO = 1500.0
SUPPORTED_FEATURES = {"toss_won_t1", "elo_diff"}

# Only used for "demo mode", when the notebook files have not been added yet.
DEFAULT_TEAMS = [
    "Hyderabad Kingsmen", "Islamabad United", "Karachi Kings", "Lahore Qalandars",
    "Multan Sultans", "Peshawar Zalmi", "Quetta Gladiators", "Rawalpindiz",
]
DEFAULT_VENUES = [
    "Gaddafi Stadium, Lahore", "National Stadium, Karachi",
    "Rawalpindi Cricket Stadium", "Dubai International Cricket Stadium",
]


def load_artifacts() -> dict:
    """Load the saved model + team data. Falls back to demo mode if files are missing."""
    art = {
        "model": None, "features": [], "model_name": None,
        "elo": {t: BASE_ELO for t in DEFAULT_TEAMS},
        "teams": list(DEFAULT_TEAMS), "venues": list(DEFAULT_VENUES),
        "meta": {}, "demo": True,
    }
    if DATA_PATH.exists():
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        art["elo"] = {k: float(v) for k, v in data["elo"].items()}
        art["teams"] = sorted(data.get("teams") or art["elo"].keys())
        art["venues"] = data.get("venues") or art["venues"]
        art["meta"] = data.get("meta", {})
    if MODEL_PATH.exists():
        saved = joblib.load(MODEL_PATH)
        unsupported = set(saved["features"]) - SUPPORTED_FEATURES
        if unsupported:
            raise ValueError(
                f"The saved model uses features this app cannot build: {sorted(unsupported)}. "
                "The app supports the 'Logistic (toss + Elo)' model (features: toss_won_t1, elo_diff)."
            )
        art.update(model=saved["model"], features=list(saved["features"]),
                   model_name=saved["name"], demo=False)
    return art


def regress_elo(elo: dict) -> dict:
    """Start-of-season reset used in the notebook: pull ratings 25% back to 1500."""
    return {t: 0.75 * v + 0.25 * BASE_ELO for t, v in elo.items()}


def predict(art: dict, team1: str, team2: str, toss_winner: str, new_season: bool = False) -> float:
    """Return the probability that `team1` wins."""
    if team1 == team2:
        raise ValueError("Pick two different teams.")
    if toss_winner not in (team1, team2):
        raise ValueError("The toss winner must be one of the two teams.")
    elo = regress_elo(art["elo"]) if new_season else art["elo"]
    e1, e2 = elo.get(team1, BASE_ELO), elo.get(team2, BASE_ELO)

    def p_first_wins(a: str, b: str, ea: float, eb: float) -> float:
        if art["model"] is None:                       # demo mode: plain Elo expectation
            return 1 / (1 + 10 ** ((eb - ea) / 400))
        row = {"toss_won_t1": int(toss_winner == a), "elo_diff": ea - eb}
        X = pd.DataFrame([row])[art["features"]]
        return float(art["model"].predict_proba(X)[0, 1])

    # ask twice (each team as "team1") and average, exactly like the notebook
    return (p_first_wins(team1, team2, e1, e2) + 1 - p_first_wins(team2, team1, e2, e1)) / 2
