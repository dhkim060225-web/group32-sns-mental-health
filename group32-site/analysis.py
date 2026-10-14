"""
GROUP32 - ACDT Project 1: Revisit "Tackling the Conventional Wisdom"
Does more daily social media use go with poorer student mental health?

Reproduces every number shown on the data story website and writes results.json.
Requirements: pandas, numpy, scipy, scikit-learn  (no statsmodels needed)
Usage:        python analysis.py  [path/to/Students_Social_Media_Addiction.csv]
"""
import json, sys
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split, KFold
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/Students_Social_Media_Addiction.csv"
X, Y, S = "Avg_Daily_Usage_Hours", "Mental_Health_Score", "Sleep_Hours_Per_Night"
OUT = {}

# ------------------------------------------------------------------ 1. Data
raw = pd.read_csv(CSV)
dup_mask = raw.drop(columns="Student_ID").duplicated(keep=False)
df = raw.drop_duplicates(subset=[c for c in raw.columns if c != "Student_ID"]).reset_index(drop=True)
n = len(df)
OUT["meta"] = {"n_raw": len(raw), "n": n, "n_vars": raw.shape[1],
               "duplicate_ids": raw.loc[dup_mask, "Student_ID"].tolist(),
               "n_countries": int(df.Country.nunique()),
               "country_median_n": float(df.Country.value_counts().median()),
               "usage_min": float(df[X].min()), "usage_max": float(df[X].max()),
               "mental_values": sorted(int(v) for v in df[Y].unique())}
OUT["desc"] = {c: {"mean": round(df[c].mean(), 3), "sd": round(df[c].std(), 3)}
               for c in [X, Y, S, "Addicted_Score", "Conflicts_Over_Social_Media", "Age"]}
num_cols = ["Age", X, S, Y, "Conflicts_Over_Social_Media", "Addicted_Score"]
OUT["corr"] = {"cols": num_cols, "r": df[num_cols].corr().round(2).values.tolist()}


def ols(A, y):
    """OLS with classic SE. A must include an intercept column."""
    A = np.asarray(A, float); y = np.asarray(y, float)
    XtX_inv = np.linalg.inv(A.T @ A)
    b = XtX_inv @ A.T @ y
    res = y - A @ b
    dof = len(y) - A.shape[1]
    s2 = (res ** 2).sum() / dof
    se = np.sqrt(np.diag(s2 * XtX_inv))
    r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return dict(b=b, se=se, res=res, s=np.sqrt(s2), dof=dof, r2=r2, XtX_inv=XtX_inv)


def dummies(cols, data=None):
    data = df if data is None else data
    return pd.get_dummies(data[cols], columns=cols, drop_first=True).astype(float).values


one = np.ones((n, 1))
x = df[X].values; y = df[Y].values.astype(float)

# ------------------------------------------------------------------ 2. Simple linear regression (Level 4 + 5)
m = ols(np.column_stack([one, x]), y)
b0, b1 = m["b"]; se1 = m["se"][1]
t1 = b1 / se1; p1 = 2 * stats.t.sf(abs(t1), m["dof"]); tcrit = stats.t.ppf(0.975, m["dof"])
# cluster-robust (CR1) SE by country: observations within a country are not independent
A = np.column_stack([one, x]); g = df.Country.values
meat = np.zeros((2, 2))
for c in np.unique(g):
    idx = g == c
    u = A[idx].T @ m["res"][idx]
    meat += np.outer(u, u)
G = len(np.unique(g)); k = 2
cr = m["XtX_inv"] @ meat @ m["XtX_inv"] * (G / (G - 1)) * ((n - 1) / (n - k))
se1_cl = float(np.sqrt(cr[1, 1]))
OUT["slr"] = {"b0": b0, "b1": b1, "se": se1, "t": t1, "p": p1, "dof": m["dof"],
              "ci": [b1 - tcrit * se1, b1 + tcrit * se1], "tcrit": tcrit,
              "r2": m["r2"], "s": m["s"], "xbar": x.mean(), "sxx": ((x - x.mean()) ** 2).sum(),
              "se_cluster_country": se1_cl,
              "ci_cluster_country": [b1 - 1.96 * se1_cl, b1 + 1.96 * se1_cl],
              "pred_at_mean": b0 + b1 * x.mean(), "pred_at_6": b0 + b1 * 6}
# residual normality (reported as a limitation)
OUT["slr"]["shapiro_p"] = float(stats.shapiro(m["res"]).pvalue)

# Two-predictor model for the calculator: Mental ~ Usage + Sleep
m2 = ols(np.column_stack([one, x, df[S].values]), y)
OUT["mlr_sleep"] = {"b": m2["b"].tolist(), "se": m2["se"].tolist(), "r2": m2["r2"], "s": m2["s"],
                    "dof": m2["dof"], "XtX_inv": m2["XtX_inv"].tolist()}

# ------------------------------------------------------------------ 3. Train/test validation (Level 5)
r2s, rmses, base = [], [], []
for seed in range(200):
    tr, te = train_test_split(df, test_size=0.2, random_state=seed)
    lr = LinearRegression().fit(tr[[X]], tr[Y]); p = lr.predict(te[[X]])
    r2s.append(r2_score(te[Y], p)); rmses.append(mean_squared_error(te[Y], p) ** 0.5)
    base.append(mean_squared_error(te[Y], np.full(len(te), tr[Y].mean())) ** 0.5)
tr, te = train_test_split(df, test_size=0.2, random_state=42)
lr = LinearRegression().fit(tr[[X]], tr[Y]); p = lr.predict(te[[X]])
OUT["split"] = {"r2": [round(v, 4) for v in r2s], "rmse": [round(v, 4) for v in rmses],
                "r2_mean": float(np.mean(r2s)), "r2_min": float(np.min(r2s)), "r2_max": float(np.max(r2s)),
                "rmse_mean": float(np.mean(rmses)), "baseline_rmse_mean": float(np.mean(base)),
                "seed42": {"r2": r2_score(te[Y], p), "rmse": mean_squared_error(te[Y], p) ** 0.5,
                           "n_train": len(tr), "n_test": len(te)}}

# ------------------------------------------------------------------ 4. By platform (type of SNS)
rng = np.random.default_rng(0)
plat = []
for name, d in df.groupby("Most_Used_Platform"):
    row = {"platform": name, "n": len(d), "usage_mean": d[X].mean(), "usage_sd": d[X].std(),
           "mental_mean": d[Y].mean(), "aff_yes": (d.Affects_Academic_Performance == "Yes").mean(),
           "mental_constant": bool(d[Y].nunique() == 1)}
    if d[Y].nunique() > 1 and d[X].nunique() > 2:
        r = stats.linregress(d[X], d[Y])
        bs_s, bs_r = [], []
        for _ in range(2000):
            s_ = d.sample(len(d), replace=True, random_state=int(rng.integers(1e9)))
            if s_[X].nunique() < 3 or s_[Y].nunique() < 2:
                continue
            q = stats.linregress(s_[X], s_[Y]); bs_s.append(q.slope); bs_r.append(q.rvalue ** 2)
        row.update(slope=r.slope, r2=r.rvalue ** 2, p=r.pvalue,
                   slope_ci=np.percentile(bs_s, [2.5, 97.5]).tolist(),
                   r2_ci=np.percentile(bs_r, [2.5, 97.5]).tolist())
    plat.append(row)
OUT["platforms"] = sorted(plat, key=lambda r: -r["n"])


def slope_heterogeneity(col, min_n=10):
    """F-test: group-specific slopes vs one common slope (both with group intercepts)."""
    keep = df[col].map(df[col].value_counts()) >= min_n
    d = df[keep]
    yy = d[Y].values.astype(float); xx = d[X].values
    if col == "Most_Used_Platform":  # groups with constant outcome carry no slope information
        ok = d.groupby(col)[Y].transform("nunique") > 1
        d, yy, xx = d[ok], yy[ok.values], xx[ok.values]
    P = pd.get_dummies(d[col]).astype(float).values
    A0 = np.column_stack([P, xx]); A1 = np.column_stack([P, P * xx[:, None]])
    rss = lambda A: ((yy - A @ np.linalg.lstsq(A, yy, rcond=None)[0]) ** 2).sum()
    r0, r1 = rss(A0), rss(A1); k0, k1 = A0.shape[1], A1.shape[1]; nn = len(yy)
    F = ((r0 - r1) / (k1 - k0)) / (r1 / (nn - k1))
    return {"F": F, "df1": k1 - k0, "df2": nn - k1, "p": stats.f.sf(F, k1 - k0, nn - k1)}


OUT["heterogeneity"] = {"platform": slope_heterogeneity("Most_Used_Platform"),
                        "academic_level": slope_heterogeneity("Academic_Level"),
                        "gender": slope_heterogeneity("Gender")}
OUT["groups"] = {}
for col in ["Academic_Level", "Gender"]:
    OUT["groups"][col] = []
    for gname, d in df.groupby(col):
        r = stats.linregress(d[X], d[Y])
        OUT["groups"][col].append({"group": gname, "n": len(d), "slope": r.slope, "r2": r.rvalue ** 2})

# ------------------------------------------------------------------ 5. Country clustering
Dc = dummies(["Country"])
rc = ols(np.column_stack([one, Dc]), y)
kc = Dc.shape[1] + 1
r2_adj = 1 - (1 - rc["r2"]) * (n - 1) / (n - kc)
m_uc = ols(np.column_stack([one, x, Dc]), y)
m_ucp = ols(np.column_stack([one, x, Dc, dummies(["Most_Used_Platform"])]), y)
wa = df[df.Most_Used_Platform == "WhatsApp"].groupby("Country").agg(n=(Y, "size"), usage=(X, "mean"),
                                                                   mental_mean=(Y, "mean"), mental_sd=(Y, "std"))
top = df.groupby("Country").agg(n=(Y, "size"), usage=(X, "mean"), mental=(Y, "mean"),
                                 mental_sd=(Y, "std")).query("n >= 20").sort_values("usage")
OUT["country"] = {"r2_country_only": rc["r2"], "r2_country_only_adj": r2_adj,
                  "r2_usage_country": m_uc["r2"], "slope_usage_country": m_uc["b"][1], "se_usage_country": m_uc["se"][1],
                  "r2_usage_country_platform": m_ucp["r2"], "slope_usage_country_platform": m_ucp["b"][1],
                  "se_usage_country_platform": m_ucp["se"][1],
                  "whatsapp_by_country": wa.reset_index().round(2).fillna(0).to_dict("records"),
                  "large_countries": top.reset_index().round(2).fillna(0).to_dict("records"),
                  "share_constant": float((df.groupby("Country")[Y].agg(["size", "std"]).query("size >= 2")["std"] == 0).mean())}

# ------------------------------------------------------------------ 6. Sleep as a mediator (usage -> sleep -> mental)
def mediation(d):
    a = stats.linregress(d[X], d[S]).slope
    mm = ols(np.column_stack([np.ones(len(d)), d[X].values, d[S].values]), d[Y].values)
    tot = stats.linregress(d[X], d[Y]).slope
    return a, mm["b"][2], mm["b"][1], tot


a, bb, direct, total = mediation(df)
boot = []
for i in range(1000):
    s_ = df.sample(n, replace=True, random_state=i)
    aa, bbb, _, _ = mediation(s_); boot.append(aa * bbb)
OUT["mediation"] = {"a": a, "b": bb, "indirect": a * bb, "direct": direct, "total": total,
                    "indirect_ci": np.percentile(boot, [2.5, 97.5]).tolist(), "share": a * bb / total}

# ------------------------------------------------------------------ 7. Back to Week 2: perceived academic impact
yes = df[df.Affects_Academic_Performance == "Yes"]; no = df[df.Affects_Academic_Performance == "No"]
tt = stats.ttest_ind(yes[X], no[X], equal_var=False)
bins = [0, 3, 4, 5, 6, 7, 9]
labs = ["<3h", "3-4h", "4-5h", "5-6h", "6-7h", "7h+"]
cut = pd.cut(df[X], bins, labels=labs, right=False)
OUT["academic"] = {"n_yes": len(yes), "n_no": len(no),
                   "usage_yes": yes[X].mean(), "usage_no": no[X].mean(),
                   "mental_yes": yes[Y].mean(), "mental_no": no[Y].mean(),
                   "welch_t": tt.statistic, "welch_p": tt.pvalue,
                   "by_bin": [{"bin": str(b), "n": int((cut == b).sum()),
                               "yes_share": float((df.Affects_Academic_Performance[cut == b] == "Yes").mean())}
                              for b in labs]}

# ------------------------------------------------------------------ 8. Where the model is most wrong (W4 lecture task)
df["_pred"] = b0 + b1 * x; df["_res"] = y - df["_pred"]
worst = df.reindex(df["_res"].abs().sort_values(ascending=False).index).head(6)
OUT["outliers"] = worst[["Student_ID", "Age", "Gender", "Academic_Level", "Country", X, "Most_Used_Platform",
                         S, Y, "_pred", "_res"]].round(2).rename(columns={"_pred": "pred", "_res": "res"}).to_dict("records")

# ------------------------------------------------------------------ 9. Model ladder (OLS)
ladder = []
def add(label, A, kind="OLS", note=""):
    mm = ols(A, y); ladder.append({"label": label, "est": mm["b"][1], "se": mm["se"][1], "kind": kind,
                                   "r2": mm["r2"], "note": note})
add("Hours only", np.column_stack([one, x]))
add("+ academic level", np.column_stack([one, x, dummies(["Academic_Level"])]))
add("+ sleep", np.column_stack([one, x, df[S].values]), note="sleep may be a mediator")
add("+ country", np.column_stack([one, x, Dc]))
add("+ country + platform", np.column_stack([one, x, Dc, dummies(["Most_Used_Platform"])]))
add("+ sleep + addiction + conflicts", np.column_stack([one, x, df[S].values, df[["Addicted_Score", "Conflicts_Over_Social_Media"]].values]),
    note="bad controls: likely consequences of usage")
OUT["ladder"] = ladder

# ------------------------------------------------------------------ 10. Double/debiased ML (partially linear model)
top10 = df.Country.value_counts().head(10).index
df["Country_g"] = df.Country.where(df.Country.isin(top10), "Other")


def dml_plr(d, num, cat, reps=3, K=5, leaf=5, trees=100):
    """Partialling-out DML with random forests and K-fold cross-fitting (Chernozhukov et al., 2018)."""
    Xc = pd.get_dummies(d[num + cat], columns=cat, drop_first=True).astype(float).values
    yy = d[Y].values.astype(float); tt_ = d[X].values.astype(float); nn = len(d)
    thetas, ses = [], []
    for r in range(reps):
        ry, rt = np.zeros(nn), np.zeros(nn)
        for tr_, te_ in KFold(K, shuffle=True, random_state=r).split(Xc):
            f = lambda: RandomForestRegressor(trees, min_samples_leaf=leaf, random_state=r)
            ry[te_] = yy[te_] - f().fit(Xc[tr_], yy[tr_]).predict(Xc[te_])
            rt[te_] = tt_[te_] - f().fit(Xc[tr_], tt_[tr_]).predict(Xc[te_])
        th = (rt * ry).sum() / (rt ** 2).sum()
        se = np.sqrt(np.mean((ry - th * rt) ** 2 * rt ** 2) / np.mean(rt ** 2) ** 2 / nn)
        thetas.append(th); ses.append(se)
    th = float(np.median(thetas))
    se = float(np.sqrt(np.median(np.array(ses) ** 2 + (np.array(thetas) - th) ** 2)))
    return {"theta": th, "se": se, "ci": [th - 1.96 * se, th + 1.96 * se], "n": nn}


base_num, base_cat = ["Age"], ["Gender", "Academic_Level", "Relationship_Status", "Country_g"]
OUT["dml"] = {"overall": [], "groups": []}
for label, num, cat in [("A: background only", base_num, base_cat),
                        ("B: A + platform", base_num, base_cat + ["Most_Used_Platform"]),
                        ("C: A + sleep", base_num + [S], base_cat),
                        ("D: A + addiction + conflicts", base_num + ["Addicted_Score", "Conflicts_Over_Social_Media"], base_cat)]:
    r = dml_plr(df, num, cat); r["label"] = label; OUT["dml"]["overall"].append(r)
    print(label, round(r["theta"], 3), flush=True)
for col, vals in [("Academic_Level", ["Undergraduate", "Graduate", "High School"]),
                  ("Gender", ["Female", "Male"]),
                  ("Most_Used_Platform", ["Instagram", "TikTok", "Facebook", "WhatsApp"])]:
    for v in vals:
        d = df[df[col] == v].reset_index(drop=True)
        cat = [c for c in base_cat if c != col and d[c].nunique() > 1]
        r = dml_plr(d, base_num, cat, leaf=8); r.update(group=col, value=v)
        r["degenerate"] = bool(r["se"] < 0.01)
        OUT["dml"]["groups"].append(r)
        print(col, v, round(r["theta"], 3), flush=True)

# ------------------------------------------------------------------ 11. Points for the scatter plot
plats = [p["platform"] for p in OUT["platforms"]]
levels = ["High School", "Undergraduate", "Graduate"]
countries = df.Country.value_counts().index.tolist()
OUT["codes"] = {"platforms": plats, "levels": levels, "countries": countries}
OUT["points"] = [[float(r[X]), int(r[Y]), plats.index(r.Most_Used_Platform), levels.index(r.Academic_Level),
                  countries.index(r.Country), float(r[S]), int(r.Student_ID)] for _, r in df.iterrows()]


def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)): return None if np.isnan(o) else round(float(o), 6)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, np.bool_): return bool(o)
    return o


with open("results.json", "w") as f:
    json.dump(clean(OUT), f)
print("wrote results.json")
