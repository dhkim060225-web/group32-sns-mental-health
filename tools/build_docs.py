"""Build executive-summary.pdf (1 page) and technical-documentation.pdf (max 2 pages) from results.json."""
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

root = Path(__file__).resolve().parent.parent
R = json.loads((root / "results.json").read_text())
D = "/usr/share/fonts/truetype/dejavu/"
for name, f in [("Body", "DejaVuSansCondensed.ttf"), ("Body-B", "DejaVuSansCondensed-Bold.ttf"),
                ("Body-I", "DejaVuSansCondensed-Oblique.ttf"), ("Body-BI", "DejaVuSansCondensed-BoldOblique.ttf"),
                ("Head", "DejaVuSans-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, D + f))
addMapping("Body", 0, 0, "Body"); addMapping("Body", 1, 0, "Body-B")
addMapping("Body", 0, 1, "Body-I"); addMapping("Body", 1, 1, "Body-BI")

INK = colors.HexColor("#1C2140"); MUTED = colors.HexColor("#5A6080"); PINK = colors.HexColor("#D63A6E")
LINE = colors.HexColor("#D7DAE6"); SOFT = colors.HexColor("#F2F3F7"); TEAL = colors.HexColor("#2A8C80")

def m(v, d=2):
    s = f"{v:.{d}f}"
    return s.replace("-", "\u2212")

S, sl = R["slr"], R["split"]
het, med, ctry = R["heterogeneity"], R["mediation"], R["country"]
dml = {d["label"][0]: d for d in R["dml"]["overall"]}
lad = {l["label"]: l for l in R["ladder"]}
plat = {p["platform"]: p for p in R["platforms"]}


def styles(base):
    st = {
        "title": ParagraphStyle("title", fontName="Head", fontSize=base + 8.5, leading=base + 11, textColor=INK, spaceAfter=2),
        "sub": ParagraphStyle("sub", fontName="Body", fontSize=base - 0.3, leading=base + 2.2, textColor=MUTED, spaceAfter=0),
        "h": ParagraphStyle("h", fontName="Head", fontSize=base + 1.2, leading=base + 3.4, textColor=PINK, spaceBefore=5.5, spaceAfter=1.8),
        "p": ParagraphStyle("p", fontName="Body", fontSize=base, leading=base * 1.36, textColor=INK, spaceAfter=2.5),
        "b": ParagraphStyle("b", fontName="Body", fontSize=base, leading=base * 1.33, textColor=INK, leftIndent=9, bulletIndent=0, spaceAfter=1.3),
        "cell": ParagraphStyle("cell", fontName="Body", fontSize=base - 0.6, leading=(base - 0.6) * 1.3, textColor=INK),
        "cellh": ParagraphStyle("cellh", fontName="Body-B", fontSize=base - 0.6, leading=(base - 0.6) * 1.3, textColor=INK),
        "note": ParagraphStyle("note", fontName="Body-I", fontSize=base - 1.2, leading=(base - 1.2) * 1.3, textColor=MUTED, spaceBefore=2),
    }
    return st


def table(rows, widths, st, head=True, zebra=True):
    data = [[Paragraph(c, st["cellh"] if (head and i == 0) else st["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
            ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5)]
    if head:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), SOFT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK)]
    t.setStyle(TableStyle(cmds))
    return t


def footer_factory(label):
    def f(c, doc):
        c.saveState()
        c.setFont("Body", 7.2); c.setFillColor(MUTED)
        c.drawString(doc.leftMargin, 9 * mm, f"GROUP32  |  ACDT 2026 Semester 2, Hanyang University Intercollege  |  {label}")
        c.drawRightString(A4[0] - doc.rightMargin, 9 * mm, f"Page {doc.page}")
        c.setStrokeColor(PINK); c.setLineWidth(2.2)
        c.line(doc.leftMargin, A4[1] - 11 * mm, doc.leftMargin + 28 * mm, A4[1] - 11 * mm)
        c.restoreState()
    return f


TEAM = "Chae Seungrok, Im Junho, Jaemin Ok, Jeongwoo Park, Kim Dohyun, Park Jihu"
LINKS = 'Website: <a href="https://dhkim060225-web.github.io/group32-sns-mental-health/" color="#D63A6E">dhkim060225-web.github.io/group32-sns-mental-health</a><br/>Code: <a href="https://github.com/dhkim060225-web/group32-sns-mental-health" color="#D63A6E">github.com/dhkim060225-web/group32-sns-mental-health</a>'

# =================================================================== EXECUTIVE SUMMARY
def executive_summary(path, base=9.7):
    st = styles(base)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                            title="Executive Summary: Does scrolling more mean feeling worse?", author="GROUP32")
    W = A4[0] - 34 * mm
    s = []
    s.append(Paragraph("Does scrolling more mean feeling worse?", st["title"]))
    s.append(Paragraph("<b>Executive Summary</b>, ACDT Project 1: Revisit \u201cTackling the Conventional Wisdom\u201d", st["sub"]))
    s.append(Paragraph(f"GROUP32: {TEAM}", st["sub"]))
    s.append(Paragraph(LINKS, st["sub"]))

    s.append(Paragraph("The conventional wisdom and our question", st["h"]))
    s.append(Paragraph(
        "Many people believe that the more time students spend on social media, the worse they feel and the worse they do in class. "
        "We set out to test whether passive social media use lowers grades. The only usable dataset had no GPA and no measure of "
        "passive versus active use, so we asked: <b>is more daily social media use associated with a lower self-rated mental health "
        "score, and how much of that link survives other explanations?</b>", st["p"]))

    s.append(Paragraph("Data and approach", st["h"]))
    s.append(Paragraph(
        f"We used the <i>Students\u2019 Social Media Addiction</i> dataset (Kaggle): 705 self-reported survey responses, 13 variables. "
        f"After removing one duplicated row, <b>n = {R['meta']['n']}</b> students from <b>{R['meta']['n_countries']}</b> countries remained. "
        "We fitted a simple linear regression with a t-test and 95% confidence interval, validated it on 200 random 80/20 train/test "
        "splits, and then tested competing explanations: country clustering, platform type, sleep as a pathway, and double machine "
        "learning (DML) to remove measured background differences.", st["p"]))

    s.append(Paragraph("Key findings", st["h"]))
    rows = [["Finding", "Evidence"],
            ["Heavier use goes with lower mental health",
             f"{m(S['b1'])} points per extra hour (95% CI {m(S['ci'][0])} to {m(S['ci'][1])}; t = {m(S['t'],1)}, p &lt; 0.001); R<super>2</super> = {S['r2']:.2f}"],
            ["The model predicts unseen students as well as seen ones",
             f"Test R<super>2</super> {sl['r2_mean']:.2f} on average across 200 splits (range {sl['r2_min']:.2f}\u2013{sl['r2_max']:.2f}); error {sl['rmse_mean']:.2f} vs {sl['baseline_rmse_mean']:.2f} for guessing the mean. For one student the 95% prediction interval is about \u00b11.3 points."],
            ["Country explains more than hours do",
             f"Country alone explains {ctry['r2_country_only']*100:.0f}% of score variation ({ctry['r2_country_only_adj']*100:.0f}% adjusted). Within countries the slope is {m(ctry['slope_usage_country'])}; the country-clustered CI is {m(S['ci_cluster_country'][0])} to {m(S['ci_cluster_country'][1])}."],
            ["Platform type changes the relationship",
             f"Slopes range from {m(plat['WhatsApp']['slope'])} (WhatsApp) to {m(plat['Twitter']['slope'])} (Twitter); one common slope is rejected, F({het['platform']['df1']}, {het['platform']['df2']}) = {het['platform']['F']:.2f}, p &lt; 0.001."],
            ["Sleep carries part of the link",
             f"About {med['share']*100:.0f}% runs through sleep (indirect effect {m(med['indirect'])}, 95% CI {m(med['indirect_ci'][0])} to {m(med['indirect_ci'][1])})."],
            ["The link survives measured background",
             f"After DML removes age, gender, academic level, relationship status and country: {m(dml['A']['theta'])} per hour (95% CI {m(dml['A']['ci'][0])} to {m(dml['A']['ci'][1])})."]]
    s.append(table(rows, [W * 0.33, W * 0.67], st))

    s.append(Paragraph("What the data actually shows", st["h"]))
    s.append(Paragraph(
        "The conventional wisdom points in the right direction but tells the wrong story. Hours matter, roughly 0.6 points per hour "
        "even after removing measured background, but they are tangled up with where students live, how much they sleep and which "
        "platform they use. Because the data is cross-sectional and self-reported, it cannot tell us whether heavy use lowers mood or "
        "low mood drives heavy use, and unmeasured stress could drive both.", st["p"]))

    s.append(Paragraph("Limitations", st["h"]))
    s.append(Paragraph(
        "The sampling frame is undocumented, so results describe this dataset rather than all students. The data looks unusually "
        "clean: the addiction score correlates \u22120.95 with mental health, every user of three platforms gives the same score, and "
        "\u201csocial media hurts my studies\u201d answers jump from 0% to 100% across usage bands. Students are clustered by country, "
        "residuals are not normal, and stress and purpose of use were never measured. We treat the results as a strong teaching "
        "example, not as evidence for policy.", st["p"]))

    s.append(Paragraph("Recommendations", st["h"]))
    for t in ["<b>Counsellors:</b> use heavy use as a reason to start a conversation, not as a diagnosis; ask about sleep first.",
              "<b>Students:</b> notice what the hours are for; a group chat and an endless feed may not affect you the same way.",
              "<b>Researchers:</b> measure stress and purpose of use, follow the same students over time, and sample within countries."]:
        s.append(Paragraph(t, st["b"], bulletText="\u2022"))
    doc.build(s, onFirstPage=footer_factory("Executive Summary"), onLaterPages=footer_factory("Executive Summary"))


# =================================================================== TECHNICAL DOCUMENTATION
def technical(path, base=9.0):
    st = styles(base)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=15 * mm,
                            title="Technical Documentation: Does scrolling more mean feeling worse?", author="GROUP32")
    W = A4[0] - 30 * mm
    s = []
    s.append(Paragraph("Technical Documentation", st["title"]))
    s.append(Paragraph("ACDT Project 1, GROUP32: Is daily social media use associated with student mental health?", st["sub"]))
    s.append(Paragraph(LINKS, st["sub"]))

    s.append(Paragraph("1. Research question and hypotheses", st["h"]))
    s.append(Paragraph(
        "Outcome Y = Mental_Health_Score; treatment X = Avg_Daily_Usage_Hours. Model: Y = \u03b2<sub>0</sub> + \u03b2<sub>1</sub>X + \u03b5. "
        "H<sub>0</sub>: \u03b2<sub>1</sub> = 0; H<sub>1</sub>: \u03b2<sub>1</sub> \u2260 0 (two-sided; our earlier directional version was \u03b2<sub>1</sub> &lt; 0, "
        "controlling for academic level). <b>\u03b1 = 0.05</b>: a Type I error would justify blanket screen-time rules and wasted counselling time; "
        "a Type II error would leave struggling heavy users unflagged. Neither cost dominates, so we kept the conventional level.", st["p"]))

    s.append(Paragraph("2. Data and preprocessing", st["h"]))
    s.append(Paragraph(
        f"Source: <i>Students\u2019 Social Media Addiction</i> (Kaggle), 705 rows, 13 self-reported variables, no missing values. Recruitment "
        f"method and sampling frame are not documented (treated as a convenience sample). Student IDs {' and '.join(str(i) for i in R['meta']['duplicate_ids'])} "
        f"are identical in every answer; one was removed (<b>n = {R['meta']['n']}</b>). {R['meta']['n_countries']} countries, median "
        f"{R['meta']['country_median_n']:.0f} student per country. For DML, Country was recoded to the 10 largest countries plus \u201cOther\u201d.", st["p"]))
    rows = [["Variable", "Type / range", "Role", "Reason"],
            ["Avg_Daily_Usage_Hours", f"Continuous, {R['meta']['usage_min']}\u2013{R['meta']['usage_max']} h", "Treatment (X)", "The conventional wisdom is about time spent"],
            ["Mental_Health_Score", "Integer, observed 4\u20139 (1\u201310 scale)", "Outcome (Y)", "Replaces GPA, which is not in the data"],
            ["Age, Gender, Academic_Level, Relationship_Status", "Background", "Control", "Fixed before usage; can confound, not caused by usage"],
            ["Country", "110 categories", "Control / cluster", "Strongest confounder; breaks independence"],
            ["Most_Used_Platform", "12 categories", "Moderator", "Proxy for type of use (our original idea)"],
            ["Sleep_Hours_Per_Night", "Continuous", "Mediator", "Usage can reduce sleep; not controlled for the total effect"],
            ["Addicted_Score, Conflicts_Over_Social_Media", "Scores / counts", "Not controlled", "Likely consequences of usage (bad controls)"],
            ["Affects_Academic_Performance", "Yes / No", "Secondary outcome", "Closest proxy for the original GPA question"]]
    s.append(table(rows, [W * 0.27, W * 0.22, W * 0.14, W * 0.37], st))

    s.append(Paragraph("3. Methods", st["h"]))
    rows = [["Framework level", "Method", "Implementation details"],
            ["Sampling distribution / Inference", "OLS, t-test, 95% CI",
             f"df = {S['dof']}, t* = {S['tcrit']:.3f}. Independence violated by country clustering, so CR1 cluster-robust SEs with 110 clusters are also reported. Residual normality: Shapiro\u2013Wilk p &lt; 0.001; with n = 704 the CLT supports t-based inference."],
            ["Prediction", "Train/test validation",
             "200 random 80/20 splits (scikit-learn, seeds 0\u2013199); metrics: test R<super>2</super>, RMSE, vs a train-mean baseline. Prediction intervals: \u0177 \u00b1 t*\u00b7s\u221a(1 + 1/n + (x\u2212x\u0304)<super>2</super>/S<sub>xx</sub>)."],
            ["Inference (heterogeneity)", "Per-platform OLS; nested F-test",
             "Bootstrap CIs (2,000 resamples) for slope and R<super>2</super>. F-test: platform-specific slopes vs one common slope, both with platform intercepts (platforms with n \u2265 10 and varying outcome)."],
            ["Reasoning", "Country fixed effects; mediation",
             "110 country dummies. Sleep mediation by product of coefficients a\u00b7b, 1,000 bootstrap resamples."],
            ["Reasoning", "Double/debiased ML (partially linear model)",
             "Y = \u03b8X + g(W) + \u03b5, X = m(W) + v. Random forests (100 trees, min leaf 5; 8 in subgroups) estimate g and m with 5-fold cross-fitting; \u03b8 from residual-on-residual regression; 3 repetitions, median aggregation; influence-function SE. Covariate sets A\u2013D below."]]
    s.append(table(rows, [W * 0.19, W * 0.2, W * 0.61], st))

    res_head = Paragraph("4. Results", st["h"])
    def ci(e, se): return f"{m(e - 1.96 * se)} to {m(e + 1.96 * se)}"
    rows = [["Model", "Estimate per hour", "95% CI", "R<super>2</super>"],
            ["OLS: hours only", m(lad["Hours only"]["est"], 3), f"{m(S['ci'][0])} to {m(S['ci'][1])} (clustered: {m(S['ci_cluster_country'][0])} to {m(S['ci_cluster_country'][1])})", f"{lad['Hours only']['r2']:.3f}"],
            ["OLS: + academic level", m(lad["+ academic level"]["est"], 3), ci(lad["+ academic level"]["est"], lad["+ academic level"]["se"]), f"{lad['+ academic level']['r2']:.3f}"],
            ["OLS: + sleep (direct effect)", m(lad["+ sleep"]["est"], 3), ci(lad["+ sleep"]["est"], lad["+ sleep"]["se"]), f"{lad['+ sleep']['r2']:.3f}"],
            ["OLS: + country fixed effects", m(lad["+ country"]["est"], 3), ci(lad["+ country"]["est"], lad["+ country"]["se"]), f"{lad['+ country']['r2']:.3f}"],
            ["OLS: + country + platform", m(lad["+ country + platform"]["est"], 3), ci(lad["+ country + platform"]["est"], lad["+ country + platform"]["se"]), f"{lad['+ country + platform']['r2']:.3f}"],
            ["OLS: + sleep + addiction + conflicts", m(lad["+ sleep + addiction + conflicts"]["est"], 3), ci(lad["+ sleep + addiction + conflicts"]["est"], lad["+ sleep + addiction + conflicts"]["se"]), f"{lad['+ sleep + addiction + conflicts']['r2']:.3f}"]]
    for k, lab in [("A", "DML A: background (age, gender, level, relationship, country)"), ("B", "DML B: A + platform"),
                   ("C", "DML C: A + sleep"), ("D", "DML D: A + addiction + conflicts")]:
        rows.append([lab, m(dml[k]["theta"], 3), f"{m(dml[k]['ci'][0])} to {m(dml[k]['ci'][1])}", "\u2013"])
    s.append(KeepTogether([res_head, table(rows, [W * 0.45, W * 0.15, W * 0.3, W * 0.1], st)]))
    g = R["dml"]["groups"]
    gtxt = ", ".join(f"{d['value']} {m(d['theta'])}" for d in g if not d["degenerate"])
    s.append(Paragraph(
        f"Validation: mean test R<super>2</super> {sl['r2_mean']:.3f} (range {sl['r2_min']:.3f}\u2013{sl['r2_max']:.3f}), RMSE {sl['rmse_mean']:.3f} vs baseline {sl['baseline_rmse_mean']:.3f}. "
        f"Platform slope heterogeneity: F({het['platform']['df1']}, {het['platform']['df2']}) = {het['platform']['F']:.2f}, p = {het['platform']['p']:.4f}; "
        f"academic level p = {het['academic_level']['p']:.2f}; gender p = {het['gender']['p']:.2f}. "
        f"Mediation: a = {m(med['a'],3)}, b = {med['b']:.3f}, indirect = {m(med['indirect'],3)} (95% CI {m(med['indirect_ci'][0],3)} to {m(med['indirect_ci'][1],3)}), {med['share']*100:.1f}% of total. "
        f"DML subgroups: {gtxt}; WhatsApp could not be estimated because scores are constant within its countries. "
        f"Secondary outcome: students reporting academic harm use {R['academic']['usage_yes']:.2f} vs {R['academic']['usage_no']:.2f} h (Welch t = {R['academic']['welch_t']:.1f}, p &lt; 0.001).", st["p"]))
    s.append(Paragraph(
        "Interpretation of D: controlling for addiction and conflicts removes the effect because both are probably downstream of usage "
        "and strongly tied to the outcome (r = \u22120.95 for addiction). We report D only to show why such variables must not be controlled.", st["note"]))

    s.append(Paragraph("5. Limitations and threats to validity", st["h"]))
    for t in ["<b>External validity:</b> undocumented, non-random sample; half of the 110 countries contribute one student.",
              "<b>Internal validity:</b> cross-sectional self-reports; reverse causation and unmeasured confounding (stress, workload, purpose of use) remain. DML adjusts only for measured covariates; no valid instrument was available.",
              f"<b>Data quality:</b> scores identical for all users of LINE, KakaoTalk and VKontakte and within {ctry['share_constant']*100:.0f}% of countries with n \u2265 2; academic-impact answers move from 0% to 100% across usage bands; outcome is ordinal with six observed values.",
              "<b>Model assumptions:</b> non-normal residuals and clustered observations; addressed with large-sample inference and cluster-robust SEs, not eliminated."]:
        s.append(Paragraph(t, st["b"], bulletText="\u2022"))

    s.append(Paragraph("6. Reproducibility", st["h"]))
    s.append(Paragraph(
        "Repository files: <b>analysis.py</b> (all computations, writes results.json), <b>results.json</b>, <b>data/Students_Social_Media_Addiction.csv</b>, "
        "<b>index.html</b> (data story website), <b>tools/</b> (page and document builders). Environment: Python 3 with pandas, numpy, scipy, scikit-learn. "
        "Run <font name='Body-B'>python analysis.py</font> (about 1\u20132 minutes), then <font name='Body-B'>python tools/build_page.py</font> and "
        "<font name='Body-B'>python tools/build_docs.py</font>. All random procedures use fixed seeds.", st["p"]))
    doc.build(s, onFirstPage=footer_factory("Technical Documentation"), onLaterPages=footer_factory("Technical Documentation"))


if __name__ == "__main__":
    executive_summary(root / "executive-summary.pdf")
    technical(root / "technical-documentation.pdf")
    print("built executive-summary.pdf and technical-documentation.pdf")
