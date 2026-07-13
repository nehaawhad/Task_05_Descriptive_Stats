"""
Ground Truth Script - 2025 Syracuse Women's Lacrosse Season
Task 05: Descriptive Statistics and Large Language Models

Computes trusted descriptive statistics two independent ways:
  1. Pandas  (primary, does the heavy lifting)
  2. Pure Python (cross-check on the highest-stakes numbers, no libraries)

If both methods agree, the number goes in the answer key.
Run: python ground_truth.py
"""

import csv
import pandas as pd

PLAYERS_CSV = "../data/players_2025.csv"
GAMES_CSV = "../data/games_2025.csv"


# ---------------------------------------------------------------------------
# PANDAS VERSION
# ---------------------------------------------------------------------------
def pandas_ground_truth():
    players = pd.read_csv(PLAYERS_CSV)
    games = pd.read_csv(GAMES_CSV)

    answers = {}

    # --- Basic facts ---
    answers["games_played"] = len(games)
    answers["wins"] = (games["result"] == "W").sum()
    answers["losses"] = (games["result"] == "L").sum()

    # --- Top scorer ---
    top_scorer_row = players.loc[players["g"].idxmax()]
    answers["top_scorer"] = top_scorer_row["player"]
    answers["top_scorer_goals"] = int(top_scorer_row["g"])

    # --- Top points player (different from top goal scorer) ---
    top_pts_row = players.loc[players["pts"].idxmax()]
    answers["top_points_player"] = top_pts_row["player"]
    answers["top_points"] = int(top_pts_row["pts"])

    # --- Average margin of victory in wins ---
    wins_df = games[games["result"] == "W"]
    margins = wins_df["su_score"] - wins_df["opp_score"]
    answers["avg_margin_of_victory"] = round(margins.mean(), 2)

    # --- Average margin of defeat in losses ---
    losses_df = games[games["result"] == "L"]
    loss_margins = losses_df["opp_score"] - losses_df["su_score"]
    answers["avg_margin_of_defeat"] = round(loss_margins.mean(), 2)

    # --- Highest combined score game ---
    games["combined_score"] = games["su_score"] + games["opp_score"]
    highest_combined = games.loc[games["combined_score"].idxmax()]
    answers["highest_combined_game"] = (
        f"{highest_combined['opponent']} on {highest_combined['date']} "
        f"({int(highest_combined['su_score'])}-{int(highest_combined['opp_score'])}, "
        f"combined {int(highest_combined['combined_score'])})"
    )

    # --- Team shooting percentage across the season (weighted, not avg of averages) ---
    total_goals = games["su_goals"].sum()
    total_shots = games["su_shots"].sum()
    answers["season_shooting_pct"] = round(total_goals / total_shots, 3)

    # --- Player with most draw controls, caused turnovers, ground balls ---
    answers["most_ground_balls"] = players.loc[players["gb"].idxmax(), "player"]
    answers["most_caused_turnovers"] = players.loc[players["ct"].idxmax(), "player"]
    answers["most_turnovers_committed"] = players.loc[players["to"].idxmax(), "player"]

    return answers


# ---------------------------------------------------------------------------
# PURE PYTHON CROSS-CHECK (no libraries) — validates the highest-stakes facts
# ---------------------------------------------------------------------------
def pure_python_cross_check():
    with open(PLAYERS_CSV, newline="") as f:
        players = list(csv.DictReader(f))
    with open(GAMES_CSV, newline="") as f:
        games = list(csv.DictReader(f))

    checks = {}

    checks["games_played"] = len(games)
    checks["wins"] = sum(1 for g in games if g["result"] == "W")
    checks["losses"] = sum(1 for g in games if g["result"] == "L")

    top_scorer = max(players, key=lambda p: int(p["g"]))
    checks["top_scorer"] = top_scorer["player"]
    checks["top_scorer_goals"] = int(top_scorer["g"])

    win_margins = [
        int(g["su_score"]) - int(g["opp_score"]) for g in games if g["result"] == "W"
    ]
    checks["avg_margin_of_victory"] = round(sum(win_margins) / len(win_margins), 2)

    best = max(games, key=lambda g: int(g["su_score"]) + int(g["opp_score"]))
    checks["highest_combined_game"] = (
        f"{best['opponent']} on {best['date']} "
        f"({best['su_score']}-{best['opp_score']}, "
        f"combined {int(best['su_score']) + int(best['opp_score'])})"
    )

    total_goals = sum(int(g["su_goals"]) for g in games)
    total_shots = sum(int(g["su_shots"]) for g in games)
    checks["season_shooting_pct"] = round(total_goals / total_shots, 3)

    return checks


if __name__ == "__main__":
    pd_answers = pandas_ground_truth()
    py_answers = pure_python_cross_check()

    print("=" * 70)
    print("GROUND TRUTH ANSWER KEY — 2025 SU Women's Lacrosse")
    print("=" * 70)
    for k, v in pd_answers.items():
        print(f"{k:30s}: {v}")

    print("\n" + "=" * 70)
    print("CROSS-CHECK: pure Python vs pandas (should match exactly)")
    print("=" * 70)
    all_match = True
    for k, v in py_answers.items():
        match = pd_answers.get(k) == v
        all_match = all_match and match
        flag = "OK" if match else "MISMATCH"
        print(f"{k:30s}: pandas={pd_answers.get(k)!r:30} python={v!r:30} [{flag}]")

    print("\nAll cross-checked values match:", all_match)
