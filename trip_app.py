import streamlit as st
import datetime
import urllib.parse

# Page Setup
st.set_page_config(page_title="Rangers Matchday Tracker", page_icon="🔵", layout="centered")

# Royal Blue Custom Styling
st.markdown("""
    <style>
    .main-header {
        background-color: #003399;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border-bottom: 4px solid #CC0000;
        margin-bottom: 20px;
    }
    </style>
    <div class="main-header">
        <h1 style="margin:0; color:white;">🔵 Rangers Trip Tracker 🔴</h1>
        <p style="margin:5px 0 0 0; color:#e0e0e0;">Ibrox Matchday & Travel Splitter</p>
    </div>
""", unsafe_allow_html=True)

# 1. ONCE-A-DAY PRICE CHECKER (Runs max once every 24 hours / 86400 seconds)
@st.cache_data(ttl=86400)
def get_daily_baseline_rates(date_str):
    last_checked = datetime.datetime.now().strftime("%d %b %Y at %H:%M")
    default_flight = 65.0
    default_hotel = 95.0
    return default_flight, default_hotel, last_checked

# 2. MATCH & DATE DETAILS
st.subheader("📅 Match Details")
col1, col2 = st.columns(2)
with col1:
    fixture = st.text_input("Fixture / Opponent", value="Rangers vs ")
    travel_date = st.date_input("Match Date", datetime.date.today())
with col2:
    num_travellers = st.number_input("Total Lads Travelling", min_value=1, max_value=10, value=2, step=1)
    match_ticket = st.number_input("Match Ticket (£ per person)", min_value=0.0, value=48.0, step=1.0)

est_flight, est_hotel, last_sync = get_daily_baseline_rates(str(travel_date))
st.caption(f"🔄 *Daily baseline rates synced: {last_sync} (Updates once every 24h)*")

st.divider()

# 3. ACCOMMODATION (With 0-Night Day Trip Option)
st.subheader("🏨 Accommodation")
nights = st.slider("Nights in Glasgow", min_value=0, max_value=5, value=0)

if nights == 0:
    st.info("⚡ **Day Trip Mode:** In and out on matchday — £0 accommodation cost.")
    hotel_total = 0.0
    hotel_per_person = 0.0
else:
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        room_rate = st.number_input("Hotel Price per Night (£)", min_value=0.0, value=est_hotel, step=5.0)
    with h_col2:
        rooms_needed = st.number_input("Number of Rooms", min_value=1, max_
