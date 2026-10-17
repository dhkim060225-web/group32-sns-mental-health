# Does scrolling more mean feeling worse?

Website: https://dhkim060225-web.github.io/group32-sns-mental-health/  
Repository: https://github.com/dhkim060225-web/group32-sns-mental-health

**GROUP32 · ACDT 2026 Semester 2 · Project 1: Revisit "Tackling the Conventional Wisdom"**

A data story website (Option 4) testing the conventional wisdom that more social media use means poorer student mental health.

## Files
| Path | What it is |
|---|---|
| `index.html` | The data story website (self-contained; all results are embedded) |
| `analysis.py` | Reproduces every number on the site and writes `results.json` |
| `results.json` | All computed results |
| `data/Students_Social_Media_Addiction.csv` | Raw data (Kaggle, 705 rows, 13 variables) |
| `executive-summary.pdf`, `technical-documentation.pdf` | 1-page summary and 2-page technical documentation |
| `three-system-maps-report.pdf` | Map A, B, C comparison and justification document (3 pages) |
| `tools/` | Rebuild `index.html` (`build_page.py`) and the three PDFs (`build_docs.py`, `build_maps_report.py`) |

## Reproduce
```bash
pip install pandas numpy scipy scikit-learn
python analysis.py                  # a few minutes (double machine learning, repeated splits)
python tools/build_page.py          # refresh index.html with the new results.json
python tools/build_docs.py          # executive summary (1 page) and technical documentation (2 pages)
python tools/build_maps_report.py   # three system maps comparison report
```

## Publish with GitHub Pages
1. Create a public repository (e.g. `group32-sns-mental-health`) and upload all files, keeping the folder structure.
2. Settings → Pages → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → Save.
3. The site appears at `https://<account>.github.io/<repository>/` within a few minutes.

## Methods in one paragraph
Simple linear regression (Mental_Health_Score ~ Avg_Daily_Usage_Hours) with a two-sided t-test and 95% CI; country-clustered (CR1) standard errors for the pooled and within-country slopes; 200 random 80/20 train/test splits plus 200 repeats of 5-fold splits that hold out whole countries; per-platform regressions with 2,000-resample bootstrap intervals, an F-test for equal slopes and a Bonferroni check; Spearman rank correlation for the ordinal outcome; sleep mediation with bootstrap CI; an OLS model ladder; double/debiased machine learning (partially linear model, random forests, 5-fold cross-fitting, 3 repetitions); and a robustness value for unmeasured confounding. One duplicated row (Student IDs 242 and 274) was removed, leaving n = 704. Re-running `analysis.py` from a clean copy reproduces `results.json` exactly.

## Data source
Students' Social Media Addiction dataset, Kaggle (705 responses, 13 self-reported variables). Dataset description mirrored at https://baselight.app/u/kaggle/dataset/rehan497_students_social_media_addiction. The recruitment method and consent process are not documented; the file is de-identified.

## References
- Chernozhukov, V., et al. (2018). Double/debiased machine learning for treatment and structural parameters. *The Econometrics Journal, 21*(1), C1–C68.
- Cinelli, C., & Hazlett, C. (2020). Making sense of sensitivity: Extending omitted variable bias. *Journal of the Royal Statistical Society: Series B, 82*(1), 39–67.
- Hale, L., & Guan, S. (2015). Screen time and sleep among school-aged children and adolescents: A systematic literature review. *Sleep Medicine Reviews, 21*, 50–58.
- Orben, A., & Przybylski, A. K. (2019). The association between adolescent well-being and digital technology use. *Nature Human Behaviour, 3*(2), 173–182.
