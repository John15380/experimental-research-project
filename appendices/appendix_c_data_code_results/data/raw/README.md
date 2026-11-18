# Original API Records

This directory preserves the original per-model CSV exports from the team's working package, consolidated into `main/` and `single/`. The retained files are byte-for-byte copies of those exports, including their original encodings.

| Directory | Trial CSVs | Records | Contents |
| --- | ---: | ---: | --- |
| `main/deepseek/flash/` | 1 | 600 | Flash sessions with thinking disabled/enabled |
| `main/deepseek/pro/` | 1 | 600 | Pro sessions with thinking disabled/enabled |
| `main/grok_grok-4/` | 1 | 300 | Grok-4 main experiment |
| `main/kimi_kimi-k2-250905/` | 1 | 300 | Kimi-k2 main experiment |
| `main/openai_gpt-4.1/` | 1 | 300 | GPT-4.1 main experiment |
| `single/deepseek/` | 1 | 1,200 | Independent-question controls for both DeepSeek models |
| `single/grok_grok-4/` | 1 | 600 | Grok-4 independent-question controls |
| `single/kimi_kimi-k2-250905/` | 1 | 600 | Kimi-k2 independent-question controls |
| `single/openai_gpt-4.1/` | 1 | 600 | GPT-4.1 independent-question controls |

Each main-experiment directory also retains its original `summary.csv`. Main trial records contain ten decisions per session; single-question records contain one decision per API call.

During consolidation, the combined DeepSeek trial CSV and combined summary CSVs were removed after confirming that their records matched the retained per-model files. The combined Grok/Kimi/GPT trial CSV contained the same 900 sessions plus derived columns (`choices_parsed`, `reasoning_len`, and `source_csv`); the original responses remain in the per-model files. Generated images in the original working folder were removed, while the submitted appendix figures and paper figures were preserved.

The cleaned dataset in `../cleaned_data.csv` and the summaries in the parent directory describe these same experiments at different processing stages. Do not add their record counts to the raw sample size.
