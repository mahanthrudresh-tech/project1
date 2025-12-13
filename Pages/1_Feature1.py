import streamlit as st
import base64, requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide")

# ---------- CSS ----------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- LOGO ----------
def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.markdown(
    f"<img src='data:image/png;base64,{b64('assets/holo_logo.png')}' class='holo-logo-small'>",
    unsafe_allow_html=True
)

# ---------- NAVBAR ----------
def navbar():
    pages = [
        ("Home","Home.py"),
        ("Feature 1","pages/1_Feature1.py"),
        ("Feature 2","pages/2_Feature2.py"),
        ("Feature 3","pages/3_Feature3.py"),
        ("Feature 4","pages/4_Feature4.py"),
    ]
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    for c,(n,p) in zip(st.columns(len(pages)),pages):
        with c:
            if st.button(n):
                st.switch_page(p)
    st.markdown('</div>', unsafe_allow_html=True)

navbar()

# ---------- UI ----------
st.title("Rainfall Prediction (Outlier-Handled)")
st.write("Outliers replaced with median → prediction shown")

city = st.text_input("City")
state = st.text_input("State code")
country = st.text_input("Country code")

months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
start = st.selectbox("Start month", range(1,13), format_func=lambda x: months[x-1])
sel = [start, start%12+1, (start+1)%12+1]

# ---------- RUN ----------
if st.button("Run Prediction"):
    try:
        # ---- GEO ----
        geo = requests.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params={"q": f"{city},{state},{country}", "appid": "fdd8f6c0a72156ba6b0742cdb7bbc58e"}
        ).json()[0]

        # ---- RAIN DATA ----
        rain = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "start_date": "2006-11-29",
                "end_date": "2025-11-27",
                "daily": "rain_sum"
            }
        ).json()["daily"]

        df = pd.DataFrame({
            "date": pd.to_datetime(rain["time"]),
            "rain": rain["rain_sum"]
        })
        df["year"], df["month"] = df.date.dt.year, df.date.dt.month

        monthly = df.groupby(["year","month"])["rain"].sum().reset_index()

        def sum_3m(y):
            return monthly[
                (monthly.year == y) & (monthly.month.isin(sel))
            ]["rain"].sum()

        data = pd.DataFrame({
            "year": range(2007, 2026),
            "rain": [sum_3m(y) for y in range(2007, 2026)]
        }).dropna().reset_index(drop=True)

        # ---------- OUTLIER HANDLING ----------
        median_val = data["rain"].median()
        q1 = data["rain"].quantile(0.25)
        q3 = data["rain"].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr

        data["rain_clean"] = data["rain"]
        data.loc[
            (data["rain"] < low) | (data["rain"] > high),
            "rain_clean"
        ] = median_val

        # ---------- TRAIN / TEST ----------
        train = data[data.year < 2025]
        test = data[data.year == 2025]

        Xtr = train[["year"]].values
        ytr = train["rain_clean"].values
        Xte = test[["year"]].values

        sc = StandardScaler()
        Xtr, Xte = sc.fit_transform(Xtr), sc.transform(Xte)

        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(Xtr, ytr)

        prediction = model.predict(Xte)[0]
        actual = test["rain"].values[0]

        # ---------- OUTPUT ----------
        st.success("Prediction complete")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Predicted Value (mm)", f"{prediction:.2f}")
        with c2:
            st.metric("Actual Value (mm)", f"{actual:.2f}")

        st.subheader("Dataset Used (Outliers Replaced)")
        st.dataframe(
            data[["year","rain","rain_clean"]],
            use_container_width=True
        )

    except Exception as e:
        st.error(e)

st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)
