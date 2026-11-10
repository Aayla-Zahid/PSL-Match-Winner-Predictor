"""Prediction logic for the PSL Match Winner Predictor.

The model is a Logistic Regression (toss + Elo gap). Instead of loading a pickled
scikit-learn object (which breaks when scikit-learn versions differ), the notebook
exports the model's numbers into app_data.json and we do the maths here with numpy:

    z = intercept + sum( coef_i * (x_i - mean_i) / scale_i )
    P(team1 wins) = 1 / (1 + e^-z)

Like the notebook's predict_match(), we ask twice (each team as "team1") and average,
which removes any bias from the arbitrary team order.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "app_data.json"      # created by the notebook export cell

BASE_ELO = 1500.0
SUPPORTED_FEATURES = {"toss_won_t1", "elo_diff"}


class MissingFilesError(Exception):
    """app_data.json is missing or was exported with an older version of the export cell."""


def load_artifacts() -> dict:
    if not DATA_PATH.exists():
        raise MissingFilesError("app_data.json")
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    params = data.get("model_params")
    if not params:
        raise MissingFilesError("app_data.json (it is from an older export: run the latest export_for_app.py cell again)")

    unsupported = set(params["features"]) - SUPPORTED_FEATURES
    if unsupported:
        raise ValueError(
            f"The exported model uses features this app cannot build: {sorted(unsupported)}. "
            "The app supports the 'Logistic (toss + Elo)' model (features: toss_won_t1, elo_diff)."
        )
    elo = {k: float(v) for k, v in data["elo"].items()}
    return {
        "params": {
            "features": list(params["features"]),
            "mean": np.array(params["mean"], dtype=float),
            "scale": np.array(params["scale"], dtype=float),
            "coef": np.array(params["coef"], dtype=float),
            "intercept": float(params["intercept"]),
        },
        "model_name": data.get("meta", {}).get("model_name", "Logistic (toss + Elo)"),
        "elo": elo,
        "teams": sorted(data.get("teams") or elo.keys()),
        "venues": data.get("venues") or [],
        "meta": data.get("meta", {}),
    }


def regress_elo(elo: dict) -> dict:
    """Start-of-season reset used in the notebook: pull ratings 25% back to 1500."""
    return {t: 0.75 * v + 0.25 * BASE_ELO for t, v in elo.items()}


def _proba(params: dict, row: dict) -> float:
    x = np.array([row[f] for f in params["features"]], dtype=float)
    z = params["intercept"] + float(np.dot(params["coef"], (x - params["mean"]) / params["scale"]))
    return 1.0 / (1.0 + math.exp(-z))


def predict(art: dict, team1: str, team2: str, toss_winner: str, new_season: bool = False) -> float:
    """Return the probability that `team1` wins."""
    if team1 == team2:
        raise ValueError("Pick two different teams.")
    if toss_winner not in (team1, team2):
        raise ValueError("The toss winner must be one of the two teams.")
    elo = regress_elo(art["elo"]) if new_season else art["elo"]
    e1, e2 = elo.get(team1, BASE_ELO), elo.get(team2, BASE_ELO)

    def p_first_wins(a: str, ea: float, eb: float) -> float:
        return _proba(art["params"], {"toss_won_t1": int(toss_winner == a), "elo_diff": ea - eb})

    return (p_first_wins(team1, e1, e2) + 1 - p_first_wins(team2, e2, e1)) / 2
