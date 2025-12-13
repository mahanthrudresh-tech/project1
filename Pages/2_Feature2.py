import streamlit as st
import base64
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

st.set_page_config(layout="wide", page_title="Soil → Crop → Fertiliser")

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
    cols = st.columns(len(pages))
    for c,(n,p) in zip(cols,pages):
        with c:
            if st.button(n):
                st.switch_page(p)
    st.markdown('</div>', unsafe_allow_html=True)

navbar()

# ---------- HEADER ----------
st.title("Soil → Crop → Fertiliser Predictor")
st.write("Simple ML predictions using soil nutrient composition.")

# ---------- LOAD DATA ----------
DATA = "soil_data.csv"
try:
    df = pd.read_csv(DATA)
except:
    st.error("soil_data.csv not found")
    st.stop()

st.subheader("Dataset")
st.dataframe(df, use_container_width=True)

# ---------- COLUMN DETECTION ----------
def find_col(keys):
    for k in keys:
        for c in df.columns:
            if k.lower() in c.lower():
                return c

features = [find_col([x]) for x in ["N","P","K","pH"]]
features = [f for f in features if f]

if len(features) < 4:
    features = df.select_dtypes("number").columns[:4].tolist()

targets = {
    "soil": find_col(["soil"]),
    "crop": find_col(["crop"]),
    "fertilizer": find_col(["fertilizer","fertiliser"])
}

X = df[features].apply(pd.to_numeric, errors="coerce").fillna(df[features].median())

# ---------- TRAIN MODELS ----------
models, encoders, acc = {}, {}, {}

for k,col in targets.items():
    if not col: continue
    y_raw = df[col].astype(str)
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=0)
    m = DecisionTreeClassifier(random_state=0).fit(Xtr,ytr)
    models[k], encoders[k] = m, le
    acc[k] = accuracy_score(yte,m.predict(Xte))

# ---------- ACCURACY ----------
st.subheader("Model Accuracy")
cols = st.columns(len(acc))
for c,(k,v) in zip(cols,acc.items()):
    with c:
        st.metric(k.title(), f"{v*100:.2f}%")

# ---------- SLIDERS ----------
st.subheader("Nutrient Increase (%)")
rates = {
    f: st.slider(f,0,300,50)
    for f in features
}

# ---------- INPUT ----------
st.subheader("Predict")
base = [
    st.number_input(f, value=float(X[f].median()))
    for f in features
]

scaled = [base[i]*(1+rates[f]/100) for i,f in enumerate(features)]

c1,c2 = st.columns(2)

def predict(vals):
    out={}
    for k,m in models.items():
        p = encoders[k].inverse_transform([m.predict([vals])[0]])[0]
        out[k]=p
    return out

with c1:
    if st.button("Predict (Base)"):
        r=predict(base)
        st.success("Base Prediction")
        st.write(r)

with c2:
    if st.button("Predict (With Increases)"):
        r=predict(scaled)
        st.success("Scaled Prediction")
        st.write(r)

st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)
