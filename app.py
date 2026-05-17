# =========================================================
# IMPORTS
# =========================================================
import numpy as np
import pickle as pk
import streamlit as st
import base64
import hashlib
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Fuel Consumption Prediction",
    page_icon="⛽",
    layout="wide"
)
# BACKGROUND FUNCTION
# =================================================
def set_bg(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background:linear-gradient(rgba(0,0,0,.8),rgba(0,0,0,.9)),
        url(data:image/png;base64,{encoded});
        background-size:cover;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# LOAD MODEL & SCALER (KEEP YOUR PATHS)
# =========================================================
loaded_model = pk.load(open(r"C:\Users\DELL\Desktop\FUEL_CONSUMPTION_ANALYSIS-main\trained_model_lr.sav","rb"))
scaled_data = pk.load(open(r"C:\Users\DELL\Desktop\FUEL_CONSUMPTION_ANALYSIS-main\scaled_data.sav", "rb"))

# =========================================================
# SESSION STATE INIT
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    set_bg(r"C:\Users\DELL\Desktop\FUEL_CONSUMPTION_ANALYSIS-main\Fuel.png")

# =========================================================
# AUTH DATABASE (DEMO – CAN MOVE TO SQLITE LATER)
# =========================================================
USERS = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin"
    },
    "user": {
        "password": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user"
    }
}

# =========================================================
# AUTH FUNCTIONS
# =========================================================
def authenticate(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if username in USERS and USERS[username]["password"] == hashed:
        return USERS[username]["role"]
    return None

def login_page():
    st.markdown(
        """
        <h1 style="text-align:center; color:white;">🔐 Fuel Consumption Prediction </h1>
        <p style="text-align:center; color:#cbd5f5;">
            Machine Learning App to Predict Vehicle Fuel Consumption
        </p>
        """,
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login 🚀")

    if login_btn:
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Welcome {username} ({role.upper()}) 🎉")
            st.rerun()
        else:
            st.error("❌ Invalid Username or Password")

# =========================================================
# GLOBAL UI STYLE
# =========================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
    background: radial-gradient(circle at top left, #1f2933, #020617);
    color: white;
}

.glass-card {
    background: rgba(15,23,42,0.85);
    border-radius: 24px;
    padding: 24px;
    border: 1px solid rgba(148,163,184,0.4);
    box-shadow: 0 18px 45px rgba(0,0,0,0.6);
    backdrop-filter: blur(18px);
}

.app-title {
    font-size: 2.4rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg,#38bdf8,#22c55e,#eab308);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.result-card {
    padding: 1.2rem;
    border-radius: 18px;
    background: radial-gradient(circle at top left, rgba(56,220,220,.25), rgba(15,223,20 2,.95));
    border: 1px solid rgba(56,225,225,.6);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MODEL INPUT CONVERTER (UNCHANGED LOGIC)
# =========================================================
def input_converter(inp):
    vcl = ['Two-seater','Minicompact','Compact','Subcompact','Mid-size','Full-size',
           'SUV: Small','SUV: Standard','Minivan','Station wagon: Small',
           'Station wagon: Mid-size','Pickup truck: Small',
           'Special purpose vehicle','Pickup truck: Standard']
    trans = ['AV','AM','M','AS','A']
    fuel = ["D","P","G","C"]

    lst = []
    lst.append(vcl.index(inp[0]))
    lst.append(inp[1])
    lst.append(inp[2])
    lst.append(trans.index(inp[3]))
    lst.append(inp[4])

    fuel_encoding = [0]*4
    fuel_encoding[fuel.index(inp[5])] = 1
    lst.extend(fuel_encoding)

    arr = np.asarray(lst).reshape(1,-1)
    arr = scaled_data.transform(arr)
    prediction = loaded_model.predict(arr)

    return round(prediction[0],2)

# =========================================================
# MAIN APPLICATION
# =========================================================
def main():

    # Sidebar
    st.sidebar.markdown(f"👤 **{st.session_state.username}** ({st.session_state.role})")
    set_bg(r"C:\Users\DELL\Desktop\FUEL_CONSUMPTION_ANALYSIS-main\images\image.jpg")

    if st.sidebar.button("Logout 🔓"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="app-title">Fuel Consumption Prediction ⛽📊</div>', unsafe_allow_html=True)

    with st.container():

        vehicle = ['Two-seater','Minicompact','Compact','Subcompact','Mid-size',
                   'Full-size','SUV: Small','SUV: Standard','Minivan',
                   'Station wagon: Small','Station wagon: Mid-size',
                   'Pickup truck: Small','Special purpose vehicle',
                   'Pickup truck: Standard']

        transmission = ['AV','AM','M','AS','A']
        fuel = ["D","P","G","C"]

        with st.form("predict_form"):
            Vehicle_class = st.selectbox("Vehicle Class", vehicle)
            Engine_size = st.selectbox("Engine Size (1–7)", [1,2,3,4,5,6,7])
            Cylinders = st.number_input("Cylinders (1–16)",1,16,4)
            Transmission = st.selectbox("Transmission", transmission)
            Co2_Rating = st.number_input("CO₂ Rating (1–10)",1,10,5)
            Fuel_type = st.selectbox("Fuel Type", fuel)

            submit = st.form_submit_button("Predict 🔍")

        if submit:
            pred = input_converter([
                Vehicle_class, Engine_size, Cylinders,
                Transmission, Co2_Rating, Fuel_type
            ])

            st.markdown(f"""    
            <div class="result-card">
                <h3>✅ Prediction Result</h3>
                <h2>{pred} L/100km</h2>
                <p>Lower value means better fuel efficiency</p>
            </div>
            """, unsafe_allow_html=True)

            # =========================
            # VISUALIZATION
            # =========================
            df = {
                "Feature": ["Engine Size","Cylinders","CO₂ Rating","Predicted Fuel"],
                "Value": [Engine_size,Cylinders,Co2_Rating,pred]
            }

            fig = px.bar(
                x=df["Feature"],
                y=df["Value"],
                color=df["Feature"],
                title="📊 Prediction Analysis",
                animation_frame=None
            )
            st.plotly_chart(fig, use_container_width=True)

            # =========================
            # ADMIN ONLY ANALYTICS
            # =========================
            if st.session_state.role == "admin":
                radar = px.line_polar(
                    r=[Engine_size,Cylinders,Co2_Rating],
                    theta=["Engine Size","Cylinders","CO₂ Rating"],
                    line_close=True,
                    title="👑 Admin Feature Impact Radar"
                )
                st.plotly_chart(radar, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main()
