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
# ---------- LOGO ----------
def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = b64("assets/rain.png")   # <-- Add this line

st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(rgba(0,0,0,0.42), rgba(0,0,0,0.42)),
        url("data:image/png;base64,{bg}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
""",
    unsafe_allow_html=True
)
# ---------- NAVBAR ----------
def navbar():
    pages = [
        ("Home","Home.py"),
        ("Rain-prediction model","pages/1_Feature1.py"),
        ("Fertilizer recommendation","pages/2_Feature2.py"),
        
    ]
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    for c,(n,p) in zip(st.columns(len(pages)),pages):
        with c:
            if st.button(n):
                st.switch_page(p)
    st.markdown('</div>', unsafe_allow_html=True)

navbar()

# ---------- UI ----------
st.title("Rainfall Prediction System")
st.write("Predict rainfall for a 3-month period based on historical data.")

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
            params={
                "q": f"{city},{state},{country}",
                "appid": "fdd8f6c0a72156ba6b0742cdb7bbc58e"
            }
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

        df["year"] = df.date.dt.year
        df["month"] = df.date.dt.month

        monthly = df.groupby(["year","month"])["rain"].sum().reset_index()

        def sum_3m(y):
            return monthly[
                (monthly.year == y) &
                (monthly.month.isin(sel))
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
            (data["rain"] < low) |
            (data["rain"] > high),
            "rain_clean"
        ] = median_val
        # ---------- OUTLIERS DETECTED ----------
        outliers = data[
        (data["rain"] < low) | (data["rain"] > high)
        ][["year", "rain"]]

        # ---------- TRAIN / TEST ----------
        train = data[data.year < 2025]
        test = data[data.year == 2025]

        Xtr = train[["year"]].values
        ytr = train["rain_clean"].values
        Xte = test[["year"]].values

        sc = StandardScaler()
        Xtr = sc.fit_transform(Xtr)
        Xte = sc.transform(Xte)

        model = RandomForestRegressor(
            n_estimators=200,
            random_state=42
        )

        model.fit(Xtr, ytr)

        prediction = model.predict(Xte)[0]
        actual = test["rain"].values[0]

        # ---------- ACCURACY ----------
        mae = abs(actual - prediction)
        rmse = np.sqrt((prediction - actual) ** 2)

        if actual != 0:
            mape = (mae / actual) * 100
            accuracy = max(0, 100 - mape)
        else:
            mape = 0
            accuracy = 0

        # ---------- OUTPUT ----------
        st.success("Prediction Complete")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Predicted Rainfall",
                f"{prediction:.2f} mm"
            )

        with c2:
            st.metric(
                "Actual Rainfall",
                f"{actual:.2f} mm"
            )

        with c3:
            st.metric(
                "Prediction Accuracy",
                f"{accuracy:.2f}%"
            )

        with c4:
            st.metric(
                "RMSE",
                f"{rmse:.2f}"
            )
        # ---------- PREDICTION DETAILS ----------
        month_names = [
                "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December"
                    ]

        selected_months = [month_names[m - 1] for m in sel]

        st.subheader("Prediction Details")

        st.info(
            f"""
        **Selected Months:** {selected_months[0]}, {selected_months[1]}, {selected_months[2]}
        
        **Prediction Year:** 2025

        **Training Data:** 2007–2024

        **Testing Data:** Actual rainfall recorded during {selected_months[0]}, {selected_months[1]}, and {selected_months[2]} of 2025.

        The predicted rainfall shown above is for these selected three months in **2025**, and it is compared with the actual recorded rainfall for the same months in 2025.
        """
                )    

        st.subheader("the complete rainfall data for the selected months across the years 2007–2025 is shown below:, the model was trained on the data from 2007–2024 and tested on the actual rainfall data for 2025.")
        st.dataframe(
            data[["year","rain","rain_clean"]],
            use_container_width=True
        )
        st.subheader("Outlier Handling")

        if outliers.empty:
            st.success("No outliers were detected for the selected three-month period.")
        else:
            st.warning(
            f"{len(outliers)} outlier(s) were detected and replaced with the median rainfall "
                f"({median_val:.2f} mm) before training."
        )

        st.dataframe(
        outliers.rename(columns={
            "year": "Year",
            "rain": "Original Rainfall (mm)"
        }),
        use_container_width=True
        )
        st.subheader("Rainfall values that fall outside the Interquartile Range (IQR) bounds are treated as outliers. These extreme values are replaced with the median rainfall before training the model. This prevents unusually wet or dry years from dominating the learning process while still preserving the overall rainfall trend. The table above lists all years that were identified and corrected for the selected three-month period..")
       

    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)