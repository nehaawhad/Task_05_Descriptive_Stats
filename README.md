# Task 05: Descriptive Statistics and Large Language Models
### From Ground Truth to LLM Judgment — 2025 Syracuse Women's Lacrosse Season

## Overview

This project tests whether a large language model (Microsoft Copilot) can be trusted to reason
accurately about real, structured data — first on simple factual questions, then on
judgment questions that require an explicit, defensible metric before they can be answered at
all. Every claim the model made was checked against a ground-truth answer key computed
independently with Python/pandas, cross-validated with a second, library-free implementation.

The short version: Copilot was reliable on direct lookups and single-value extremes, but
repeatedly failed at final-step arithmetic (an average, a rounded percentage) and — most
seriously — at reading which column was which when a calculation spanned two fields. That
column-confusion error surfaced three separate times across the project, including inside the
model's single most consequential output: its recommendation for which player a coach should
develop into a "game changer." The full arc of that failure, and how it was eventually corrected,
is documented in `prompt_log.md`.

## Dataset

**Source:** [Syracuse University Women's Lacrosse Statistics](https://cuse.com/sports/womens-lacrosse/stats/2025/) (official athletics site)

**Season used:** 2025 (19 games, 32 rostered players)

This repository does **not** include the dataset files, per assignment requirements. To
reproduce this project:

1. Go to the source URL above.
2. Under the "Players" tab, copy the full player stats table into a CSV with these columns:
   `number, player, gp, gs, g, a, pts, sh, sh_pct, sog, sog_pct, gwg, fpg, fps, gb, to, ct, dc, fouls, rc, yc, gc`
   Save as `data/players_2025.csv`.
3. Under the "Team" → game-by-game tab, copy the full schedule/results table into a CSV with these columns:
   `date, opponent, result, su_score, opp_score, su_goals, su_assists, su_pts, su_shots, su_sh_pct, su_sog, su_sog_pct, su_gwg, su_fpg, su_fps, su_gb, su_to, su_ct, su_dc`
   Save as `data/games_2025.csv`.

Column glossary (from the source site): gp/gs = games played/started, g = goals, a = assists,
pts = points, sh = shots, sog = shots on goal, gwg = game-winning goals, fpg/fps = free-position
goals/shots, gb = ground balls, to = turnovers, ct = caused turnovers, dc = draw controls.

## Reproducing the Ground Truth

```bash
pip install pandas
cd scripts
python ground_truth.py
```

This computes descriptive statistics two independent ways — pandas (primary) and pure Python
with no libraries (cross-check) — and prints both side by side with a match/mismatch flag for
each value. All cross-checked values matched on every run. This answer key is what every
model response in `prompt_log.md` was validated against.

**Ground truth highlights (2025 season):**
| Stat | Value |
|---|---|
| Games played | 19 (10 W, 9 L) |
| Top goal scorer | Emma Muchnick — 34 goals |
| Top points player | Emma Ward — 76 points |
| Avg margin of victory | +5.5 |
| Avg margin of defeat | -4.56 |
| Highest combined-score game | UAlbany, 2/7/2025 (21-9, combined 30) |
| Season shooting % | .437 |
| Team leader, GB + caused turnovers | Coco Vandiver (34 GB + 40 CT = 74) |

## Experiment Narrative

### Phase A — Baseline Factual Q&A

Five factual questions were asked of Copilot, each checkable directly against the ground truth
table above:

1. **Games played / record** — Correct. Copilot counted rows and correctly separated two
   Stanford games and two Yale games by date rather than merging them.
2. **Top goal scorer** — Correct. Correctly distinguished "most goals" (Muchnick, 34) from
   "most points" (Ward, 76) — a distinction the dataset deliberately makes possible to conflate.
3. **Average margin of victory** — **Incorrect.** Copilot listed all ten individual win margins
   correctly (12, 6, 8, 1, 6, 2, 1, 1, 12, 6) but added them wrong, reporting 6.8 instead of the
   correct 5.5. When explicitly asked to verify this by writing and running code, it produced a
   fully correct pandas script — and then reported a fabricated "Output: 6.8," identical to its
   original wrong answer, styled with a checkmark and "Final Answer" label. The code was never
   actually executed.
4. **Highest combined-score game** — Correct, including a fully accurate ranked list of the
   next four highest games.
5. **Season shooting percentage** — Minor error. Correct inputs (235 goals, 538 shots) and
   correct division, but rounded to 43.6% instead of the correct 43.7%.

**Pattern:** Copilot was reliable at retrieval and at finding extremes across many rows, but
broke specifically at the final arithmetic step of an aggregate calculation — and, when caught
and asked to prove its work with code, fabricated a matching "execution output" rather than
actually running anything or admitting the discrepancy.

### Phase B — Metric Design and the Coach Question

**Metric defined:** a "game changer" is a player with 10+ games played who ranks in the team's
top 5 in total points AND top 5 in combined ground balls + caused turnovers (gb + ct) — requiring
contribution on both sides of the ball, not just scoring. Computed independently before asking
the model: **Emma Muchnick and Alexa Vogelman** both qualify.

Asked to apply this exact definition, Copilot got the offense side right (correct top-5 points
list) but the defense side wrong — it misread two players' rows, pulling `dc` (draw controls) and
`fouls` values in place of `gb`/`ct` for one player, and `to` (turnovers) in place of `gb` for
another. Its conclusion — "no players qualify" — was the opposite of the true answer.

Three rounds of prompt engineering were tried to fix this:
1. **Plain re-ask** — no change.
2. **Explicit column-binding instruction** ("GB means the `gb` column... do not use `dc`, `to`,
   or `fouls`") — no improvement. Copilot repeated the identical wrong numbers while explicitly
   claiming to have followed the new instruction.
3. **Forced literal row quoting** before any computation — partially effective. This fixed the
   `gb` misread but revealed a narrower, consistent error: substituting `to` for `ct` on both
   players, every time.

**None of the three techniques fully resolved the underlying error through re-derivation** — the
only thing that worked was supplying pre-verified numbers directly in the prompt (see below).

**The coach question** — the assignment's central advisory prompt — surfaced this same failure
at the highest stakes in the project. Asked "should I focus on offense or defense, and which one
player should I develop into a game changer," Copilot's offense-vs-defense analysis was fully
correct (verified independently: 13.2 goals allowed per game in losses, correctly identified five
winnable one/two-possession losses). But its player recommendation — **Meghan Rode** — was based
on the same fabricated `gb`/`ct` reading: it quoted her real row verbatim, then still called her
draw controls (75) and fouls (17) her ground balls and caused turnovers. Rode's actual GB+CT is
1 — she is near the bottom of the roster on both metrics, not the "clearest defensive anchor" as
claimed.

**Resolution:** supplying the verified top-5 GB+CT table directly in the follow-up prompt (rather
than asking Copilot to compute or re-verify it) produced a fully validated recommendation:
**Coco Vandiver**, the team's actual leader in both ground balls and caused turnovers. This
recommendation held up under independent validation, though a few qualitative claims in its
explanation (e.g., "conference-level elite," "reduces scoring by 3-5 goals per game") were
confident-sounding elaborations not derived from anything in the two CSVs.

## Reflections

**Where I'd trust this model:** direct lookups, sorting/ranking across many rows, and reasoning
that stays within a single, clearly-labeled column. It never got a name, a count, or a max/min
wrong across the entire project.

**Where I would always verify myself:** anything requiring the model to align values across
multiple adjacent columns (it repeatedly and specifically confused `to`↔`ct` and `dc`/`fouls`↔`gb`/`ct`,
even after being told explicitly which column meant what), any aggregate arithmetic beyond simple
per-row addition, and any claim that it had verified something with code — in this project, a
claimed "code execution" was fabricated rather than real, which is arguably more dangerous than a
plain wrong answer because it looks more rigorous.

**Most effective prompt-engineering technique:** supplying pre-verified numbers directly in the
prompt and asking the model to reason over them, rather than asking it to extract and compute
those numbers itself. This was the only approach, across every technique tried, that reliably
fixed an error.

**Biggest finding overall:** an unresolved data-reading error does not stay contained to the
question where it is first caught — the same column confusion first found in a mid-level metric
question resurfaced, unprompted, inside the single highest-stakes recommendation of the entire
project. A confident, well-sourced-looking answer (complete with a verbatim CSV quote) does not
mean the answer is correct; it only survived validation once verified numbers were fed in
directly rather than left for the model to derive.

## Files

- `data/` — dataset CSVs (not committed; see reproduction instructions above)
- `scripts/ground_truth.py` — descriptive statistics computed two independent ways, with an
  automatic cross-check
- `prompt_log.md` — full prompt-and-response log for both phases, including model/version,
  exact prompts, exact responses, verdicts, and root-cause notes for every discrepancy found
