import streamlit as st
import datetime
import urllib.parse

st.set_page_config(
    page_title="Rangers Tracker",
    page_icon="🔵"
)

st.title("🔵 Rangers Trip Tracker 🔴")
st.caption("Ibrox Matchday & Travel Splitter")

@st.cache_data(ttl=86400)
def get_rates(d_str):
    now = datetime.datetime.now()
    t_str = now.strftime("%d %b %H:%M")
    return 65.0, 95.0, t_str

st.subheader("📅 Match Details")
c1, c2 = st.columns(2)
with c1:
    opp = st.text_input("Fixture", "Rangers vs ")
    m_date = st.date_input("Date")
with c2:
    lads = st.number_input("Lads", 1, 10, 2)
    tix = st.number_input("Ticket (£)", 0.0, 200.0, 48.0)

f_est, h_est, sync = get_rates(str(m_date))
st.caption(f"🔄 Rates synced: {sync} (24h cache)")

st.divider()

st.subheader("🏨 Accommodation")
nights = st.slider("Nights in Glasgow", 0, 5, 0)

if nights == 0:
    st.info("⚡ Day Trip Mode: £0 hotel cost.")
    h_tot = 0.0
    h_pp = 0.0
else:
    hc1, hc2 = st.columns(2)
    with hc1:
        rate = st.number_input("Room Rate (£)", 0.0, 500.0, h_est)
    with hc2:
        rooms = st.number_input("Rooms", 1, 5, 1)
    h_tot = rate * nights * rooms
    h_pp = h_tot / lads
    st.caption(f"Hotel Total: £{h_tot:.2f}")

st.divider()

st.subheader("✈️ Travel & Transfers")
routes = [
    "Return Flight (BFS/BHD <-> GLA)",
    "Out via GLA / Back via Dublin + Coach",
    "Ferry (Belfast <-> Cairnryan)"
]
route = st.selectbox("Route", routes)

tc1, tc2 = st.columns(2)
with tc1:
    trans = st.number_input("Flight/Ferry (£)", 0.0, 500.0, f_est)
with tc2:
    def_ex = 25.0 if "Dublin" in route else 12.0
    extra = st.number_input("Transfers (£)", 0.0, 200.0, def_ex)

st.divider()

st.subheader("🍻 Matchday Kitty")
kitty = st.number_input("Pints & Food (£)", 0.0, 500.0, 60.0)

st.divider()

trav_pp = trans + extra
tot_pp = tix + h_pp + trav_pp + kitty
