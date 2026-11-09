import pandas as pd
import streamlit as st

st.set_page_config(page_title="Recession Shopping Signals", layout="wide")

st.title("Recession Shopping Signals")
st.write("Can Google searches predict Canadian retail spending before Statistics Canada publishes it?")

# 1. This month's nowcasts
now = pd.read_csv("nowcasts.csv", parse_dates=["month", "latest_published"])
latest = now["latest_published"].max()

st.subheader("This month's nowcasts")
st.caption(f"Based on StatCan data up to {latest:%B %Y}. Updates automatically on the 25th of each month.")

names = {"health": "Health & personal care", "clothing": "Clothing", "cars": "Cars & parts"}
cols = st.columns(3)
for col, (key, label) in zip(cols, names.items()):
    col.markdown(f"**{label}**")
    for _, r in now[now["category"] == key].sort_values("month").iterrows():
        col.metric(f"{r['month']:%B %Y}", f"${r['nowcast'] / 1e6:.2f}B")

# 2. The headline chart
st.subheader("Google searches vs. a simple rule: Canadian car sales, 2008 to 2026")
chart = pd.read_csv("chart_cars.csv", parse_dates=["month"]).set_index("month") / 1e6
chart = chart.rename(columns={"actual": "Real sales", "baseline": "Seasonal rule", "model": "Google model"})
st.line_chart(chart, y_label="Monthly sales ($ billions)")

# 3. The finding
st.subheader("What I found")
st.write(
    "I tested whether Google searches improve monthly estimates of Canadian retail sales "
    "for health and personal care, clothing, and cars, using walk-forward testing from 2008 to 2026. "
    "A simple seasonal rule (last month, adjusted by how that month changed last year) won in every category, "
    "even when using Google's search categories and Ridge regression. "
    "Search signals were real but tiny, and in 2008 the model had never seen a recession to learn from."
)
st.table(pd.DataFrame({
    "Category": ["Health & personal care", "Clothing", "Cars"],
    "Seasonal rule error": ["2.66%", "7.43%", "6.93%"],
    "Best Google model error": ["2.77%", "7.72%", "7.00%"],
}))
