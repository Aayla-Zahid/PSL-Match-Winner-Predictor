import json
import numpy as np

# the model's numbers (no pickle, so it works with any scikit-learn version)
scaler = best_model.named_steps["sc"]
logit  = best_model.named_steps["m"]
params = {
    "features":  list(best_cols),
    "mean":      scaler.mean_.tolist(),
    "scale":     scaler.scale_.tolist(),
    "coef":      logit.coef_[0].tolist(),
    "intercept": float(logit.intercept_[0]),
}

# safety check: our own maths must match scikit-learn
test = data[best_cols].head(20)
z = params["intercept"] + ((test.values - np.array(params["mean"])) / np.array(params["scale"])) @ np.array(params["coef"])
mine = 1 / (1 + np.exp(-z))
assert np.allclose(mine, best_model.predict_proba(test)[:, 1], atol=1e-6), "exported numbers do not match the model"
print("Check passed: exported model matches scikit-learn")

app_data = {
    "model_params": params,
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
with open("app_data.json", "w", encoding="utf-8") as f:
    json.dump(app_data, f, indent=2)

print("Model:", best_name, "| features:", best_cols)
print("Team Elo ratings:")
for t, v in sorted(app_data["elo"].items(), key=lambda kv: -kv[1]):
    print(f"  {t:22s} {v:7.1f}")

# download the file (Colab only)
try:
    from google.colab import files
    files.download("app_data.json")
except ImportError:
    print("Not in Colab: app_data.json is in the current folder.")
