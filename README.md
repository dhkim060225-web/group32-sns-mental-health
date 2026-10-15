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
| `three-system-maps-report.pdf` | Map A, B, C comparison and justification document (2 pages) |
| `tools/` | Rebuild `index.html` (`build_page.py`) and the two PDFs (`build_docs.py`, `build_maps_report.py`) |

## Reproduce
```bash
pip install pandas numpy scipy scikit-learn
python analysis.py            # about 1-2 minutes (double machine learning)
python tools/build_page.py    # refresh index.html with the new results.json
```

## Publish with GitHub Pages
1. Create a public repository (e.g. `group32-sns-mental-health`) and upload all files, keeping the folder structure.
2. Settings → Pages → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → Save.
3. The site appears at `https://<account>.github.io/<repository>/` within a few minutes.

## Before final submission (team to do)
- [ ] Fill in the "How we used AI" box in `tools/template.html` (then rebuild) following the Intercollege AI policy.
- [ ] Confirm the AI-assistance statement matches what the team actually did (website Process section and Technical Documentation), then rebuild.
- [ ] If a video pitch is required, upload it (unlisted, 720p+, captions) and add the link.
- [ ] Check every number against your own run of `analysis.py`.

## Methods in one paragraph
Simple linear regression (Mental_Health_Score ~ Avg_Daily_Usage_Hours), 95% CI and t-test; country-clustered (CR1) standard errors; 200 random 80/20 train/test splits; per-platform regressions with 2,000-resample bootstrap intervals and an F-test for equal slopes; sleep mediation with bootstrap CI; OLS model ladder; double/debiased machine learning (partially linear model, random forests, 5-fold cross-fitting, 3 repetitions). One duplicated row (Student IDs 242 and 274) was removed, leaving n = 704.
