import streamlit as st
import base64
from PIL import Image

st.set_page_config(layout="wide")

# ---------- CSS ----------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- HELPERS ----------
def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

def pest_img(name):
    try:
        return Image.open(f"assets/pests/{name}.png")
    except:
        return None

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

st.markdown(
    f"<img src='data:image/png;base64,{b64('assets/holo_logo.png')}' class='holo-logo-small'>",
    unsafe_allow_html=True
)

# ---------- RULE ENGINE ----------
def predict(crop, leaf, dmg):
    c,l,d = crop.lower(),leaf.lower(),dmg.lower()

    rules = [
        (c in ["rice","paddy"] and "yellow" in l and "spots" in d, "Brown Plant Hopper"),
        (c in ["rice","paddy"] and ("cut" in d or "eaten" in d), "Rice Stem Borer"),
        (c=="cotton" and "holes" in d, "Pink Bollworm"),
        (c=="cotton" and "curl" in l, "Whitefly"),
        (c=="tomato" and "spots" in d, "Leaf Miner"),
        (c=="tomato" and "holes" in d, "Fruit Borer"),
        (c=="tomato" and "white" in l, "Whiteflies"),
        (c=="wheat" and "yellow" in l, "Aphids"),
        (c=="wheat" and "brown" in d, "Armyworm"),
        (c in ["maize","corn"] and "holes" in d, "Fall Armyworm"),
        (c in ["maize","corn"] and "wilt" in l, "Corn Borer"),
        ("holes" in d, "Caterpillar / Armyworm"),
        ("spots" in d, "Leaf Miner or Fungal Infection"),
        ("yellow" in l, "Aphids or Nutrient Deficiency"),
    ]
    for cond,res in rules:
        if cond: return res
    return "Pest not identifiable"

pesticide = {
    "Brown Plant Hopper":"Imidacloprid / Buprofezin",
    "Rice Stem Borer":"Chlorantraniliprole / Cartap",
    "Pink Bollworm":"Emamectin Benzoate",
    "Whitefly":"Acetamiprid / Thiamethoxam",
    "Leaf Miner":"Abamectin / Spinosad",
    "Fruit Borer":"Cypermethrin / Lambda-cyhalothrin",
    "Whiteflies":"Imidacloprid / Neem Oil",
    "Aphids":"Neem Oil / Imidacloprid",
    "Armyworm":"Chlorpyrifos / Cypermethrin",
    "Fall Armyworm":"Spinosad / Emamectin Benzoate",
    "Corn Borer":"Carbaryl / Cypermethrin",
    "Caterpillar / Armyworm":"Chlorpyrifos / Emamectin",
    "Leaf Miner or Fungal Infection":"Spinosad / Mancozeb",
    "Aphids or Nutrient Deficiency":"Imidacloprid / Nitrogen"
}

# ---------- UI ----------
st.title("Pest Prediction System")

crop = st.selectbox("Crop", ["rice","wheat","cotton","tomato","maize"])
leaf = st.selectbox("Leaf Color", ["yellow","brown","green","white patches"])
dmg  = st.selectbox("Damage Type", ["holes","spots","cut marks","curling"])
season = st.selectbox("Season", ["kharif","rabi","summer","winter"])

if st.button("Predict Pest"):
    pest = predict(crop,leaf,dmg)
    st.success(f"Predicted Pest: **{pest}**")

    img = pest_img(pest)
    if img: st.image(img, caption=pest, use_column_width=True)

    ok = st.radio("Is this correct?", ["Yes","No"], horizontal=True)

    if ok == "Yes":
        st.info(f"Pesticide: **{pesticide.get(pest,'No data')}**")
    else:
        st.warning("Refine inputs")
        crop = st.selectbox("Correct Crop", ["rice","wheat","cotton","tomato","maize"])
        leaf = st.selectbox("Correct Leaf Color", ["yellow","brown","green","white patches"])
        dmg  = st.selectbox("Correct Damage", ["holes","spots","cut marks","curling"])

        if st.button("Recalculate"):
            p2 = predict(crop,leaf,dmg)
            st.success(f"Updated Pest: **{p2}**")
            img2 = pest_img(p2)
            if img2: st.image(img2, caption=p2, use_column_width=True)
            st.info(f"Pesticide: **{pesticide.get(p2,'No data')}**")

st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)
