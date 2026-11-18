import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

from project_paths import DATA, FIGURES

# Set Chinese font
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

df = pd.read_csv(DATA / 'reason_keywords_stats.csv')

# Filter for the 3 representative models
rep_models = ['grok:grok-4', 'kimi:kimi-k2-250905', 'openai:gpt-4.1']
df_rep = df[df['model'].isin(rep_models)].copy()

# Map model names for display
model_map = {
    'grok:grok-4': 'Grok-4 (绝对理性型)',
    'kimi:kimi-k2-250905': 'Kimi-k2 (极度保守型)',
    'openai:gpt-4.1': 'GPT-4.1 (情境敏感型)'
}
df_rep['Model_Name'] = df_rep['model'].map(model_map)

# Map condition to Role
def get_role(x):
    if 'self' in x: return 'Self'
    if 'inv' in x: return 'Agent (Inv)'
    if 'vis' in x: return 'Agent (Vis)'
df_rep['Role'] = df_rep['condition'].apply(get_role)
df_rep['Role'] = pd.Categorical(df_rep['Role'], categories=['Self', 'Agent (Inv)', 'Agent (Vis)'], ordered=True)

# We want to show how different models focus on different things
# Aggregate across domains (Gain/Loss) to simplify, or just show everything.
# Let's aggregate across Gain/Loss and Mode to get the average focus per role per model
df_agg = df_rep.groupby(['Model_Name', 'Role'])[['kw_math', 'kw_client', 'kw_risk']].mean().reset_index()

# Melt for seaborn
df_melt = pd.melt(df_agg, id_vars=['Model_Name', 'Role'], value_vars=['kw_math', 'kw_client', 'kw_risk'], 
                  var_name='Keyword_Type', value_name='Frequency')

kw_map = {
    'kw_math': '期望值与计算 (Math & EV)',
    'kw_client': '客户与问责 (Client & Accountability)',
    'kw_risk': '风险与损失 (Risk & Loss)'
}
df_melt['Keyword_Type'] = df_melt['Keyword_Type'].map(kw_map)

# Plot
g = sns.catplot(
    data=df_melt, kind="bar",
    x="Role", y="Frequency", hue="Keyword_Type", col="Model_Name",
    height=4.5, aspect=1.1, palette="Set2", alpha=0.9
)
g.set_axis_labels("", "词频占比")
g.set_titles("{col_name}")
g.legend.set_title("关键词类别")
g.set(ylim=(0, 1.1))

# Annotate values
for ax in g.axes.ravel():
    for p in ax.patches:
        height = p.get_height()
        if pd.notnull(height) and height > 0:
            ax.annotate(format(height, '.1%'), 
                       (p.get_x() + p.get_width() / 2., height), 
                       ha = 'center', va = 'center', 
                       xytext = (0, 7), 
                       textcoords = 'offset points',
                       fontsize=8)

plt.subplots_adjust(top=0.85)
g.figure.suptitle('不同行为原型模型的思维链特征差异 (Text Analysis by Model)', fontsize=15)

out_path = FIGURES / 'Plot_K_Text_Models.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Plot saved to {out_path}")
