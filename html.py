import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


file_path = r'C:\Users\DELL\Desktop\工作簿1.xlsx'  
df = pd.read_excel(file_path)

if df.shape[1] < 3:
    raise ValueError("Excel 至少需要三列：生物名、数量、站位")

species_col = df.columns[0]
abundance_col = df.columns[1]
station_col = df.columns[2]

df = df[[species_col, abundance_col, station_col]].dropna()
df[abundance_col] = pd.to_numeric(df[abundance_col], errors='coerce')
df = df.dropna()


pivot = df.pivot_table(
    index=species_col,
    columns=station_col,
    values=abundance_col,
    aggfunc='sum',
    fill_value=0
)

pivot['Total'] = pivot.sum(axis=1)
pivot = pivot.sort_values('Total', ascending=False)
pivot = pivot.drop(columns='Total')

species_list = pivot.index.tolist()
stations = pivot.columns.tolist()
N = len(species_list)

theta_deg = np.linspace(0, 360, N, endpoint=False)


fig = go.Figure()

hover_template = (
    "<b>%{customdata[0]}</b><br>" +
    "站位: %{customdata[1]}<br>" +
    "数量: %{r}<extra></extra>"
)

bottom = np.zeros(N)
for station in stations:
    values = pivot[station].values
    customdata = [[species, station] for species in species_list]
    
    fig.add_trace(go.Barpolar(
        r=values,
        theta=theta_deg,
        name=str(station),
        hovertemplate=hover_template,
        customdata=customdata,
        base=bottom,
        width=360 / N * 0.8
    ))
    bottom += values

# 设置颜色
colors = px.colors.qualitative.Bold * 10
for i, trace in enumerate(fig.data):
    trace.marker.color = colors[i % len(colors)]


fig.update_layout(
    title={
        'text': "各站位生物数量分布（环形堆叠图）",
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    font=dict(size=12),
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, bottom.max() * 1.1],
            # 允许用户缩放径向轴
            autorange=False
        ),
        angularaxis=dict(
            tickmode='array',
            tickvals=theta_deg,
            ticktext=species_list,
            rotation=90,
            direction="clockwise"
        )
    ),
    legend=dict(
        title="站位",
        orientation="v",
        yanchor="top",
        y=0.95,
        xanchor="left",
        x=1.0
    ),
    height=800,
    width=900,
    # 🔑 关键：启用滚轮缩放和拖拽缩放
    dragmode='zoom'  # 或 'select', 但 'zoom' 支持滚轮
)

# 🔑 启用滚轮缩放（通过 config）
config = {
    'scrollZoom': True,      # 允许滚轮缩放
    'displayModeBar': True,  # 显示工具栏（包含重置缩放按钮）
    'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'resetScale2d']
}


output_file = '环形生物堆叠图.html'
fig.write_html(
    output_file,
    config=config,
    include_plotlyjs='cdn'
)

print(f"✅ 交互式图表已保存为: {output_file}")
print("🖱️  支持：")
print("   - 鼠标悬停：显示生物名、站位、数量")
print("   - 滚轮：缩放径向轴（放大/缩小数量范围）")
print("   - 拖拽：框选区域放大（按住鼠标左键拖动）")
print("   - 工具栏：可重置缩放")