# ---------------------------------------------------------------------------
# Paste this into a NEW CELL at the END of PSL_Match_Winner_Predictor.ipynb
# and run it (after Step 10, which saves psl_best_model.pkl).
# It writes app_data.json, which the Streamlit app reads.
# Then download BOTH psl_best_model.pkl and app_data.json into the repo root.
# ---------------------------------------------------------------------------
import json, os

app_data = {
    "elo":    {t: float(v) for t, v in final_state.elo.items()},   # current team ratings
    "teams":  sorted(final_state.elo.keys()),
    "venues": sorted(data["venue"].dropna().unique().tolist()),
    "meta": {
        "model_name":     best_name,
        "accuracy":       float(results.loc[best_name, "accuracy"]),
        "auc":            float(results.loc[best_name, "auc"]),
        "toss_baseline":  float(results.loc["Baseline: toss winner", "accuracy"]),
        "chase_baseline": float(results.loc["Baseline: chasing team", "accuracy"]),
        "matches_total":  int(len(data)),
        "matches_tested": int(evaluated.sum()),
        "last_match":     str(data["date"].max().date()),
    },
}
path = os.path.join(OUT_DIR, "app_data.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(app_data, f, indent=2)
print("Saved", path)
print(json.dumps(app_data["elo"], indent=2))
