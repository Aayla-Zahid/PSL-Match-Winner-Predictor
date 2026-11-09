🏏 PSL Match Winner Predictor

A Streamlit web app that predicts the winner of a Pakistan Super League (PSL) match from the two teams and the toss result, built on a machine-learning project that was tested honestly with walk-forward evaluation.

App screenshot

<!-- Take a screenshot of your running app, save it as docs/screenshot.png -->
✨ Features
Pick any two PSL teams, the venue, who won the toss and what they chose
Win probability for both teams with an animated bar and a "Toss-up / Slight edge / Clear edge" label
Live Elo rating for each team, with an optional start-of-season reset
Night-stadium theme with a cricket background (swap in your own photo, see below)
Honest "About the model" panel showing the real test accuracy and baselines
🧠 How the model works
Data: ball-by-ball match files in Cricsheet JSON format (one file per match, 354 matches with a result), turned into one row per match.
Features: built in date order using only information known before each match (no leakage): recent form, head-to-head, venue record, toss, home advantage, an Elo rating per team, and later player-level batting/bowling ratings.
Evaluation: walk-forward testing. Train on earlier seasons, predict the next one, repeat. Every match is predicted by a model that never saw it or anything after it.
Final model: Logistic Regression using two features, toss_won_t1 and elo_diff. Predictions are made twice (each team as "team 1") and averaged to remove team-order bias.
Results (275 matches, seasons 2018/19 to 2026)
Model / rule	Accuracy
Logistic (toss + Elo), used in the app	59.6%
Baseline: always pick the toss winner	59.6%
Baseline: always pick the chasing team	54.5%
Baseline: higher Elo	52.4%
Logistic Regression (all features)	53.5%
Random Forest	47.6%
SVM	51.6%
Keras neural network	49.5%

Takeaway: the toss is the only clear signal. Complex models, Elo on its own and even player-level features did not reliably beat simple rules, and none of the differences against the chasing-team baseline were statistically significant. PSL (T20 cricket) is very random, and 354 matches is a small dataset. The app should be treated as a fun estimate, not a betting tool.

📁 Project structure
psl-match-predictor/
├── app.py                    # Streamlit interface
├── predictor.py              # Prediction logic (mirrors predict_match() in the notebook)
├── export_for_app.py         # Cell to paste at the end of the notebook
├── PSL_Match_Winner_Predictor.ipynb
├── psl_best_model.pkl        # saved model (from the notebook, Step 10)
├── app_data.json             # team Elo ratings, venues, test results (from export_for_app.py)
├── assets/
│   └── stadium_batsman.svg   # default background
├── .streamlit/config.toml    # dark theme
└── requirements.txt
🚀 Run it locally
bash
git clone https://github.com/<your-username>/psl-match-predictor.git
cd psl-match-predictor
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
Getting the model files from your notebook

The app needs two files produced by the notebook:

Run the notebook up to Step 10. This creates psl_best_model.pkl.
Paste the contents of export_for_app.py into a new cell at the end of the notebook and run it. This creates app_data.json (current Elo ratings, venues and test results).
Download both files from Colab and put them in the project root, next to app.py.

Until both files are present, the app runs in demo mode (all teams rated equally) and shows a banner saying so.

Version tip: pickled scikit-learn models should be loaded with the same version that saved them. In Colab run pip show scikit-learn, then pin that version in requirements.txt (for example scikit-learn==1.6.1).

🖼️ Use your own background photo

Save any cricket image (a batter mid-shot, a floodlit stadium) as assets/background.jpg (or .png / .webp). The app uses it automatically and falls back to the built-in SVG if it is missing. Use photos you have the right to use, for example from Unsplash or Pexels, and check their licence.

☁️ Deploy for free (Streamlit Community Cloud)
Push this repo to GitHub (include psl_best_model.pkl and app_data.json).
Go to share.streamlit.io, sign in with GitHub and click New app.
Choose the repo, branch main and the main file app.py, then Deploy.
🔄 Updating after a new season

Add the new Cricsheet JSON files, re-run the notebook, then re-export psl_best_model.pkl and app_data.json and commit them. Elo ratings and form update automatically.

⚠️ Limitations
Small dataset (354 matches); results vary a lot from season to season.
Predictions are made at the toss: the toss result is a required input.
The saved model uses only the toss and the Elo gap. Venue and bat/field choice are shown for context and are not model inputs.
Team colours are approximate and the app uses short codes instead of official logos.
🔮 Future work
Train player ratings on other leagues (IPL, Big Bash) using shared Cricsheet player IDs
Add pitch, weather and dew information
Add batter-vs-bowler matchups
🙏 Data

Match data is in Cricsheet format. Please check Cricsheet's terms of use and credit them if you publish the data or results.

👩‍💻 Author

Laiba Bintay Naeem, BS Computer Science, The University of Lahore GitHub: @your-username

📄 License

MIT, see LICENSE (add one via GitHub: Add file → Create new file → LICENSE).
