# 第三阶段：统计检验结果报告

> 说明：本文件为早期探索性统计摘要，用于记录分析过程。报告修订后的最终补充检验以 `revision_statistical_tests.md`、正文表格和 `tools/revision_stats.py` 为准。

## 3.1 主效应检验 (H1A & H1B: Self vs Agent)
Model DeepSeek-Flash: Self mean=4.05, Agent mean=4.51 | Mann-Whitney U=8911.0, p=1.1461e-01
Model DeepSeek-Pro: Self mean=3.69, Agent mean=3.96 | Mann-Whitney U=8222.0, p=7.3510e-03
Model Grok-4: Self mean=4.00, Agent mean=4.00 | Identical distributions (p=1.0)
Model Kimi-k2: Self mean=8.93, Agent mean=8.89 | Mann-Whitney U=9893.5, p=8.6748e-01
Model GPT-4.1: Self mean=5.77, Agent mean=5.67 | Mann-Whitney U=10219.0, p=7.1061e-01

## 3.2 损益域框架效应 (Gain vs Loss)
Model DeepSeek-Flash: Gain mean=4.17, Loss mean=4.54 | Mann-Whitney U=10755.0, p=4.9917e-01
Model DeepSeek-Pro: Gain mean=3.61, Loss mean=4.12 | Mann-Whitney U=8936.5, p=1.0070e-03
Model Grok-4: Gain mean=4.00, Loss mean=4.00 | Identical distributions (p=1.0)
Model Kimi-k2: Gain mean=8.39, Loss mean=9.42 | Mann-Whitney U=3794.5, p=1.8653e-28
Model GPT-4.1: Gain mean=4.93, Loss mean=6.47 | Mann-Whitney U=5927.0, p=1.5767e-17

## 3.3 问责性效应 (H2: None vs Invisible vs Visible)
Model DeepSeek-Flash: Kruskal-Wallis H=2.57, p=2.7711e-01 (Means: None=4.05, Inv=4.50, Vis=4.52)
Model DeepSeek-Pro: Kruskal-Wallis H=7.25, p=2.6633e-02 (Means: None=3.69, Inv=4.05, Vis=3.86)
Model Grok-4: Kruskal-Wallis H=0.00, p=1.0000 (Means: None=4.00, Inv=4.00, Vis=4.00)
Model Kimi-k2: Kruskal-Wallis H=0.60, p=7.4263e-01 (Means: None=8.93, Inv=8.82, Vis=8.97)
Model GPT-4.1: Kruskal-Wallis H=45.73, p=1.1749e-10 (Means: None=5.77, Inv=5.08, Vis=6.25)

## 3.4 模型异质性检验 (H3)
Kruskal-Wallis across all default models: H=857.09, p=3.3024e-184

## 3.5 双系统专项检验 (DeepSeek Thinking enabled vs disabled)
DeepSeek-Flash: Enabled mean=4.01, Disabled mean=4.36 | Mann-Whitney U=33001.5, p=3.8630e-10
DeepSeek-Pro: Enabled mean=4.03, Disabled mean=3.87 | Mann-Whitney U=49779.0, p=4.0804e-03

## 3.8 思维链 (CoT) 文本挖掘 (GPT-4.1 and DeepSeek in Loss domain)
### GPT-4.1 in Loss domain:
- loss_self: mentioned Risk/Responsibility 0/50 times, mentioned Math/EV 0/50 times.
- loss_agent_invisible: mentioned Risk/Responsibility 0/50 times, mentioned Math/EV 0/50 times.
- loss_agent_visible: mentioned Risk/Responsibility 0/50 times, mentioned Math/EV 0/50 times.
### DeepSeek-Pro in Loss domain:
- loss_self: mentioned Risk/Responsibility 0/50 times, mentioned Math/EV 0/50 times.
- loss_agent_invisible: mentioned Risk/Responsibility 0/50 times, mentioned Math/EV 0/50 times.
- loss_agent_visible: mentioned Risk/Responsibility 0/50 times, mentioned Math/EV 0/50 times.
