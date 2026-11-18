# 修订补充统计检验结果

本文件为报告修订后新增的最终补充检验，优先级高于早期探索性统计摘要。

## 收益域内H1检验（置换检验，双侧）

- DeepSeek-V4-Flash: Self=3.92, Inv=4.14 (Delta=+0.22, p=0.6979, q_BH=0.9970), Vis=4.46 (Delta=+0.54, p=0.3139, q_BH=0.6279)
- DeepSeek-V4-Pro: Self=3.36, Inv=3.74 (Delta=+0.38, p=0.1337, q_BH=0.3344), Vis=3.74 (Delta=+0.38, p=0.1116, q_BH=0.3344)
- Grok-4: Self=4.00, Inv=4.00 (Delta=+0.00, p=1.0000, q_BH=1.0000), Vis=4.00 (Delta=+0.00, p=1.0000, q_BH=1.0000)
- Kimi-k2: Self=8.48, Inv=8.14 (Delta=-0.34, p=0.4197, q_BH=0.6995), Vis=8.56 (Delta=+0.08, p=0.8422, q_BH=1.0000)
- GPT-4.1: Self=4.92, Inv=4.66 (Delta=-0.26, p=0.0037, q_BH=0.0187), Vis=5.22 (Delta=+0.30, p=0.0001, q_BH=0.0010)

## H2差中差检验（Agent条件内；置换检验，双侧）

- DeepSeek-V4-Flash: Gain Vis-Inv=+0.32, Loss Vis-Inv=-0.28, DiD=-0.60, p=0.4580, q_BH=0.5725
- DeepSeek-V4-Pro: Gain Vis-Inv=+0.00, Loss Vis-Inv=-0.38, DiD=-0.38, p=0.3989, q_BH=0.5725
- Grok-4: Gain Vis-Inv=+0.00, Loss Vis-Inv=+0.00, DiD=+0.00, p=1.0000, q_BH=1.0000
- Kimi-k2: Gain Vis-Inv=+0.42, Loss Vis-Inv=-0.12, DiD=-0.54, p=0.2662, q_BH=0.5725
- GPT-4.1: Gain Vis-Inv=+0.56, Loss Vis-Inv=+1.78, DiD=+1.22, p=0.0051, q_BH=0.0255

正文与表格以 Benjamini-Hochberg 校正后的 q_BH 作为多重比较后的显著性判断依据。
