import os
import csv
import urllib.parse
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Rangers Travel Hub", page_icon="⚽", layout="wide")

TRIPS_FILE = "my_rangers_trips.csv"

# --- PREMIUM IBROX CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Oswald:wght@500;700&display=swap');

    .stApp {
        background-color: #030712;
        background-image: radial-gradient(circle at 50% -20%, #0f2b6b 0%, #030712 70%);
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
    }
    .hero-banner {
        background: linear-gradient(135deg, #0033A0 0%, #081a45 50%, #C8102E 100%);
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        margin-bottom: 30px;
    }
    .hero-title {
        font-family: 'Oswald', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
        color: #ffffff;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #bfdbfe;
        margin-top: 5px;
        font-weight: 500;
    }
    .scoreboard {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border-top: 4px solid #0033A0;
        border-bottom: 4px solid #C8102E;
        border-left: 1px solid rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .match-teams {
        font-family: 'Oswald', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 15px 0;
        line-height: 1.1;
    }
    .match-details {
        font-size: 1.1rem;
        color: #94a3b8;
    }
    .badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 5px;
    }
    .badge-comp { background: #C8102E; color: white; }
    .badge-ha { background: #0033A0; color: white; }
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .glass-panel:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(56, 189, 248, 0.4);
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .panel-header {
        font-family: 'Oswald', sans-serif;
        font-size: 1.5rem;
        color: #38bdf8;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
    }
    .filter-tag {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        color: #7dd3fc;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 6px;
    }
    .alert-pill {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- CSV INIT ---
def init_trips_csv():
    if not os.path.exists(TRIPS_FILE):
        with open(TRIPS_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Match_Date", "Fixture", "Airport", "Check_In", "Check_Out", "Out_Time", "Ret_Time", "Hotel_Name", "Total_Cost_GBP", "Status"])

init_trips_csv()

# --- FIXTURES DATABASE ---
UPCOMING_FIXTURES = [
    {"opponent": "St. Johnstone", "ha": "HOME", "date": "2026-10-24", "time": "15:00", "venue": "Ibrox Stadium, Glasgow", "comp": "Scottish Premiership", "tier": "Standard"},
    {"opponent": "Heart of Midlothian", "ha": "AWAY", "date": "2026-10-28", "time": "20:00", "venue": "Tynecastle Park, Edinburgh", "comp": "Scottish Premiership", "tier": "High Demand"},
    {"opponent": "Aberdeen", "ha": "NEUTRAL", "date": "2026-10-31", "time": "17:30", "venue": "Hampden Park, Glasgow", "comp": "League Cup Semi-Final", "tier": "Peak Cup Tie"},
    {"opponent": "St. Mirren", "ha": "AWAY", "date": "2026-11-07", "time": "20:00", "venue": "SMiSA Stadium, Paisley", "comp": "Scottish Premiership", "tier": "Standard"},
    {"opponent": "Motherwell", "ha": "AWAY", "date": "2026-11-21", "time": "20:00", "venue": "Fir Park, Motherwell", "comp": "Scottish Premiership", "tier": "Standard"},
    {"opponent": "Aberdeen", "ha": "HOME", "date": "2026-11-24", "time": "20:00", "venue": "Ibrox Stadium, Glasgow", "comp": "Scottish Premiership", "tier": "High Demand"},
    {"opponent": "Falkirk", "ha": "HOME", "date": "2026-11-28", "time": "15:00", "venue": "Ibrox Stadium, Glasgow", "comp": "Scottish Premiership", "tier": "Standard"},
    {"opponent": "Dundee United", "ha": "HOME", "date": "2026-12-02", "time": "19:45", "venue": "Ibrox Stadium, Glasgow", "comp": "Scottish Premiership", "tier": "Standard"},
    {"opponent": "Hibernian", "ha": "AWAY", "date": "2026-12-07", "time": "20:00", "venue": "Easter Road, Edinburgh", "comp": "Scottish Premiership", "tier": "High Demand"},
    {"opponent": "Celtic", "ha": "HOME", "date": "2027-01-03", "time": "12:00", "venue": "Ibrox Stadium, Glasgow", "comp": "New Year Derby", "tier": "Peak Derby"}
]

TIME_FILTER_META = {
    "Any Time": {"query_word": "", "short": "Any Time", "ics_hr": "090000", "price_adj": 0.0},
    "Morning (Before 12 PM)": {"query_word": "morning", "short": "Morning (<12PM)", "ics_hr": "083000", "price_adj": -5.0},
    "Afternoon (12 PM - 5 PM)": {"query_word": "afternoon", "short": "Afternoon (12-5PM)", "ics_hr": "133000", "price_adj": 5.0},
    "Evening (After 5 PM)": {"query_word": "evening", "short": "Evening (>5PM)", "ics_hr": "183000", "price_adj": 15.0},
}

# --- UI START ---
st.markdown("""
<div class="hero-banner">
    <p class="hero-title">⚽ RANGERS TRAVEL HUB</p>
    <p class="hero-sub">Live Flights • Central Hotels • Smart Budget Projections</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATOR ---
with st.sidebar:
    st.markdown("### ⚙️ Trip Configurator")
    st.caption("Plan your journey from Belfast:")
    
    fix_labels = [f"{g['date']} • {g['opponent']} ({g['ha']})" for g in UPCOMING_FIXTURES]
    selected_label = st.selectbox("🎯 Select Match", fix_labels, index=2)
    match = UPCOMING_FIXTURES[fix_labels.index(selected_label)]
    
    st.divider()
    
    airport_choice = st.radio("🛫 Departure Airport", ["Belfast City (BHD)", "Belfast Intl (BFS)"])
    origin_code = "BHD" if "BHD" in airport_choice else "BFS"
    
    arrival_offset = st.selectbox("📅 Outbound Flight", ["Day Before Match", "Morning of Matchday", "2 Days Before Match"], index=0)
    nights = st.slider("🏨 Nights in Glasgow", min_value=1, max_value=5, value=2)
    
    st.divider()
    st.markdown("#### ⏰ Flight Time Filters")
    outbound_time = st.selectbox("Outbound Time Window", list(TIME_FILTER_META.keys()), index=0)
    return_time = st.selectbox("Return Time Window", list(TIME_FILTER_META.keys()), index=0)
    
    out_meta = TIME_FILTER_META[outbound_time]
    ret_meta = TIME_FILTER_META[return_time]
    
    # Calculate dynamic baseline flight estimate based on airport + chosen time windows
    base_air_fare = 45.0 if origin_code == "BHD" else 35.0
    dynamic_flight_default = max(20.0, base_air_fare + out_meta["price_adj"] + ret_meta["price_adj"])
    default_hotel = 125.0 if "Peak" in match["tier"] else 85.0

    st.divider()
    st.markdown("#### 💷 Budget Overrides")
    est_flight = st.number_input("Est. Return Flight (£)", value=float(dynamic_flight_default), step=5.0)
    est_hotel_night = st.number_input("Est. Hotel / Night (£)", value=float(default_hotel), step=5.0)
    est_match_ticket = st.number_input("Match Ticket (£)", value=45.0, step=5.0)

# --- DATES & MATH ---
match_dt = datetime.strptime(match["date"], "%Y-%m-%d")
days_until = (match_dt.date() - datetime.now().date()).days

dep_dt = match_dt - timedelta(days={"Day Before Match": 1, "2 Days Before Match": 2, "Morning of Matchday": 0}[arrival_offset])
ret_dt = dep_dt + timedelta(days=nights)

total_trip_cost = est_flight + (est_hotel_night * nights) + est_match_ticket

if days_until < 14:
    alert_style = "background: rgba(220,38,38,0.2); color: #fca5a5; border: 1px solid #ef4444;"
    alert_text = "🔴 LATE BOOKING ZONE: Expect High Flight & Hotel Prices"
elif 21 <= days_until <= 50:
    alert_style = "background: rgba(34,197,94,0.2); color: #86efac; border: 1px solid #22c55e;"
    alert_text = "🟢 OPTIMAL BOOKING WINDOW: Prime time for £30-£40 Flights"
else:
    alert_style = "background: rgba(59,130,246,0.2); color: #93c5fd; border: 1px solid #3b82f6;"
    alert_text = "🔵 EARLY PLANNING: Lock in Free-Cancellation Hotels Now"

# --- CENTER SCOREBOARD ---
st.markdown(f"""
<div class="scoreboard">
    <div>
        <span class="badge badge-comp">{match['comp']}</span>
        <span class="badge badge-ha">{match['ha']} FIXTURE</span>
    </div>
    <p class="match-teams">RANGERS <span style="color:#64748b; font-size:2rem;">vs</span> {match['opponent'].upper()}</p>
    <p class="match-details">
        🏟️ <b>{match['venue']}</b> &nbsp;|&nbsp; 🗓️ <b>{match_dt.strftime('%A, %d %B %Y')}</b> &nbsp;|&nbsp; ⏰ <b>{match['time']}</b>
    </p>
    <div class="alert-pill" style="{alert_style}">
        ⏳ <b>{max(0, days_until)} Days Away</b> — {alert_text}
    </div>
</div>
""", unsafe_allow_html=True)

# --- METRICS ROW (NOW UPDATES WITH SELECTED FLIGHT TIMES) ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("✈️ Fly Out", f"{dep_dt.strftime('%a %d %b')}", f"{origin_code} • {out_meta['short']}")
c2.metric("🛬 Return", f"{ret_dt.strftime('%a %d %b')}", f"GLA • {ret_meta['short']}")
c3.metric("🎫 Match Ticket", f"£{est_match_ticket:,.0f}", "Est. Face Value")
c4.metric("💷 Total Trip Cost", f"£{total_trip_cost:,.2f}", f"Includes £{est_flight:.0f} Flight Est.")

st.write("")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Live Booking Hub", "🏨 Recommended Hotels", "📒 Saved Trips"])

# --- TAB 1: LIVE HUB ---
with tab1:
    c_hub1, c_hub2 = st.columns(2)
    ds, rs = dep_dt.strftime("%Y-%m-%d"), ret_dt.strftime("%Y-%m-%d")
    
    # Build dynamic natural-language query for Google Flights with time filters included
    out_q = f" {out_meta['query_word']}" if out_meta["query_word"] else ""
    ret_q = f" {ret_meta['query_word']}" if ret_meta["query_word"] else ""
    raw_flight_query = f"flights from {origin_code} to GLA on {ds}{out_q} returning {rs}{ret_q}"
    encoded_flight_query = urllib.parse.quote(raw_flight_query)
    g_flights_url = f"https://www.google.com/travel/flights?q={encoded_flight_query}&curr=GBP"
    
    # Also build one-way specific leg links if user wants to inspect outbound/return separately
    out_only_q = urllib.parse.quote(f"flights from {origin_code} to GLA on {ds}{out_q}")
    ret_only_q = urllib.parse.quote(f"flights from GLA to {origin_code} on {rs}{ret_q}")

    with c_hub1:
        st.markdown(f"""
        <div class="glass-panel">
            <p class="panel-header">✈️ FLIGHT SCANNERS ({origin_code} ➔ GLA)</p>
            <p style="color:#94a3b8; font-size:0.95rem;">Active time filters applied to your search links:</p>
            <div>
                <span class="filter-tag">🛫 Out: {dep_dt.strftime('%d %b')} ({out_meta['short']})</span>
                <span class="filter-tag">🛬 Back: {ret_dt.strftime('%d %b')} ({ret_meta['short']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button(
            f"🔍 Search Return Flights ({out_meta['short']} / {ret_meta['short']})",
            g_flights_url,
            type="primary",
            use_container_width=True
        )
        col_leg1, col_leg2 = st.columns(2)
        col_leg1.link_button(f"🛫 Outbound Only ({out_meta['short']})", f"https://www.google.com/travel/flights?q={out_only_q}&curr=GBP", use_container_width=True)
        col_leg2.link_button(f"🛬 Return Only ({ret_meta['short']})", f"https://www.google.com/travel/flights?q={ret_only_q}&curr=GBP", use_container_width=True)
        st.link_button(f"⚡ Search Skyscanner ({origin_code} ➔ GLA)", f"https://www.skyscanner.net/transport/flights/{origin_code.lower()}/gla/{dep_dt.strftime('%y%m%d')}/{ret_dt.strftime('%y%m%d')}/", use_container_width=True)

    with c_hub2:
        st.markdown(f"""
        <div class="glass-panel">
            <p class="panel-header">🏨 HOTEL SCANNERS</p>
            <p style="color:#94a3b8; font-size:0.95rem;"><b>{nights} Nights</b> in Central Glasgow ({dep_dt.strftime('%d %b')} to {ret_dt.strftime('%d %b')}).</p>
            <div>
                <span class="filter-tag">📍 Glasgow City Centre</span>
                <span class="filter-tag">🛏️ {nights} Night Stay</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🏨 Search Google Hotels (Central)", f"https://www.google.com/travel/search?q=hotels%20in%20Glasgow%20city%20centre%20check-in%20{ds}%20check-out%20{rs}&curr=GBP", type="primary", use_container_width=True)
        st.link_button("🛏️ Search Booking.com", f"https://www.booking.com/searchresults.en-gb.html?ss=Glasgow+City+Centre&checkin={ds}&checkout={rs}", use_container_width=True)

    st.divider()
    ics = f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Rangers Hub//EN\nBEGIN:VEVENT\nSUMMARY:Rangers vs {match['opponent']} ({out_meta['short']} Flight)\nDESCRIPTION:Outbound: {outbound_time} | Return: {return_time} | Est Total: £{total_trip_cost:.2f}\nDTSTART:{dep_dt.strftime('%Y%m%d')}T{out_meta['ics_hr']}Z\nDTEND:{ret_dt.strftime('%Y%m%d')}T{ret_meta['ics_hr']}Z\nLOCATION:{match['venue']}\nEND:VEVENT\nEND:VCALENDAR"
    st.download_button("📥 Sync to Apple / Outlook Calendar (.ics)", data=ics, file_name=f"Rangers_{match['date']}.ics", mime="text/calendar", type="primary")

# --- TAB 2: HOTELS ---
with tab2:
    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown("""<div class="glass-panel"><p class="panel-header">Revolver Glasgow</p><p style="color:#38bdf8;">📍 Merchant City</p><p>Boutique, vibrant, highly rated, and frequently beats the big chain prices.</p></div>""", unsafe_allow_html=True)
    with h2:
        st.markdown("""<div class="glass-panel"><p class="panel-header">The Social Hub</p><p style="color:#38bdf8;">📍 Candleriggs</p><p>4.4★ rated. Ultra-modern base, excellent bar, and just minutes from the subway.</p></div>""", unsafe_allow_html=True)
    with h3:
        st.markdown("""<div class="glass-panel"><p class="panel-header">YOTEL / Novotel</p><p style="color:#38bdf8;">📍 Glasgow Central</p><p>Incredibly convenient. Drops you right beside the airport bus and mainline trains.</p></div>""", unsafe_allow_html=True)

# --- TAB 3: TRIPS LOG ---
with tab3:
    with st.form("save_form"):
        f1, f2, f3 = st.columns(3)
        hotel = f1.text_input("Hotel Name", "Revolver")
        cost = f2.number_input("Actual Total Cost (£)", value=float(total_trip_cost))
        stat = f3.selectbox("Status", ["Planning", "Flights Booked", "Fully Booked"])
        if st.form_submit_button("📌 Save to Logbook"):
            with open(TRIPS_FILE, mode="a", newline="") as f:
                csv.writer(f).writerow([match["date"], match['opponent'], origin_code, ds, rs, out_meta['short'], ret_meta['short'], hotel, f"{cost:.2f}", stat])
            st.rerun()

    df = pd.read_csv(TRIPS_FILE)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

