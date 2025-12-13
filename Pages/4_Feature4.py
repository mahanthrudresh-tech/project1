import streamlit as st
import base64
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------- CSS ----------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- LOGO ----------
def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo = b64("assets/holo_logo.png")

# ---------- NAVBAR ----------
def navbar():
    pages = [
        ("Home","Home.py"),
        ("Feature 1","pages/1_Feature1.py"),
        ("Feature 2","pages/2_Feature2.py"),
        ("Feature 3","pages/3_Feature3.py"),
        ("Feature 4",None),
    ]
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    for c,(n,p) in zip(st.columns(len(pages)),pages):
        with c:
            if st.button(n) and p:
                st.switch_page(p)
    st.markdown('</div>', unsafe_allow_html=True)

navbar()

st.markdown(
    f"<img src='data:image/png;base64,{logo}' class='holo-logo-small'>",
    unsafe_allow_html=True
)

# ---------- TITLE ----------
st.title("Crop Production Insights Dashboard")
st.write("Explore crop trends, yields, and performance.")

# ---------- DATA ----------
df = pd.read_csv("crop_sample.csv")
df["yield_t_per_ha"] = df.production_tonnes / df.area_hectares

# ---------- SUMMARY ----------
year_prod = df.groupby("year").production_tonnes.sum()
top_crops = df.groupby("crop").production_tonnes.sum().nlargest(2)

c1,c2 = st.columns(2)
with c1:
    st.markdown(
        f"<div class='glass-card'><h3>Highest Production Year</h3>"
        f"<p><b>{int(year_prod.idxmax())}</b></p>"
        f"<p>{year_prod.max():.2f} tonnes</p></div>",
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"<div class='glass-card'><h3>Top Producing Crops</h3>"
        f"<p>1. {top_crops.index[0]} — {top_crops.iloc[0]:.2f} t</p>"
        f"<p>2. {top_crops.index[1]} — {top_crops.iloc[1]:.2f} t</p></div>",
        unsafe_allow_html=True
    )

# ---------- CHARTS ----------
st.plotly_chart(
    px.bar(
        df.groupby("year").production_tonnes.mean().reset_index(),
        x="year", y="production_tonnes",
        title="📈 Average Production per Year"
    ),
    use_container_width=True
)

st.plotly_chart(
    px.pie(
        df.groupby("crop").production_tonnes.sum().reset_index(),
        names="crop", values="production_tonnes",
        title="Total Production Share by Crop"
    ),
    use_container_width=True
)

# ---------- STATE INSIGHTS ----------
st.subheader("🌾 State-wise Insights")
state = st.text_input("Enter your state name")

if state:
    s = df[df.state.str.lower() == state.lower()]
    if s.empty:
        st.error("No data found for this state.")
    else:
        st.write("### Recent 10 Years")
        st.dataframe(
            s.sort_values("year", ascending=False).head(10),
            use_container_width=True
        )

        stats = (
            s.groupby("crop")[["production_tonnes","area_hectares","yield_t_per_ha"]]
            .mean()
            .sort_values("yield_t_per_ha", ascending=False)
        )

        st.write("### Average Yield per Crop")
        st.dataframe(stats, use_container_width=True)

        best = stats.iloc[0]
        st.success(
            f"**Suggested Crop:** {stats.index[0]}  \n"
            f"**Avg Yield:** {best.yield_t_per_ha:.2f} t/ha",
            icon="✨"
        )

# ---------- SCROLL ----------
st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)
