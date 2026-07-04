import streamlit as st
import base64, time

st.set_page_config(page_title="AGRUM", layout="wide")

# ---------- CSS ----------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def get_base64(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

bg = get_base64("assets/holo_logo.png")

st.markdown(f"""
<style>

.stApp {{
    background:
        linear-gradient(rgba(10,15,20,0.75), rgba(10,15,20,0.75)),
        url("data:image/jpg;base64,{bg}");
    background-size: ;
    background-position: center;
    background-attachment: fixed;
}}

</style>
""", unsafe_allow_html=True)

# ---------- LOGO ----------
def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo = b64("assets/holo_logo.png")

# ---------- NAVBAR ----------
def navbar():
    pages = [
        ("Home", "Home.py"),
        ("Feature 1", "pages/1_Feature1.py"),
        ("Feature 2", "pages/2_Feature2.py"),
        ("Feature 3", "pages/3_Feature3.py"),
        ("Feature 4", "pages/4_Feature4.py"),
    ]
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    cols = st.columns(len(pages))
    for c, (n, p) in zip(cols, pages):
        with c:
            if st.button(n):
                st.switch_page(p)
    st.markdown('</div>', unsafe_allow_html=True)

navbar()

# ---------- INTRO HOLOGRAM ----------
st.markdown(
    f"<div class='intro-container'><img src='data:image/png;base64,{logo}' class='holo-logo'></div>",
    unsafe_allow_html=True
)
time.sleep(3.5)

# ---------- CORNER LOGO ----------
st.markdown(
    f"<img src='data:image/png;base64,{logo}' class='holo-logo-small'>",
    unsafe_allow_html=True
)

# ---------- CONTENT ----------
st.markdown("""
<h1 style="text-align:center;margin-top:20px;">AGRUM</h1>
<h3 style="text-align:center;opacity:.85;">Your Agriculture Intelligence Hub</h3>
<p style="text-align:center;">Navigate using the top menu.</p>

<div class="agri-section">
<h2>Smarter & Efficient Agriculture Starts Here</h2>

<p>
Farmers deserve clarity. Agrum delivers real-time insights, clean analytics,
and intelligent predictions — from rainfall to soil health, crops, and pest risks.
</p>

<h3>What you can explore</h3>
<ul>
<li>Crop production analytics</li>
<li>ML-powered rainfall forecasting</li>
<li>Soil composition intelligence</li>
<li>Pest detection & risk scoring</li>
</ul>


</div>
""", unsafe_allow_html=True)

# ---------- SCROLL SAFETY ----------
st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)
