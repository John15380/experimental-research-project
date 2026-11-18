#!/usr/bin/env python3
import csv
import math
import re
from collections import defaultdict
from project_paths import DATA, ROOT


OUT = ROOT / "paper" / "figs" / "tikz"
TABLE_OUT = ROOT / "paper" / "tables"

CONDS = [
    ("gain_self", "G/Self"),
    ("gain_agent_invisible", "G/Inv"),
    ("gain_agent_visible", "G/Vis"),
    ("loss_self", "L/Self"),
    ("loss_agent_invisible", "L/Inv"),
    ("loss_agent_visible", "L/Vis"),
]
COND_LABEL = dict(CONDS)
MODELS = ["DeepSeek-Flash", "DeepSeek-Pro", "Grok-4", "Kimi-k2", "GPT-4.1"]
MODEL_COLORS = {
    "DeepSeek-Flash": "dsflash",
    "DeepSeek-Pro": "dspro",
    "Grok-4": "grokc",
    "Kimi-k2": "kimic",
    "GPT-4.1": "gptc",
}
RISK_CLASSES = [
    ("highly risk-seeking", "H seek", "riskred"),
    ("very risk-seeking", "V seek", "riskorange"),
    ("risk-seeking", "seek", "riskorangeone"),
    ("slightly risk-seeking", "S seek", "riskyellow"),
    ("risk-neutral", "neutral", "riskneutral"),
    ("slightly risk-averse", "S averse", "riskgreenone"),
    ("risk-averse", "averse", "riskgreentwo"),
    ("very risk-averse", "V averse", "riskgreenthree"),
    ("highly risk-averse", "H averse", "riskgreenfour"),
]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def esc(s):
    return s.replace("_", r"\_").replace("&", r"\&")


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def stderr(xs):
    xs = list(xs)
    if len(xs) <= 1:
        return 0.0
    m = mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var) / math.sqrt(len(xs))


def value(row, key):
    return float(row[key])


def classify(n_safe):
    n = int(round(float(n_safe)))
    if n <= 0:
        return "highly risk-seeking"
    if n == 1:
        return "very risk-seeking"
    if n == 2:
        return "risk-seeking"
    if n == 3:
        return "slightly risk-seeking"
    if n == 4:
        return "risk-neutral"
    if n == 5:
        return "slightly risk-averse"
    if n == 6:
        return "risk-averse"
    if n <= 8:
        return "very risk-averse"
    return "highly risk-averse"


def preamble():
    return r"""\tikzset{
  every picture/.style={font=\scriptsize},
}
\definecolor{dsflash}{HTML}{4E79A7}
\definecolor{dspro}{HTML}{F28E2B}
\definecolor{grokc}{HTML}{59A14F}
\definecolor{kimic}{HTML}{E15759}
\definecolor{gptc}{HTML}{B07AA1}
\definecolor{gridgray}{HTML}{D9D9D9}
\definecolor{riskred}{HTML}{B2182B}
\definecolor{riskorange}{HTML}{EF8A62}
\definecolor{riskorangeone}{HTML}{FDAE61}
\definecolor{riskyellow}{HTML}{FDDC8B}
\definecolor{riskneutral}{HTML}{FFFFBF}
\definecolor{riskgreenone}{HTML}{D9EF8B}
\definecolor{riskgreentwo}{HTML}{A6D96A}
\definecolor{riskgreenthree}{HTML}{66BD63}
\definecolor{riskgreenfour}{HTML}{1A9850}
"""


def axis_style(extra=""):
    return rf"""
  width=\linewidth,
  height=0.27\textheight,
  tick label style={{font=\tiny}},
  label style={{font=\scriptsize}},
  legend style={{font=\tiny, draw=none, fill=none}},
  ymajorgrids=true,
  grid style={{gridgray}},
  ymin=0,
  ymax=10.5,
  ylabel={{$N_{{\mathrm{{safe}}}}$}},
  {extra}
"""


def write(name, body):
    # pgfplots option lists are sensitive to blank paragraphs inside [...].
    compact = "\n".join(line for line in body.strip().splitlines() if line.strip())
    (OUT / name).write_text(preamble() + "\n" + compact + "\n", encoding="utf-8")


def write_table(name, body):
    TABLE_OUT.mkdir(parents=True, exist_ok=True)
    (TABLE_OUT / name).write_text(body.strip() + "\n", encoding="utf-8")


def fmt_num(x, ndigits=2):
    return f"{float(x):.{ndigits}f}"


def fmt_p(x):
    x = float(x)
    if x < 0.001:
        return r"$<0.001$"
    return f"{x:.3f}"


def p_stars(p):
    p = float(p)
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def stat_report_text():
    return (DATA / "statistical_test_results.md").read_text(encoding="utf-8")


def coords(pairs):
    return " ".join(f"({x},{y:.3f})" for x, y in pairs)


def mean_by(rows, keys):
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in keys)].append(float(r["n_safe"]))
    return {k: mean(v) for k, v in groups.items()}


def grouped_bar(name, rows, models, title=None, height="0.27\\textheight"):
    means = mean_by(rows, ["model", "condition"])
    plots = []
    bar_width = "8pt" if len(models) == 1 else ("4pt" if len(models) <= 3 else "2.4pt")
    max_val = max((means.get((model, cond), 0) for model in models for cond, _ in CONDS), default=10)
    ymax = 5.2 if max_val <= 5 else 10.5
    for model in models:
        points = []
        for cond, label in CONDS:
            val = means.get((model, cond))
            if val is not None:
                points.append((label, val))
        plots.append(
            rf"\addplot[ybar, bar width={bar_width}, fill={MODEL_COLORS[model]}, draw=none] coordinates {{{coords(points)}}};"
        )
    legend = ",".join(esc(m) for m in models)
    legend_line = rf"\legend{{{legend}}}" if len(models) > 1 else ""
    title_line = f"title={{{title}}}," if title else ""
    body = rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  width=\linewidth,
  height={height},
  ybar,
  ymin=0,
  ymax={ymax},
  ylabel={{$N_{{\mathrm{{safe}}}}$}},
  symbolic x coords={{G/Self,G/Inv,G/Vis,L/Self,L/Inv,L/Vis}},
  xtick=data,
  enlarge x limits=0.10,
  xticklabel style={{font=\tiny, rotate=35, anchor=east}},
  tick label style={{font=\tiny}},
  label style={{font=\scriptsize}},
  legend style={{font=\tiny, draw=none, fill=none, at={{(0.5,1.05)}}, anchor=south, legend columns=3}},
  ymajorgrids=true,
  grid style={{gridgray}},
  {title_line}
]
{chr(10).join(plots)}
\addplot[black, dashed, sharp plot, forget plot] coordinates {{(G/Self,4) (L/Vis,4)}};
{legend_line}
\end{{axis}}
\end{{tikzpicture}}
"""
    write(name, body)


def distribution(name, rows, model, title=None, height="0.43\\textheight"):
    counts = defaultdict(lambda: [0] * 11)
    for r in rows:
        if r["model"] == model and r["thinking"] == "disabled":
            counts[r["condition"]][int(float(r["n_safe"]))] += 1
    panels = []
    for i, (cond, label) in enumerate(CONDS, 1):
        points = [(x, counts[cond][x]) for x in range(11)]
        panel_mean = mean([i for i, c in enumerate(counts[cond]) for _ in range(c)])
        axis_labels = []
        if i in (1, 2, 3):
            axis_labels.append(r"xticklabels={}")
        if i in (4, 5, 6):
            axis_labels.append(r"xlabel={$N_{\mathrm{safe}}$}")
        if i in (1, 4):
            axis_labels.append("ylabel={freq}")
        axis_label_opts = ",\n  ".join(axis_labels)
        if axis_label_opts:
            axis_label_opts += ","
        panels.append(
            rf"""\nextgroupplot[
  title={{{label}}},
  ymin=0,
  ymax={max(counts[cond] + [1]) * 1.18:.1f},
  xmin=-0.5,
  xmax=10.5,
  xtick={{0,2,4,6,8,10}},
  yticklabel style={{font=\tiny}},
  {axis_label_opts}
]
\addplot[ybar, bar width=4.6pt, fill={MODEL_COLORS.get(model, "dsflash")}, draw=none] coordinates {{{coords(points)}}};
\addplot[red, dashed, thick, forget plot] coordinates {{({panel_mean:.2f},0) ({panel_mean:.2f},{max(counts[cond] + [1]) * 1.05:.1f})}};
\node[anchor=north east, font=\tiny, fill=white, fill opacity=0.78, text opacity=1, inner sep=1pt] at (rel axis cs:0.98,0.98) {{Mean={panel_mean:.2f}}};"""
        )
    title_line = f"group style={{group name=g, group size=3 by 2, horizontal sep=0.48cm, vertical sep=0.62cm}}, title={{{title}}}," if title else "group style={group name=g, group size=3 by 2, horizontal sep=0.48cm, vertical sep=0.62cm},"
    body = rf"""
\begin{{tikzpicture}}
\begin{{groupplot}}[
  {title_line}
  width=0.33\linewidth,
  height={height}/2.35,
  tick label style={{font=\tiny}},
  label style={{font=\tiny}},
  title style={{font=\tiny}},
  ymajorgrids=true,
  grid style={{gridgray}},
]
{chr(10).join(panels)}
\end{{groupplot}}
\end{{tikzpicture}}
"""
    write(name, body)


def interaction_gpt(rows):
    subset = [r for r in rows if r["model"] == "GPT-4.1" and r["thinking"] == "disabled"]
    groups = defaultdict(list)
    for r in subset:
        groups[(r["domain"], r["acc_derived"])].append(float(r["n_safe"]))
    acc_order = [("none", "Self", "gptc"), ("invisible", "Inv", "dsflash"), ("visible", "Vis", "grokc")]
    plots = []
    for acc, label, color in acc_order:
        pts = [("Gain", mean(groups[("gain", acc)])), ("Loss", mean(groups[("loss", acc)]))]
        plots.append(rf"\addplot+[mark=*, thick, {color}] coordinates {{{coords(pts)}}};")
    style = axis_style('height=0.215\\textheight, symbolic x coords={Gain,Loss}, xtick=data, legend pos=north west, xlabel={domain},')
    body = rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  {style}
]
{chr(10).join(plots)}
\addplot+[black, dashed, sharp plot, forget plot] coordinates {{(Gain,4) (Loss,4)}};
\legend{{Self,Invisible,Visible}}
\end{{axis}}
\end{{tikzpicture}}
"""
    write("fig04_gpt41_interaction.tex", body)


def risk_class(name, rows, model, height="0.25\\textheight", legend_y="-0.24", legend_columns=5):
    totals = defaultdict(int)
    class_counts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if r["model"] == model and r["thinking"] == "disabled":
            label = COND_LABEL[r["condition"]]
            totals[label] += 1
            class_counts[label][classify(r["n_safe"])] += 1
    plots = []
    for cls, _, color in RISK_CLASSES:
        pts = []
        for _, label in CONDS:
            prop = class_counts[label][cls] / totals[label] if totals[label] else 0
            pts.append((prop, label))
        plots.append(rf"\addplot[xbar, fill={color}, draw=white] coordinates {{{' '.join(f'({x:.3f},{y})' for x, y in pts)}}};")
    legend = ",".join(short for _, short, _ in RISK_CLASSES)
    body = rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  width=\linewidth,
  height={height},
  xbar stacked,
  xmin=0,
  xmax=1,
  symbolic y coords={{G/Self,G/Inv,G/Vis,L/Self,L/Inv,L/Vis}},
  ytick=data,
  yticklabel style={{font=\tiny}},
  xticklabel style={{font=\tiny}},
  xlabel={{proportion}},
  label style={{font=\scriptsize}},
  title style={{font=\scriptsize}},
  clip=false,
  legend style={{font=\tiny, draw=none, fill=none, at={{(0.5,{legend_y})}}, anchor=north, legend columns={legend_columns}, /tikz/every even column/.append style={{column sep=0.45em}}}},
]
{chr(10).join(plots)}
\legend{{{legend}}}
\end{{axis}}
\end{{tikzpicture}}
"""
    write(name, body)


def thinking_compare(rows):
    groups = defaultdict(list)
    for r in rows:
        if r["model"] in ("DeepSeek-Flash", "DeepSeek-Pro"):
            groups[(r["model"], r["thinking"])].append(float(r["n_safe"]))
    plots = []
    for thinking, color, shift in [("disabled", "dsflash", "-8pt"), ("enabled", "dspro", "8pt")]:
        pts = []
        for m in ("DeepSeek-Flash", "DeepSeek-Pro"):
            vals = groups[(m, thinking)]
            pts.append(rf"({m},{mean(vals):.3f}) +- (0,{stderr(vals):.3f})")
        plots.append(
            rf"\addplot[ybar, bar width=14pt, bar shift={shift}, fill={color}, draw=none, error bars/.cd, y dir=both, y explicit, error bar style={{black, thick}}] coordinates {{{' '.join(pts)}}};"
        )
    style = axis_style('width=0.58\\linewidth, height=0.19\\textheight, ybar, symbolic x coords={DeepSeek-Flash,DeepSeek-Pro}, xtick=data, xticklabel style={font=\\tiny}, enlarge x limits=0.34, legend style={font=\\tiny, draw=none, fill=white, fill opacity=0.9, text opacity=1, at={(0.98,0.98)}, anchor=north east},')
    body = rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  {style}
]
{chr(10).join(plots)}
\addplot[black, dashed, sharp plot, forget plot] coordinates {{(DeepSeek-Flash,4) (DeepSeek-Pro,4)}};
\legend{{disabled, enabled}}
\end{{axis}}
\end{{tikzpicture}}
"""
    write("fig09_deepseek_thinking.tex", body)


def text_analysis():
    rows = [r for r in read_csv(DATA / "reason_keywords_stats.csv") if r["mode"] == "batch"]
    role_map = {"self": "Self", "agent_invisible": "Inv", "agent_visible": "Vis"}
    keys = [("kw_math", "EV/math", "dsflash"), ("kw_client", "client/resp.", "dspro"), ("kw_risk", "risk/loss", "grokc")]
    panels = []
    for idx, (domain, title) in enumerate([("gain", "Gain"), ("loss", "Loss")], 1):
        grouped = defaultdict(list)
        for r in rows:
            cond = r["condition"]
            if cond.startswith(domain):
                role = role_map["_".join(cond.split("_")[1:])]
                for key, _, _ in keys:
                    grouped[(role, key)].append(float(r[key]))
        ylabel = "ylabel={mention rate (\\%)}," if idx == 1 else ""
        panel = [rf"\nextgroupplot[title={{{title}}}, symbolic x coords={{Self,Inv,Vis}}, xtick=data, {ylabel}]"]
        for key, label, color in keys:
            pts = [(role, mean(grouped[(role, key)]) * 100) for role in ["Self", "Inv", "Vis"]]
            panel.append(rf"\addplot[ybar, bar width=4pt, fill={color}, draw=none] coordinates {{{coords(pts)}}};")
        panels.append("\n".join(panel))
    body = rf"""
\begin{{tikzpicture}}
\begin{{groupplot}}[
  group style={{group size=2 by 1, horizontal sep=0.62cm}},
  width=0.44\linewidth,
  height=0.18\textheight,
  ymin=0,
  ymax=105,
  tick label style={{font=\tiny}},
  label style={{font=\scriptsize}},
  title style={{font=\scriptsize}},
  ymajorgrids=true,
  grid style={{gridgray}},
]
{chr(10).join(panels)}
\end{{groupplot}}
\node[anchor=north, font=\tiny] at ($(group c1r1.south)!0.5!(group c2r1.south)+(0,-0.20)$)
  {{\tikz\fill[dsflash] (0,0) rectangle (0.16,0.08); EV/math \quad
    \tikz\fill[dspro] (0,0) rectangle (0.16,0.08); client/resp. \quad
    \tikz\fill[grokc] (0,0) rectangle (0.16,0.08); risk/loss}};
\end{{tikzpicture}}
"""
    write("fig11_text_analysis.tex", body)


def text_models():
    rows = [r for r in read_csv(DATA / "reason_keywords_stats.csv") if r["mode"] == "batch"]
    model_map = [("grok:grok-4", "Grok-4"), ("kimi:kimi-k2-250905", "Kimi-k2"), ("openai:gpt-4.1", "GPT-4.1")]
    keys = [("kw_math", "EV/math", "dsflash"), ("kw_client", "client/resp.", "dspro"), ("kw_risk", "risk/loss", "grokc")]
    panels = []
    for idx, (model_key, title) in enumerate(model_map, 1):
        grouped = defaultdict(list)
        for r in rows:
            if model_key in r["model"]:
                role = "Self" if r["condition"].endswith("_self") else ("Inv" if "invisible" in r["condition"] else "Vis")
                for key, _, _ in keys:
                    grouped[(role, key)].append(float(r[key]))
        ylabel = "ylabel={mention rate (\\%)}," if idx == 1 else ""
        panel = [rf"\nextgroupplot[title={{{title}}}, symbolic x coords={{Self,Inv,Vis}}, xtick=data, {ylabel}]"]
        for key, label, color in keys:
            pts = [(role, mean(grouped[(role, key)]) * 100) for role in ["Self", "Inv", "Vis"]]
            panel.append(rf"\addplot[ybar, bar width=3.2pt, fill={color}, draw=none] coordinates {{{coords(pts)}}};")
        panels.append("\n".join(panel))
    body = rf"""
\begin{{tikzpicture}}
\begin{{groupplot}}[
  group style={{group size=3 by 1, horizontal sep=0.72cm}},
  width=0.31\linewidth,
  height=0.19\textheight,
  ymin=0,
  ymax=105,
  tick label style={{font=\tiny}},
  label style={{font=\tiny}},
  title style={{font=\tiny}},
  ymajorgrids=true,
  grid style={{gridgray}},
]
{chr(10).join(panels)}
\end{{groupplot}}
\node[anchor=north, font=\tiny] at ($(group c1r1.south)!0.5!(group c3r1.south)+(0,-0.18)$)
  {{\tikz\fill[dsflash] (0,0) rectangle (0.16,0.08); EV/math \quad
    \tikz\fill[dspro] (0,0) rectangle (0.16,0.08); client/resp. \quad
    \tikz\fill[grokc] (0,0) rectangle (0.16,0.08); risk/loss}};
\end{{tikzpicture}}
"""
    write("fig12_text_models.tex", body)


def sequence_all():
    rows = read_csv(DATA / "sequence_effect_all_models.csv")
    panels = []
    for model in MODELS:
        panel_rows = [r for r in rows if r["model"] == model]
        panel = [rf"\nextgroupplot[title={{{esc(model)}}}, symbolic x coords={{G/Self,G/Inv,G/Vis,L/Self,L/Inv,L/Vis}}, xtick=data]"]
        for key, sd_key, n_key, label, color, shift in [
            ("batch_mean", "batch_sd", "batch_n", "batch", "dsflash", "-2.1pt"),
            ("single_mean", "single_sd", "single_n", "single", "dspro", "2.1pt"),
        ]:
            pts = []
            for r in panel_rows:
                se = float(r[sd_key]) / math.sqrt(float(r[n_key])) if float(r[n_key]) else 0.0
                pts.append(rf"({COND_LABEL[r['condition']]},{float(r[key]):.3f}) +- (0,{se:.3f})")
            panel.append(
                rf"\addplot[ybar, bar width=3.4pt, bar shift={shift}, fill={color}, draw=none, error bars/.cd, y dir=both, y explicit, error bar style={{black, thin}}] coordinates {{{' '.join(pts)}}};"
            )
        for r in panel_rows:
            stars = p_stars(r["p"])
            if stars:
                y = min(10.35, float(r["single_mean"]) + float(r["single_sd"]) / math.sqrt(float(r["single_n"])) + 0.42)
                panel.append(rf"\node[red, font=\tiny] at (axis cs:{COND_LABEL[r['condition']]},{y:.2f}) {{{stars}}};")
        panels.append("\n".join(panel))
    body = rf"""
\begin{{tikzpicture}}
\begin{{groupplot}}[
  group style={{group name=seq, group size=5 by 1, horizontal sep=0.42cm}},
  width=0.252\linewidth,
  height=0.18\textheight,
  ymin=0,
  ymax=10.5,
  enlarge x limits=0.12,
  xticklabel style={{font=\tiny, rotate=45, anchor=east}},
  tick label style={{font=\tiny}},
  label style={{font=\tiny}},
  title style={{font=\tiny}},
  ymajorgrids=true,
  grid style={{gridgray}},
  clip=false,
]
{chr(10).join(panels)}
\end{{groupplot}}
\node[anchor=south, font=\tiny, fill=white, fill opacity=0.90, text opacity=1, inner sep=1.5pt]
  at ($(seq c1r1.north)!0.5!(seq c5r1.north)+(0,0.68)$)
  {{\tikz\fill[dsflash] (0,0) rectangle (0.16,0.08); batch \quad
    \tikz\fill[dspro] (0,0) rectangle (0.16,0.08); single}};
\end{{tikzpicture}}
"""
    write("fig13_sequence_all_models.tex", body)


def sequence_heatmap():
    rows = read_csv(DATA / "sequence_effect_all_models.csv")
    lookup = {(r["model"], r["condition"]): float(r["delta"]) for r in rows}
    max_abs = max(abs(v) for v in lookup.values())
    cell_w, cell_h = 1.52, 0.42
    lines = [
        r"\begin{tikzpicture}[x=1cm,y=1cm,font=\tiny]",
        r"\path[use as bounding box] (0.05,1.10) rectangle (11.72,-2.55);",
        r"\node[font=\tiny] at (6.90,0.92) {single-call minus batch-call mean};",
    ]
    for j, (_, label) in enumerate(CONDS):
        lines.append(rf"\node[rotate=45, anchor=west] at ({2.46 + j*cell_w:.2f},0) {{{label}}};")
    for i, model in enumerate(MODELS):
        y = -0.62 - i * cell_h
        lines.append(rf"\node[anchor=east] at (2.22,{y + cell_h/2:.2f}) {{{esc(model)}}};")
        for j, (cond, _) in enumerate(CONDS):
            x = 2.34 + j * cell_w
            val = lookup[(model, cond)]
            intensity = min(90, 15 + 75 * abs(val) / max_abs)
            color = f"grokc!{intensity:.0f}!white" if val >= 0 else f"riskred!{intensity:.0f}!white"
            stars = "***" if abs(val) >= 1.5 else ("**" if abs(val) >= 1.0 else ("*" if abs(val) >= 0.5 else ""))
            lines.append(rf"\filldraw[fill={color}, draw=white] ({x:.2f},{y:.2f}) rectangle ({x+cell_w:.2f},{y+cell_h:.2f});")
            lines.append(rf"\node at ({x+cell_w/2:.2f},{y+cell_h/2:.2f}) {{${val:+.1f}$\;{stars}}};")
    lines.append(r"\end{tikzpicture}")
    write("fig14_sequence_delta_heatmap.tex", "\n".join(lines))


def table_descriptive():
    rows = read_csv(DATA / "table2_descriptive_stats.csv")
    lookup = {(r["model"], r["condition"]): r for r in rows}
    lines = [
        r"\begin{table}[tb]",
        r"  \caption{各模型在各实验条件下的安全选择数（$N_{\text{safe}}$）描述性统计；各条件样本量均为$n=50$}",
        r"  \label{tab:descriptive}",
        r"  \centering",
        r"  \scriptsize",
        r"  \setlength{\tabcolsep}{2.2pt}",
        r"  \begin{tabular}{llrrrrr}",
        r"    \toprule",
        r"    模型 & 条件 & 均值 & $SD$ & 中位数 & 最小值 & 最大值 \\",
        r"    \midrule",
    ]
    for model in MODELS:
        for i, (cond, label) in enumerate(CONDS):
            r = lookup[(model, cond)]
            model_cell = rf"\multirow{{6}}{{*}}{{{model}}}" if i == 0 else ""
            lines.append(
                "    "
                + " & ".join(
                    [
                        model_cell,
                        label.replace("G/", "Gain/").replace("L/", "Loss/"),
                        fmt_num(r["mean"]),
                        fmt_num(r["std"]),
                        fmt_num(r["median"], 1),
                        str(int(float(r["min"]))),
                        str(int(float(r["max"]))),
                    ]
                )
                + r" \\"
            )
    lines += [
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
    ]
    write_table("table_descriptive.tex", "\n".join(lines))


def table_agent_effect():
    text = stat_report_text()
    pattern = re.compile(
        r"Model ([^:]+): Self mean=([0-9.]+), Agent mean=([0-9.]+) \| (?:(?:Mann-Whitney U=([0-9.]+), p=([0-9.eE+-]+))|(?:Identical distributions \(p=1.0\)))"
    )
    rows = {m.group(1): m.groups()[1:] for m in pattern.finditer(text)}
    lines = [
        r"\begin{table}[tb]",
        r"  \caption{代理角色主效应检验结果}",
        r"  \label{tab:agent_effect}",
        r"  \centering",
        r"  \footnotesize",
        r"  \setlength{\tabcolsep}{3pt}",
        r"  \begin{tabular}{lrrrr}",
        r"    \toprule",
        r"    模型 & Self均值 & Agent均值 & $U$ & $p$ \\",
        r"    \midrule",
    ]
    for model in MODELS:
        self_m, agent_m, u, p = rows[model]
        lines.append(f"    {model} & {float(self_m):.2f} & {float(agent_m):.2f} & {u or '--'} & {fmt_p(p or 1.0)} \\\\")
    lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}"]
    write_table("table_agent_effect.tex", "\n".join(lines))


def table_domain_effect():
    text = stat_report_text()
    pattern = re.compile(
        r"Model ([^:]+): Gain mean=([0-9.]+), Loss mean=([0-9.]+) \| (?:(?:Mann-Whitney U=([0-9.]+), p=([0-9.eE+-]+))|(?:Identical distributions \(p=1.0\)))"
    )
    rows = {m.group(1): m.groups()[1:] for m in pattern.finditer(text)}
    lines = [
        r"\begin{table}[tb]",
        r"  \caption{损益域框架效应检验结果}",
        r"  \label{tab:domain_effect}",
        r"  \centering",
        r"  \footnotesize",
        r"  \setlength{\tabcolsep}{4pt}",
        r"  \begin{tabular}{lrrrr}",
        r"    \toprule",
        r"    模型 & 收益域 & 损失域 & $U$ & $p$ \\",
        r"    \midrule",
    ]
    for model in MODELS:
        gain, loss, u, p = rows[model]
        lines.append(f"    {model} & {float(gain):.2f} & {float(loss):.2f} & {u or '--'} & {fmt_p(p or 1.0)} \\\\")
    lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}"]
    write_table("table_domain_effect.tex", "\n".join(lines))


def table_accountability_effect():
    text = stat_report_text()
    pattern = re.compile(
        r"Model ([^:]+): Kruskal-Wallis H=([0-9.]+), p=([0-9.eE+-]+) \(Means: None=([0-9.]+), Inv=([0-9.]+), Vis=([0-9.]+)\)"
    )
    rows = {m.group(1): m.groups()[1:] for m in pattern.finditer(text)}
    lines = [
        r"\begin{table}[tb]",
        r"  \caption{问责性调节效应检验结果}",
        r"  \label{tab:accountability_effect}",
        r"  \centering",
        r"  \footnotesize",
        r"  \setlength{\tabcolsep}{3pt}",
        r"  \begin{tabular}{lrrrrr}",
        r"    \toprule",
        r"    模型 & Self & Inv & Vis & $H$ & $p$ \\",
        r"    \midrule",
    ]
    for model in MODELS:
        h, p, none, inv, vis = rows[model]
        lines.append(f"    {model} & {float(none):.2f} & {float(inv):.2f} & {float(vis):.2f} & {float(h):.2f} & {fmt_p(p)} \\\\")
    lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}"]
    write_table("table_accountability_effect.tex", "\n".join(lines))


def table_thinking_effect():
    text = stat_report_text()
    pattern = re.compile(
        r"(DeepSeek-[^:]+): Enabled mean=([0-9.]+), Disabled mean=([0-9.]+) \| Mann-Whitney U=([0-9.]+), p=([0-9.eE+-]+)"
    )
    rows = {m.group(1): m.groups()[1:] for m in pattern.finditer(text)}
    lines = [
        r"\begin{table}[tb]",
        r"  \caption{DeepSeek深度思考模式对比检验}",
        r"  \label{tab:thinking_effect}",
        r"  \centering",
        r"  \footnotesize",
        r"  \setlength{\tabcolsep}{4pt}",
        r"  \begin{tabular}{lrrrr}",
        r"    \toprule",
        r"    模型 & Disabled & Enabled & $U$ & $p$ \\",
        r"    \midrule",
    ]
    for model in ["DeepSeek-Flash", "DeepSeek-Pro"]:
        enabled, disabled, u, p = rows[model]
        lines.append(f"    {model} & {float(disabled):.2f} & {float(enabled):.2f} & {u} & {fmt_p(p)} \\\\")
    lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}"]
    write_table("table_thinking_effect.tex", "\n".join(lines))


def tables_readme():
    body = """# Generated Tables

These result tables are generated from data files under `appendices/appendix_c_data_code_results/data/` by `appendices/appendix_c_data_code_results/scripts/generate_tikz_figures.py`.

- `table_descriptive.tex`: `table2_descriptive_stats.csv`
- `table_agent_effect.tex`: `statistical_test_results.md`, section 3.1
- `table_domain_effect.tex`: `statistical_test_results.md`, section 3.2
- `table_accountability_effect.tex`: `statistical_test_results.md`, section 3.3
- `table_thinking_effect.tex`: `statistical_test_results.md`, section 3.5

Tables in `03_experiment_design.tex` are experiment/material specification tables, not statistical result tables.
"""
    write_table("README.md", body)


def generate_tables():
    table_descriptive()
    table_agent_effect()
    table_domain_effect()
    table_accountability_effect()
    table_thinking_effect()
    tables_readme()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_csv(DATA / "cleaned_data.csv")
    disabled = [r for r in rows if r["thinking"] == "disabled"]
    grouped_bar("fig01_mean_comparison.tex", disabled, MODELS, height="0.25\\textheight")
    grouped_bar("fig02_deepseek_pro_mean.tex", [r for r in disabled if r["model"] == "DeepSeek-Pro"], ["DeepSeek-Pro"], height="0.22\\textheight")
    distribution("fig03_gpt41_distribution.tex", rows, "GPT-4.1", height="0.36\\textheight")
    distribution("fig03_kimi_distribution.tex", rows, "Kimi-k2", height="0.36\\textheight")
    interaction_gpt(rows)
    risk_class("fig05_gpt41_risk_classification.tex", rows, "GPT-4.1", height="0.17\\textheight", legend_y="-0.32")
    distribution("fig06_grok_distribution.tex", rows, "Grok-4", height="0.34\\textheight")
    grouped_bar("fig07_kimi_mean.tex", [r for r in disabled if r["model"] == "Kimi-k2"], ["Kimi-k2"], height="0.18\\textheight")
    risk_class("fig08_deepseek_pro_risk_classification.tex", rows, "DeepSeek-Pro", height="0.16\\textheight", legend_y="-0.32")
    distribution("fig08_deepseek_flash_distribution_disabled.tex", rows, "DeepSeek-Flash", height="0.26\\textheight")
    thinking_compare(rows)
    distribution("fig10_deepseek_flash_distribution_disabled.tex", rows, "DeepSeek-Flash", height="0.25\\textheight")
    # Enabled DeepSeek-Flash distribution is a special filter, so temporarily mark it as disabled for reuse.
    enabled_rows = [dict(r, thinking="disabled") for r in rows if r["model"] == "DeepSeek-Flash" and r["thinking"] == "enabled"]
    distribution("fig10_deepseek_flash_distribution_enabled.tex", enabled_rows, "DeepSeek-Flash", height="0.25\\textheight")
    text_analysis()
    text_models()
    sequence_all()
    sequence_heatmap()
    generate_tables()


if __name__ == "__main__":
    main()
