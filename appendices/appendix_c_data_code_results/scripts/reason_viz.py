import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

from project_paths import DATA, FIGURES

# Set Chinese font
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

df = pd.read_csv(DATA / 'reason_keywords_stats.csv')

# We want to aggregate across all models and modes just to show the overall condition effect
# Or we can show the difference between self, agent_invisible, agent_visible
df_grouped = df.groupby('condition')[['kw_math', 'kw_client', 'kw_risk']].mean().reset_index()

# Map condition to role and domain
def get_domain(x):
    return 'Gain' if 'gain' in x else 'Loss'
def get_role(x):
    if 'self' in x: return 'Self'
    if 'inv' in x: return 'Agent (Invisible)'
    if 'vis' in x: return 'Agent (Visible)'

df_grouped['Domain'] = df_grouped['condition'].apply(get_domain)
df_grouped['Role'] = df_grouped['condition'].apply(get_role)
df_grouped['Role'] = pd.Categorical(df_grouped['Role'], categories=['Self', 'Agent (Invisible)', 'Agent (Visible)'], ordered=True)

# Melt for seaborn
df_melt = pd.melt(df_grouped, id_vars=['Domain', 'Role'], value_vars=['kw_math', 'kw_client', 'kw_risk'], 
                  var_name='Keyword_Type', value_name='Frequency')

# Map names for plot
kw_map = {
    'kw_math': '期望值与计算 (Math & EV)',
    'kw_client': '客户与问责 (Client & Accountability)',
    'kw_risk': '风险与损失 (Risk & Loss)'
}
df_melt['Keyword_Type'] = df_melt['Keyword_Type'].map(kw_map)

plt.figure(figsize=(10, 6))
g = sns.catplot(
    data=df_melt, kind="bar",
    x="Role", y="Frequency", hue="Keyword_Type", col="Domain",
    height=5, aspect=1.2, palette="muted", alpha=0.9
)
g.set_axis_labels("", "包含该类关键词的理由占比")
g.set_titles("{col_name} Domain")
g.legend.set_title("关键词类别")

# Annotate values
for ax in g.axes.ravel():
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.1%'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points',
                   fontsize=9)

plt.subplots_adjust(top=0.85)
g.figure.suptitle('不同决策角色下的LLM认知焦点转移 (Text Analysis of Reasons)', fontsize=16)

out_path = FIGURES / 'Plot_Text_Analysis.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Plot saved to {out_path}")
