# 序列效应稳健性检验结果（DeepSeek）

## 检验方法

- Mann-Whitney U 检验（双侧）
- Bonferroni 校正阈值：α' = 0.05/12 = 0.0042
- 效应量：rank-biserial r = 1 − 2U/(n₁·n₂)

## 逐条件检验结果

| 模型 | 条件 | Batch均值 | Single均值 | Δ | U | p | Sig. | r | Bonf. |
|------|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| DeepSeek-Flash | gain_agent_invisible | 4.14 | 5.20 | +1.06 | 197.0 | 0.2748 | n.s. | +0.212 | N |
| DeepSeek-Flash | gain_agent_visible | 4.46 | 6.60 | +2.14 | 107.5 | 0.0042 | ** | +0.570 | N |
| DeepSeek-Flash | gain_self | 3.92 | 5.30 | +1.38 | 151.0 | 0.0448 | * | +0.396 | N |
| DeepSeek-Flash | loss_agent_invisible | 4.86 | 4.50 | -0.36 | 257.0 | 0.8954 | n.s. | -0.028 | N |
| DeepSeek-Flash | loss_agent_visible | 4.58 | 4.50 | -0.08 | 255.5 | 0.9188 | n.s. | -0.022 | N |
| DeepSeek-Flash | loss_self | 4.18 | 3.30 | -0.88 | 317.5 | 0.1747 | n.s. | -0.270 | N |
| DeepSeek-Pro | gain_agent_invisible | 3.74 | 7.60 | +3.86 | 8.5 | 0.0000 | *** | +0.966 | Y |
| DeepSeek-Pro | gain_agent_visible | 3.74 | 6.90 | +3.16 | 5.5 | 0.0000 | *** | +0.978 | Y |
| DeepSeek-Pro | gain_self | 3.36 | 6.30 | +2.94 | 4.0 | 0.0000 | *** | +0.984 | Y |
| DeepSeek-Pro | loss_agent_invisible | 4.36 | 7.10 | +2.74 | 27.5 | 0.0000 | *** | +0.890 | Y |
| DeepSeek-Pro | loss_agent_visible | 3.98 | 9.10 | +5.12 | 8.5 | 0.0000 | *** | +0.966 | Y |
| DeepSeek-Pro | loss_self | 4.02 | 7.30 | +3.28 | 21.0 | 0.0000 | *** | +0.916 | Y |

