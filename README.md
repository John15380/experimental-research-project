# LLM Risk Preferences in Delegated Financial Decisions

An experimental study of how decision roles, accountability, and gain/loss framing shape the risk preferences of large language models.

This repository contains the experimental materials, archived model responses, analysis scripts, figures, and LaTeX manuscript for a collaborative course project in **Introduction to Experimental Research** at Zhejiang University. It combines behavioral economics with LLM evaluation to investigate how models make risky choices for themselves and on behalf of others.

[Read the report (Chinese, PDF)](paper/report.pdf) · [LaTeX source](paper/report.tex) · [Final revised statistical tests](appendices/appendix_c_data_code_results/data/revision_statistical_tests.md)

## Research Questions

- Does an LLM's risk preference change when it makes decisions for another person rather than for itself?
- How do gain/loss framing and the principal's ability to observe decisions affect this change?
- Do these patterns differ across models, reasoning modes, and question presentation formats?

## Experimental Design

The study adapts the **Holt–Laury paired-lottery task**: each session contains ten choices between a lower-variance option A and a higher-variance option B. The main outcome, `n_safe`, counts the number of A choices, from 0 to 10. Higher values indicate greater risk aversion; the study uses approximately four safe choices as its risk-neutral benchmark.

A **2 × 3 between-session factorial design** crosses the outcome domain with the decision role and observability condition:

| Decision condition | Gain domain | Loss domain |
| --- | --- | --- |
| Self: deciding for oneself | `gain_self` | `loss_self` |
| Agent, unobservable: deciding for another person whose observation is restricted | `gain_agent_invisible` | `loss_agent_invisible` |
| Agent, observable: deciding for another person who can observe the decisions | `gain_agent_visible` | `loss_agent_visible` |

Each model–condition combination is sampled in **50 independent, stateless API sessions**. All prompts and lottery materials are in Chinese.

| Experiment component | Coverage | Recorded sessions |
| --- | --- | ---: |
| Main experiment | 5 models × 6 conditions × 50 repetitions, with thinking disabled where recorded | 1,500 |
| Deep-thinking comparison | 2 DeepSeek models × 6 conditions × 50 repetitions, with thinking enabled | 600 |
| Total for the two components above | 10 lottery choices per session | **2,100 sessions / 21,000 choices** |

The five models are **DeepSeek-V4-Flash, DeepSeek-V4-Pro, Grok-4, Kimi-k2, and GPT-4.1**, using the identifiers recorded in the experiment. Additional single-question API calls test whether presenting each lottery independently changes the results; these controls are separate from the totals above.

The analysis combines descriptive statistics, Mann–Whitney U tests, Kruskal–Wallis tests, permutation tests, Benjamini–Hochberg (BH) multiple-comparison correction, and keyword-based analysis of decision explanations. Revised permutation tests use **20,000 iterations and fixed random seeds**.

## Main Findings

- **Risk preferences differ substantially across models.** In the full-questionnaire setting, Grok-4 consistently makes four safe choices, Kimi-k2 is highly risk-averse, and GPT-4.1 and the DeepSeek models respond more to changes in experimental conditions.
- **Delegation does not produce a universal shift toward caution or risk-taking.** For GPT-4.1 in the gain domain, unobservable delegation lowers the average safe-choice count relative to self-decisions, while observable delegation raises it. Both comparisons remain significant after BH correction.
- **Accountability interacts with the outcome domain for GPT-4.1.** Observability increases its average safe-choice count by 0.56 in gains and 1.78 in losses, yielding a difference-in-differences statistic of **+1.22** with **BH-adjusted q ≈ 0.025**. The other models do not show a significant interaction after correction.
- **Reasoning mode and presentation format affect measured behavior.** Enabling deep thinking moves both DeepSeek models closer to the study's risk-neutral benchmark. Independent single-question presentation changes the absolute risk levels of several models.

These findings describe behavior under the archived prompts and task settings. They support evaluating financial AI agents by model and deployment context rather than assuming a fixed risk preference.

For final interpretations, use the [report](paper/report.pdf), its [results section](paper/sections/04_results.tex), and the [revised statistical summary](appendices/appendix_c_data_code_results/data/revision_statistical_tests.md). Earlier exploratory summaries are retained to document the analysis process.

## Repository Structure

```text
.
├── README.md
├── paper/
│   ├── report.pdf                    # Final Chinese research report
│   ├── report.tex                    # Main LaTeX entry point
│   ├── report.bib                    # Bibliography
│   ├── sections/                     # Introduction, methods, results, discussion
│   ├── figs/tikz/                    # Figures rendered with TikZ/PGFPlots
│   ├── tables/                       # Statistical tables
│   └── makefile                      # Paper build targets
├── tools/
│   ├── revision_stats.py             # Entry point for the appendix script
│   └── generate_tikz_figures.py      # Entry point for the appendix generator
├── drafts/
│   └── ...                           # Four historical design/report documents
├── appendices/
│   ├── appendix_a_materials/         # Lottery tasks and experiment manual
│   ├── appendix_b_prompts/           # Complete system and condition prompts
│   └── appendix_c_data_code_results/
│       ├── data/                     # Cleaned datasets and statistical results
│       │   └── raw/
│       │       ├── main/             # Original per-model session CSVs/summaries
│       │       └── single/           # Original single-question control CSVs
│       ├── scripts/                  # Canonical analysis and generation code
│       └── figures/                  # Retained analysis figures
└── 期末小组大作业—完整实验研究报告要求.md
```

Experimental materials, data, and analysis implementations are consolidated under `appendices/`. The two commands in `tools/` delegate to the canonical appendix scripts. The historical document folder retains the original design document, Markdown draft, Word report, and template PDF. The `paper/README` file documents the upstream VGTC LaTeX template; this root README documents the research project.

## Data Guide

The [cleaned session-level dataset](appendices/appendix_c_data_code_results/data/cleaned_data.csv) contains the 2,100 full-questionnaire sessions, including the deep-thinking comparison.

| Field | Description |
| --- | --- |
| `model`, `provider`, `model_name` | Standardized model label and recorded provider/model identifiers |
| `thinking` | Recorded reasoning mode: `disabled` or `enabled` |
| `condition`, `trial` | Experimental condition and repetition index |
| `choices` | Comma-separated sequence of ten A/B choices |
| `n_safe` | Number of A choices in the session |
| `n_switches`, `is_valid` | Choice-switching count and the preprocessing validity flag |
| `role_derived`, `acc_derived`, `domain_derived` | Role, accountability, and gain/loss variables derived from the condition |
| `system_prompt`, `user_prompt` | Prompts used for the session |
| `reasons`, `reasoning_content`, `raw_response` | Recorded explanations and response text, where available |
| `parse_error` | Parsing-error information, if present |

Additional files provide condition-level descriptive statistics, explanation keyword rates, and comparisons between full-questionnaire and single-question presentation.

Original API records are preserved in [data/raw/](appendices/appendix_c_data_code_results/data/raw/). The `main/` directory contains five per-model trial CSVs totaling 2,100 sessions and their corresponding summaries. The `single/` directory contains four CSVs totaling 3,000 single-question calls; the DeepSeek file includes both DeepSeek models. The raw records, cleaned dataset, and summary tables represent different processing stages of the same experiments, not additional samples.

## Reproduction

### Build the paper

The compiled report is included, so no setup is needed to read it. To rebuild it, use a LaTeX distribution with **XeLaTeX, BibTeX, ctex/Fandol fonts, and TikZ/PGFPlots**, along with `make`. The VGTC class is bundled in `paper/`.

From the repository root:

```sh
cd paper
make pdf
```

The output is `paper/report.pdf`. Use the explicit `pdf` target: the default `make` target follows the template's older DVI/PostScript workflow. Existing committed figures and tables are sufficient for compilation.

### Reproduce the revised hypothesis tests

From the repository root, run:

```sh
python3 "appendices/appendix_c_data_code_results/scripts/revision_stats.py"
```

This script uses only the Python standard library and the archived cleaned dataset. It regenerates:

- `paper/tables/table_gain_agent_effect.tex`
- `paper/tables/table_domain_accountability_interaction.tex`
- `appendices/appendix_c_data_code_results/data/revision_statistical_tests.md`

These outputs cover the gain-domain delegation comparisons and the accountability-by-domain difference-in-differences tests, including BH correction.

The existing `python3 tools/revision_stats.py` command runs the same implementation. Paths are resolved from the script location, so the scripts do not depend on the caller's working directory.

### Work with the original analyses

The original scripts in `appendices/appendix_c_data_code_results/scripts/` cover data cleaning, descriptive statistics, nonparametric tests, sequence effects, and explanation analysis. Depending on the script, they use **NumPy, pandas, SciPy, Matplotlib, and seaborn**.

The shared `project_paths.py` module resolves inputs and outputs within the repository. CSV/statistical outputs go to `data/`, and generated analysis images go to `figures/`. For example, to rebuild the cleaned dataset from the original per-model CSVs:

```sh
python3 "appendices/appendix_c_data_code_results/scripts/step1_data_cleaning.py"
```

These are archived exploratory analyses and can overwrite their corresponding data or figure outputs. The final interpretations remain those in the revised report and revised statistical summary. The repository archives API outputs and prompts; it does not include an end-to-end API collection runner.

`appendices/appendix_c_data_code_results/scripts/generate_tikz_figures.py` converts the archived analysis summaries into LaTeX figures and tables; `tools/generate_tikz_figures.py` is its compatibility entry point. The generator predates the final statistical revisions and can overwrite corrected tables with earlier exploratory versions. Use the committed figures and tables to build the final report; this generator is retained for reference rather than as a complete regeneration pipeline for the final manuscript.

## Scope and Limitations

- Repeated API calls sample a model's output distribution under a prompt; they are not independent human participants. No matched human control group was collected.
- Labels such as “safe” and “risky” may influence responses. The unobservable-agent prompt also states that the principal does not care about the outcome, introducing an additional semantic difference between conditions.
- Sampling parameters followed platform defaults. Exact default temperature values were not preserved, and temperature was not experimentally manipulated.
- Lottery choices simplify real financial decisions. Findings may change with model versions, prompts, task presentation, or deployment settings.
- Explanation keywords provide descriptive evidence about generated text, not direct access to a model's internal decision mechanism.

## Team

Completed collaboratively by **Jiangtao Hu (胡江涛), Hanyang Yue (岳瀚阳), Jiayi Feng (冯嘉逸), Xin Sun (孙昕), and Qifan Zhou (周起帆)**.

The project brings together experimental design, API-based data collection, statistical analysis, visualization, and research writing. The manuscript uses the VGTC LaTeX template; its original documentation and attribution are preserved in `paper/`.
