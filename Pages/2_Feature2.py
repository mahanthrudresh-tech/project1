import streamlit as st
import base64
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

st.set_page_config(layout="wide", page_title="fertiliser help")

# ---------- CSS ----------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Logo ----------
def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.markdown(
    f"<img src='data:image/png;base64,{b64('assets/holo_logo.png')}' class='holo-logo-small'>",
    unsafe_allow_html=True
)

# ---------- Navbar ----------
def navbar():
    pages = [
        ("Home", "Home.py"),
        ("Feature 1", "pages/1_Feature1.py"),
        ("Feature 2", "pages/2_Feature2.py"),
        
    ]

    st.markdown('<div class="top-nav">', unsafe_allow_html=True)

    cols = st.columns(len(pages))

    for col, (name, page) in zip(cols, pages):
        with col:
            if st.button(name):
                st.switch_page(page)

    st.markdown("</div>", unsafe_allow_html=True)

navbar()

# ======================================================
# Header
# ======================================================

st.title("fertiliser help")
st.caption("Give inputs to get fertiliser recommendations, as per the soil nutrient values and model predictions.")

# ---------- Load Dataset ----------
@st.cache_data
def load_data():
    return pd.read_csv("soil_data.csv")

try:
    df = load_data()
except:
    st.error("soil_data.csv not found")
    st.stop()

# ---------- Detect Columns ----------
def find_col(keys):
    for key in keys:
        for col in df.columns:
            if key.lower() in col.lower():
                return col
    return None

features = [find_col(["N"]), find_col(["P"]), find_col(["K"]), find_col(["pH"])]
features = [f for f in features if f]

if len(features) < 4:
    features = df.select_dtypes(include=np.number).columns[:4].tolist()

targets = {
    "soil": find_col(["soil"]),
    "crop": find_col(["crop"]),
    "fertilizer": find_col(["fertilizer", "fertiliser"])
}

# ---------- Clean Data ----------
X = (
    df[features]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(df[features].median())
)

# ---------- Train Models ----------
@st.cache_resource
def train_models():

    models, encoders, accuracy = {}, {}, {}

    for name, column in targets.items():

        if column is None:
            continue

        encoder = LabelEncoder()
        y = encoder.fit_transform(df[column].astype(str))

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = DecisionTreeClassifier(random_state=42)
        model.fit(X_train, y_train)

        models[name] = model
        encoders[name] = encoder
        accuracy[name] = accuracy_score(
            y_test,
            model.predict(X_test)
        )

    return models, encoders, accuracy

models, encoders, accuracy = train_models()



# ======================================================
# Dataset Explorer
# ======================================================
st.subheader("the dataset used for training the model")
with st.expander("View Dataset"):
    st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")

# ---------- Soil Input ----------
st.subheader("Soil Nutrient Input")

left, right = st.columns([2, 1])
base_values = {}

with left:
    cols = st.columns(2)

    for i, feature in enumerate(features):
        with cols[i % 2]:
            base_values[feature] = st.number_input(
                feature,
                value=float(X[feature].median()),
                step=0.1,
                format="%.2f"
            )

with right:
    st.info("""
### Tip

Adjust the nutrient values to match your soil sample as per the lab report. The model will provide recommendations based on these inputs.

Use the sliders below to simulate nutrient improvements, the model will show the changes real-time.
""")

st.markdown("---")

# ---------- Nutrient Optimizer ----------
st.subheader("Nutrient Optimizer")

slider_cols = st.columns(2)
rates = {}

for i, feature in enumerate(features):
    with slider_cols[i % 2]:
        rates[feature] = st.slider(
            f"{feature} Increase (%)",
            0,
            300,
            50
        )

scaled_values = {
    feature: base_values[feature] * (1 + rates[feature] / 100)
    for feature in features
}

st.markdown("---")

# ---------- Current vs Improved ----------
st.subheader("Current vs Improved Values")

comparison = pd.DataFrame({
    "Nutrient": features,
    "Current": [base_values[f] for f in features],
    "Improved": [scaled_values[f] for f in features]
})

c1, c2 = st.columns([1.4, 1])

with c1:
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

with c2:
    st.bar_chart(
        comparison.set_index("Nutrient")
    )

st.markdown("---")

# ---------- Soil Health ----------
st.subheader("Soil Health")

score = np.mean(list(scaled_values.values()))

if score < 25:
    health, color = "Poor","cannot support healthy crop growth",
elif score < 50:
    health, color = "Average","needs improvement"
elif score < 100:
    health, color = "Good","can go ahead with some improvements" 
else:
    health, color = "Excellent", "no issues"

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Average Nutrient", f"{score:.2f}")

with c2:
    st.metric("Health", f"{color} {health}")

with c3:
    st.metric("Improvement", f"{np.mean(list(rates.values())):.0f}%")

st.progress(min(score / 120, 1.0))

st.markdown("---")

# ---------- Prediction Function ----------
def predict(values):
    prediction, confidence = {}, {}
    vals = list(values.values())

    for name, model in models.items():
        pred = model.predict([vals])[0]
        prediction[name] = encoders[name].inverse_transform([pred])[0]

        if hasattr(model, "predict_proba"):
            confidence[name] = np.max(
                model.predict_proba([vals])
            ) * 100

    return prediction, confidence

# ---------- Prediction Mode ----------
st.subheader("AI Prediction")

mode = st.radio(
    "Prediction Source",
    ["Current Soil", "Improved Soil"],
    horizontal=True
)

input_data = (
    base_values
    if mode == "Current Soil"
    else scaled_values
)

predict_btn = st.button(
    "🚀 Generate Recommendation",
    use_container_width=True
)

st.markdown("---")

# ---------- Prediction Results ----------
if predict_btn:

    prediction, confidence = predict(input_data)

    st.success("Recommendation Generated")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🌱 Soil")
        st.metric(
            "Recommended Soil",
            prediction.get("soil", "-"),
            f"{confidence.get('soil',0):.1f}% Confidence"
        )

    with c2:
        st.markdown("### 🌾 Crop")
        st.metric(
            "Recommended Crop",
            prediction.get("crop", "-"),
            f"{confidence.get('crop',0):.1f}% Confidence"
        )

    with c3:
        st.markdown("### 🧪 Fertilizer")
        st.metric(
            "Recommended Fertilizer",
            prediction.get("fertilizer", "-"),
            f"{confidence.get('fertilizer',0):.1f}% Confidence"
        )

    st.markdown("---")

    # ---------- AI Summary ----------
    st.subheader("AI Recommendation Summary")

    st.info(f"""
### 🌾 Recommended Crop
**{prediction.get("crop","-")}**

### 🧪 Recommended Fertilizer
**{prediction.get("fertilizer","-")}**

### 🌱 Suitable Soil
**{prediction.get("soil","-")}**
""")

    st.markdown("---")

    # ---------- Feature Importance ----------
    st.subheader("Feature Importance")

    importance_cols = st.columns(len(models))

    for col, (name, model) in zip(importance_cols, models.items()):

        with col:

            st.markdown(f"**{name.title()} Model**")

            importance = pd.DataFrame({
                "Feature": features,
                "Importance": model.feature_importances_
            }).sort_values(
                "Importance",
                ascending=False
            )

            st.bar_chart(
                importance.set_index("Feature")
            )

    st.markdown("---")

    # ---------- AI Insights ----------
    st.subheader("AI Insights")

    highest = max(scaled_values, key=scaled_values.get)
    lowest = min(scaled_values, key=scaled_values.get)

    c1, c2 = st.columns(2)

    with c1:
        st.success(f"""
### Strongest Nutrient

**{highest}**

Current Value

**{scaled_values[highest]:.2f}**
""")

    with c2:
        st.warning(f"""
### Weakest Nutrient

**{lowest}**

Current Value

**{scaled_values[lowest]:.2f}**
""")

    st.markdown("---")

    # ---------- Nutrient Distribution ----------
    st.subheader("Nutrient Distribution")

    nutrient_df = pd.DataFrame({
        "Current": list(base_values.values()),
        "Improved": list(scaled_values.values())
    }, index=features)

    st.line_chart(nutrient_df)

    st.markdown("---")

    # ---------- Recommendation Tips ----------
    st.subheader("Suggested Improvements")

    tips = []

    if prediction.get("crop"):
        tips.append(f" Crop best suited: **{prediction['crop']}**")

    if prediction.get("fertilizer"):
        tips.append(f" Use **{prediction['fertilizer']}** for better nutrient balance.")

    if score < 50:
        tips.append("⚠ Soil health is relatively low. Consider adding organic compost.")

    elif score < 100:
        tips.append("Soil health is moderate. Small nutrient adjustments can improve yield.")
    else:
        tips.append(" Excellent nutrient profile. Maintain current soil management practices.")

    for tip in tips:
        st.write("•", tip)

    st.markdown("---")

# ---------- Footer ----------
st.caption(
    "Predictions are generated using Decision Tree models trained on the uploaded soil dataset. "
    "These recommendations are intended for educational purposes and should be validated with agricultural experts."
)

st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

# ---------- Export Prediction ----------
if predict_btn:

    st.markdown("---")
    st.subheader("Export Results")

    export_df = pd.DataFrame({
        "Prediction": [
            prediction.get("soil", ""),
            prediction.get("crop", ""),
            prediction.get("fertilizer", "")
        ],
        "Confidence (%)": [
            round(confidence.get("soil", 0), 2),
            round(confidence.get("crop", 0), 2),
            round(confidence.get("fertilizer", 0), 2)
        ]
    }, index=["Soil", "Crop", "Fertilizer"])

    csv = export_df.to_csv(index=True).encode()

    st.download_button(
        "⬇ Download Prediction Report",
        csv,
        file_name="prediction_report.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")

# ---------- Model Information ----------
st.subheader("Model Details")

model_df = pd.DataFrame({
    "Prediction Model": list(models.keys()),
    "Algorithm": ["Decision Tree"] * len(models),
    "Accuracy (%)": [
        round(score * 100, 2)
        for score in accuracy.values()
    ]
})

st.dataframe(
    model_df,
    hide_index=True,
    use_container_width=True
)

st.markdown("---")

# ---------- Feature Importance ----------
st.subheader("Feature Importance")

tabs = st.tabs([name.title() for name in models.keys()])

for tab, (name, model) in zip(tabs, models.items()):

    with tab:

        importance = pd.DataFrame({
            "Feature": features,
            "Importance": model.feature_importances_
        }).sort_values(
            "Importance",
            ascending=False
        )

        st.bar_chart(
            importance.set_index("Feature")
        )

        st.dataframe(
            importance,
            hide_index=True,
            use_container_width=True
        )

st.markdown("---")

# ---------- Dataset Statistics ----------
st.subheader("Dataset Statistics")

stats = df[features].describe().T

stats = stats[[
    "mean",
    "std",
    "min",
    "max"
]]

st.dataframe(
    stats,
    use_container_width=True
)

st.markdown("---")

# ---------- AI Suggestions ----------
st.subheader("AI Suggestions")

highest = max(scaled_values, key=scaled_values.get)
lowest = min(scaled_values, key=scaled_values.get)

st.info(f"""
### Analysis

• Highest nutrient: **{highest}**

• Lowest nutrient: **{lowest}**

• Soil Health: **{health}**

• Average Nutrient Value: **{score:.2f}**
""")

tips = []

if score < 25:
    tips.append("Increase organic manure to improve soil fertility.")
elif score < 50:
    tips.append("Balanced fertilizer application is recommended.")
elif score < 100:
    tips.append("Current soil condition is suitable for most crops.")
else:
    tips.append("Excellent nutrient profile. Maintain the current soil management.")

tips.append("Perform soil testing every season for better recommendations.")
tips.append("Use organic compost to improve long-term soil health.")

for tip in tips:
    st.success(tip)

st.markdown("---")

# ---------- About ----------
with st.expander("About this Model"):

    st.markdown("""
### Soil → Crop → Fertiliser Predictor

This module predicts:

- Soil Type
- Suitable Crop
- Recommended Fertilizer

using Decision Tree Classification trained on the provided dataset.

The application is intended for educational and demonstration purposes.
""")

st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)