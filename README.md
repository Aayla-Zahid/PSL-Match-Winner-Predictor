# 🏏 PSL Match Winner Predictor

A machine learning project that predicts the winner of a **Pakistan Super League (PSL)** match from the two teams, the venue and the toss, built on ball-by-ball data from 354 PSL matches (2016 to 2026).

### 🚀 [Live demo: psl-match-winner-predictor-aayla.streamlit.app](https://psl-match-winner-predictor-aayla.streamlit.app/)

---

## 📌 Overview

Pick two teams, a venue, the toss winner and the toss decision, and the app shows each team's win probability. The model behind it was chosen after a careful, leakage-free comparison of several algorithms, so the project is as much about **testing honestly** as it is about predicting.

**Headline finding:** T20 cricket is very random. Complex models (Random Forest, SVM, neural network) did **not** beat simple baselines. The **toss** is the only clear signal, and the final model is a small, explainable Logistic Regression using **toss + team Elo rating**.

## ✨ Features

- Win-probability prediction for any pair of PSL teams
- Inputs: team 1, team 2, venue, toss winner, toss decision (bat / field)
- Team strength tracked with an **Elo rating** updated after every match
- Predictions averaged over both team orders to remove ordering bias
- Streamlit web app, deployed online

## 📊 Dataset

- Source: [Cricsheet](https://cricsheet.org/) PSL ball-by-ball data (`psl_male_json.zip`)
- 357 match files, one JSON per match
- 354 matches with a winner after cleaning (3 no-results removed; 4 ties kept, decided by super over)
- Seasons 2015/16 to 2026

## 🔬 Methodology

| Step | What was done |
|---|---|
| 1 | Read the match JSON files into one table and save it as CSV |
| 2 | Clean the data (drop no-result matches, merge duplicate venue names, randomise team1/team2 order to avoid bias) |
| 3 | Explore: does the toss matter? (binomial test) |
| 4 | Feature engineering from information known **before** each match: recent form, overall win rate, head-to-head, venue record, home advantage, toss, Elo rating |
| 5 | **Walk-forward evaluation**: train on past seasons, test on the next one (no future data leaks into training) |
| 6 | Compare against baselines and test significance (McNemar's test, 95% intervals) |
| 7 | ROC curves, calibration and feature importance |
| 8 | Player-level features (batting and bowling ratings of the playing XI) |
| 9 | Export the best model's parameters to `app_data.json` for the app |

**Models compared:** Logistic Regression (several feature sets), Random Forest, SVM, Keras neural network.

## 📈 Results

Walk-forward test on 275 matches (2018/19 to 2026):

| Model | Accuracy | AUC |
|---|---|---|
| Baseline: always pick the chasing team | 54.5% | n/a |
| Baseline: always pick the toss winner | 59.6% | n/a |
| Logistic Regression (all features) | 53.5% | 0.507 |
| Random Forest | 47.6% | 0.510 |
| SVM | 51.6% | 0.518 |
| Keras neural network | 50.5% | 0.499 |
| **Logistic Regression (toss + Elo), final model** | **59.6%** | **0.588** |

**Key takeaways**

- The toss winner wins **58.8%** of all matches (p = 0.001), so the toss looks like it matters a little.
- Complex models scored near 50%, which is about the same as guessing.
- Player-level features did not improve accuracy: with only 354 matches, most players have too little history.
- With a test set this small, the final model is not statistically proven to beat the "chasing team" baseline (p = 0.125). Expect roughly 55 to 60% accuracy, not certainty.
- This is a prediction **made at the toss**, not days before the match.

## 🛠️ Tech Stack

Python · pandas · NumPy · scikit-learn · TensorFlow/Keras · SciPy · Matplotlib · Seaborn · Streamlit

## 📁 Project Structure

```
├── PSL_Match_Winner_Predictor.ipynb   # full analysis and model training
├── app.py                             # Streamlit web app
├── app_data.json                      # exported model parameters, team Elo ratings, venues
├── requirements.txt                   # Python dependencies
└── README.md
```

## ▶️ Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
streamlit run app.py
```

To retrain: open the notebook in Google Colab, upload `psl_male_json.zip`, run all cells, and the last cell regenerates `app_data.json`.

## 🔮 Future Work

- Rate players using other leagues (IPL, Big Bash, etc.) from Cricsheet to get far more history per player
- Add pitch, weather and dew information
- Model specific batter-versus-bowler matchups
- Re-run after every season to keep ratings up to date

## ⚠️ Disclaimer

This project is for learning and demonstration only. Cricket is unpredictable and the model's accuracy is modest. Do not use it for betting.

## 👩‍💻 Author

**Aayla Zahid**
BSCS, The University of Lahore

---

⭐ If you found this project interesting, consider giving the repo a star!
