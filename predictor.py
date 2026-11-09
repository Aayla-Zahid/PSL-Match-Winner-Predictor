"""Match-history feature builder and Elo-backed PSL prediction helpers."""
from __future__ import annotations

import copy
import io
import json
import zipfile
from collections import defaultdict
from pathlib import PurePosixPath
from typing import Any

import numpy as np
import pandas as pd

MODEL_FEATURES = ["toss_won_t1", "elo_diff"]


def _parse_match(document: dict[str, Any], match_id: int) -> dict[str, Any] | None:
    info = document.get("info", {})
    teams = info.get("teams", [])
    innings = document.get("innings", [])
    dates = info.get("dates", [])
    if len(teams) != 2 or not dates:
        return None
    outcome = info.get("outcome", {})
    winner = outcome.get("winner") or outcome.get("eliminator")
    if winner not in teams:
        return None
    toss = info.get("toss", {})
    return {
        "match_id": match_id,
        "date": pd.to_datetime(dates[0], errors="coerce"),
        "season": str(info.get("season", "Unknown")),
        "venue": info.get("venue") or "Unknown venue",
        "team1": teams[0],
        "team2": teams[1],
        "toss_winner": toss.get("winner"),
        "winner": winner,
        "bat_first": innings[0].get("team") if innings else None,
    }


def read_match_zip(contents: bytes) -> pd.DataFrame:
    """Read match JSON files from an archive without extracting paths to disk."""
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(io.BytesIO(contents)) as archive:
        for member in archive.infolist():
            path = PurePosixPath(member.filename)
            if member.is_dir() or path.suffix.lower() != ".json":
                continue
            try:
                document = json.loads(archive.read(member).decode("utf-8"))
                match_id = int(path.stem)
                row = _parse_match(document, match_id)
                if row is not None and not pd.isna(row["date"]):
                    rows.append(row)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError, KeyError, TypeError):
                continue
    if not rows:
        return pd.DataFrame()
    result = pd.DataFrame(rows).drop_duplicates("match_id")
    result["venue"] = result["venue"].replace(
        {"National Bank Cricket Arena, Karachi": "National Stadium, Karachi"}
    )
    return result.sort_values(["date", "match_id"]).reset_index(drop=True)


class TeamState:
    """A lightweight running Elo memory; update only after a match is featured."""

    K = 20

    def __init__(self) -> None:
        self.elo: defaultdict[str, float] = defaultdict(lambda: 1500.0)

    def new_season(self) -> None:
        for team in list(self.elo):
            self.elo[team] = 0.75 * self.elo[team] + 0.25 * 1500

    def features(self, team1: str, team2: str, toss_winner: str) -> dict[str, float]:
        return {
            "toss_won_t1": float(toss_winner == team1),
            "elo_diff": float(self.elo[team1] - self.elo[team2]),
        }

    def update(self, team1: str, team2: str, winner: str) -> None:
        loser = team2 if winner == team1 else team1
        expected = 1 / (1 + 10 ** ((self.elo[loser] - self.elo[winner]) / 400))
        change = self.K * (1 - expected)
        self.elo[winner] += change
        self.elo[loser] -= change


def build_history(raw_matches: pd.DataFrame) -> tuple[pd.DataFrame, TeamState]:
    """Replay matches in date order and create leakage-safe toss/Elo features."""
    if raw_matches.empty:
        return pd.DataFrame(), TeamState()

    ordered = raw_matches.sort_values(["date", "match_id"]).reset_index(drop=True)
    randomizer = np.random.default_rng(42)
    state = TeamState()
    previous_season: str | None = None
    records: list[dict[str, Any]] = []

    for row in ordered.itertuples(index=False):
        season = str(row.season)
        if previous_season is not None and season != previous_season:
            state.new_season()
        previous_season = season

        team1, team2 = row.team1, row.team2
        if randomizer.random() < 0.5:
            team1, team2 = team2, team1
        toss_winner = row.toss_winner
        state.elo[team1]
        state.elo[team2]

        if toss_winner in (team1, team2):
            record = {
                "team1": team1,
                "team2": team2,
                "winner": row.winner,
                "team1_won": int(row.winner == team1),
                **state.features(team1, team2, toss_winner),
            }
            records.append(record)
        state.update(team1, team2, row.winner)

    return pd.DataFrame(records), state


def train_model(history: pd.DataFrame):
    """Fit the notebook's best walk-forward model: logistic regression on toss + Elo."""
    if len(history) < 20 or history["team1_won"].nunique() < 2:
        raise ValueError("Add at least 20 completed matches with toss information and both outcomes.")

    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("logistic", LogisticRegression(C=1, max_iter=1000, random_state=42)),
        ]
    )
    model.fit(history[MODEL_FEATURES], history["team1_won"])
    return model


def predict_match(
    model,
    final_state: TeamState,
    team1: str,
    team2: str,
    toss_winner: str,
    new_season: bool = False,
) -> float:
    """Return team1's probability, averaging both team orders to limit order bias."""
    if team1 == team2:
        raise ValueError("Choose two different teams.")
    if toss_winner not in (team1, team2):
        raise ValueError("The toss winner must be one of the selected teams.")

    state = copy.deepcopy(final_state)
    if new_season:
        state.new_season()
    first = state.features(team1, team2, toss_winner)
    second = state.features(team2, team1, toss_winner)
    p_first = float(model.predict_proba(pd.DataFrame([first])[MODEL_FEATURES])[0, 1])
    p_second = float(model.predict_proba(pd.DataFrame([second])[MODEL_FEATURES])[0, 1])
    return (p_first + 1 - p_second) / 2
