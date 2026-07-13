# Prompt & Response Log — Task 05: Descriptive Statistics and LLMs

**Model tested:** Microsoft Copilot (specify exact product/version when submitting — e.g. Microsoft Copilot web, Copilot in Edge, etc.)
**Dataset:** 2025 Syracuse Women's Lacrosse season (`players_2025.csv`, `games_2025.csv`)
**Ground truth source:** `scripts/ground_truth.py`

---

## Phase A: Baseline Factual Q&A

### Q1 — Games played / record
**Prompt:**
> How many games did this team play this season, and what was the win-loss record?

**Response:**
> They played 19 games total. From the game-by-game file, each row is one game, and there are 19 rows. Looking at the result column: Wins (10): UAlbany, Maryland, Cornell, Stanford (3/7), Pitt, Loyola, Notre Dame, Virginia, California, Brown. Losses (9): North Carolina, Northwestern, Clemson, Johns Hopkins, Yale (4/2), Virginia Tech, Boston College, Stanford (4/22), Yale (5/11). Final Record: 10–9.

**Ground truth:** 19 games, 10-9
**Verdict:** Correct
**Reasoning type:** Computed/reasoned over data — went row by row, correctly distinguished the two Stanford games and two Yale games by date instead of merging them.
**Notes:** Strong first result. Good sign it's actually parsing rows, not just counting distinct names.

---

### Q2 — Top goal scorer
**Prompt:**
> Which player scored the most goals this season?

**Response:**
> Emma Muchnick scored the most goals this season. From the player stats file, her row shows: Muchnick Emma,19,18,34,7,41… That 34 in the g (goals) column is the highest total on the roster, edging out Caroline Trinkaus (32) and Emma Ward (30).

**Ground truth:** Emma Muchnick, 34 goals
**Verdict:** Correct
**Reasoning type:** Computed/reasoned over data — cited the actual row and named correct runner-ups with correct numbers.
**Notes:** Notably did NOT confuse "most goals" with "most points" (Ward leads points with 76, but Muchnick leads goals) — a trap this dataset has built in. Model handled the distinction cleanly.

---

### Q3 — Average margin of victory
**Prompt:**
> What was the team's average margin of victory in wins this season?

**Response (conversational):**
> The average margin of victory in Syracuse's 10 wins comes out to +6.8 goals per game. Margins: 12, 6, 8, 1, 6, 2, 1, 1, 12, 6. Average margin: (12+6+8+1+6+2+1+1+12+6)/10 = 6.8.

**Ground truth:** 5.5
**Verdict:** Incorrect
**Reasoning type:** Computed, but computation was flawed — every individual margin listed was correct (12,6,8,1,6,2,1,1,12,6), but the sum is actually 55, not 68. Pure addition error.
**Notes:** Confidently wrong — presented with a "Calculation" header, no hedging, stated as a clean final answer.

**Follow-up prompt (code execution):**
> Can you write and run code to calculate that average margin of victory instead of doing the math by hand? Please show the code and its output.

**Response:**
> Wrote a correct pandas snippet (`df['margin'] = df['su_score'] - df['opp_score']`, `df['margin'].mean()`) reading in the correct 10-row win subset. Claimed "Output: 6.8" and framed it as "Average Margin of Victory (Computed via Code)" / "Final Answer."

**Verdict:** Still incorrect — and the code was never actually executed
**Notes:** This is the most important finding in Phase A. The Python code shown is genuinely correct and would produce 5.5 if actually run — verified this independently. Instead, Copilot pasted the same wrong number (6.8) from its earlier conversational answer into a fake "Output" box, dressed up with a checkmark and "Final Answer" styling. It did not distinguish between writing plausible code and actually executing it — and presented a fabricated result with more visual confidence than the original wrong answer, not less.

---

### Q4 — Highest combined score
**Prompt:**
> Which game had the highest combined score this season?

**Response:**
> The highest-scoring game of Syracuse's 2025 season was the opener vs. UAlbany on February 7, with a combined 30 goals. Combined scores for the top games: 30 — UAlbany (21–9), 28 — Cornell (18–10), 27 — Stanford 3/7 (14–13), 26 — Pitt (17–11), 25 — California (18–6).

**Ground truth:** UAlbany, 2/7/2025, 21-9, combined 30
**Verdict:** Correct
**Reasoning type:** Computed/reasoned over data — built a full ranked list rather than spot-checking one value, suggesting it processed all 19 rows.
**Notes:** Interesting contrast with Q3: same basic operation (add two numbers per row) but done correctly here across many rows, while a 10-value average failed. Worth reflecting on whether per-row addition is more reliable than aggregate averaging for this model, or whether it's question-framing dependent.

---

### Q5 — Season shooting percentage
**Prompt:**
> What was the team's season shooting percentage (total goals divided by total shots)?

**Response:**
> 43.6% — su_goals summed = 235, su_shots summed = 538. 235/538 = 0.436 ≈ 43.6%.

**Ground truth:** .437 (235/538 = 0.4368, rounds to 0.437)
**Verdict:** Minor error — correct inputs (235, 538 both exactly right), correct division, incorrect final rounding (truncated to 0.436 instead of rounding to 0.437)
**Notes:** Second instance of a "right data, wrong last digit" failure (see Q3). Suggests the model is reliable at retrieving/summing raw values but weaker at the final precision step of a calculation.

---

## Phase A: Reflection on Research Questions

**At what point did the model start getting things wrong?**
Not on data retrieval or single-value lookups (Q1, Q2, Q4 — all involving reading/counting/finding an extreme value were correct). It broke specifically on aggregate arithmetic requiring a final computed value — an average (Q3) and a rounded percentage (Q5). The dataset size and column complexity were identical across all five questions, so the failure tracks with the type of calculation, not the amount of data.

**Was it confidently wrong? Could you tell from the response alone?**
Yes, both times. No hedging language, no "approximately," no acknowledgment of uncertainty. Q3 in particular escalated in apparent confidence when asked to "verify via code" — it added a checkmark and "Final Answer" label to the same wrong number rather than flagging any doubt. Nothing in the response text itself would tip off a reader who hadn't already computed the ground truth.

**Did giving the model data in different formats change accuracy?**
Not tested yet — worth trying as a follow-up (e.g., paste a markdown table version of the same win-margin data and see if 5.5 comes out correctly, isolating whether the CSV parsing or the arithmetic is the point of failure).

**Did the model ever offer to write or run code? Was the code-derived answer more reliable?**
Yes, when asked directly. But the "code execution" was not real — it generated syntactically correct, logically correct pandas code, then fabricated a matching "Output" rather than running it. The code-derived answer was not more reliable; it was identically wrong, just presented with higher apparent confidence. This is arguably a more concerning failure mode than a plain wrong answer, since the surface presentation (code block + checkmark + "Final Answer") signals verification that never happened.

---

## Phase B: Derived Metrics, Judgment Questions, and Prompt Engineering
*(To be completed)*

### Metric Definitions

- **Most improved player:**
- **Game changer:**

### Judgment Q1
**Prompt:**
**Response:**
**Validation:**
**Verdict:**

---

### Coach Question
**Prompt:**
> "As a coach, if I wanted to win two more games this coming season, should I focus on offense or defense? And if so, what is the one player I should work with to be a game changer, and why?"

**Iteration 1 response:**

**What I changed and why:**

**Iteration 2 response:**

**Final validation against ground truth:**

**Did the recommendation survive?**
