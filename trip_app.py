import streamlit as st
import datetime
import urllib.parse
import urllib.request
import json

# Page Setup
st.set_page_config(
    page_title="Rangers Matchday Tracker",
    page_icon="🔵",
    layout="centered"
)

# Royal Blue Custom Styling & Header
st.markdown(
    """
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
        <h1 style="margin:0; color:white;">
            🔵 Rangers Trip Tracker 🔴
        </h1>
        <p style="margin:5px 0 0 0; color:#e0e0e0;">
            Ibrox Matchday & Travel Planner
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 0. UPCOMING 2026/27 RANGERS FIXTURES DICTIONARY
FIXTURES_26_27 = {
    "Rangers vs St Johnstone (Ibrox - Sat 24 Oct 2026)": datetime.date(2026, 10, 24),
    "Hearts vs Rangers (Tynecastle - Wed 28 Oct 2026)": datetime.date(2026, 10, 28),
    "Rangers vs Aberdeen (Hampden Cup Semi - Sat 31 Oct 2026)": datetime.date(2026, 10, 31),
    "St Mirren vs Rangers (Paisley - Sat 7 Nov 2026)": datetime.date(2026, 11, 7),
    "Motherwell vs Rangers (Fir Park - Sat 21 Nov 2026)": datetime.date(2026, 11, 21),
    "Rangers vs Aberdeen (Ibrox - Tue 24 Nov 2026)": datetime.date(2026, 11, 24),
    "Rangers vs Falkirk (Ibrox - Sat 28 Nov 2026)": datetime.date(2026, 11, 28),
    "Rangers vs Dundee United (Ibrox - Wed 2 Dec 2026)": datetime.date(2026, 12, 2),
    "Hibernian vs Rangers (Easter Road - Mon 7 Dec 2026)": datetime.date(2026, 12, 7),
    "St Johnstone vs Rangers (Perth - Sun 13 Dec 2026)": datetime.date(2026, 12, 13),
    "Rangers vs Hearts (Ibrox - Sun 20 Dec 2026)": datetime.date(2026, 12, 20),
    "Kilmarnock vs Rangers (Rugby Park - Sat 26 Dec 2026)": datetime.date(2026, 12, 26),
    "Rangers vs Dundee (Ibrox - Wed 30 Dec 2026)": datetime.date(2026, 12, 30),
    "Rangers vs Celtic (Ibrox - Sun 3 Jan 2027)": datetime.date(2027, 1, 3),
    "Dundee United vs Rangers (Tannadice - Sat 9 Jan 2027)": datetime.date(2027, 1, 9),
    "Rangers vs St Johnstone (Ibrox - Sat 23 Jan 2027)": datetime.date(2027, 1, 23),
    "Aberdeen vs Rangers (Pittodrie - Sat 30 Jan 2027)": datetime.date(2027, 1, 30),
    "Rangers vs Kilmarnock (Ibrox - Wed 3 Feb 2027)": datetime.date(2027, 2, 3),
    "Falkirk vs Rangers (Falkirk - Sat 13 Feb 2027)": datetime.date(2027, 2, 13),
    "Rangers vs St Mirren (Ibrox - Sat 20 Feb 2027)": datetime.date(2027, 2, 20),
    "Celtic vs Rangers (Parkhead - Sat 27 Feb 2027)": datetime.date(2027, 2, 27),
    "Rangers vs Motherwell (Ibrox - Sat 13 Mar 2027)": datetime.date(2027, 3, 13),
    "Hearts vs Rangers (Tynecastle - Sat 20 Mar 2027)": datetime.date(2027, 3, 20),
    "Rangers vs Hibernian (Ibrox - Sat 3 Apr 2027)": datetime.date(2027, 4, 3),
    "Custom / Other Match": datetime.date.today()
}

# 1. LIVE DAILY PRICE FETCHER (Runs max once every 24 hours per date)
@st.cache_data(ttl=86400)
def get_daily_searched_prices(out_date_str, ret_date_str):
    now = datetime.datetime.now()
    last_checked = now.strftime("%d %b %Y at %H:%M")
    is_live = False

    flight_options = {
        "easyJet (Belfast Int BFS <-> Glasgow)": 58.0,
        "easyJet (Belfast City BHD <-> Glasgow)": 68.0,
        "Aer Lingus (Belfast City BHD <-> Glasgow)": 82.0,
        "Out via Glasgow / Back via Dublin + Coach": 75.0,
        "Stena Line Ferry + Coach (Belfast <-> Glasgow)": 74.0,
        "Stena Line Day Trip Coach (Belfast <-> Glasgow)": 35.0
    }
    
    hotel_options = {
        "Village Hotel Glasgow (Near Ibrox)": 115.0,
        "Premier Inn Glasgow City Centre": 88.0,
        "Travelodge Glasgow Central": 75.0,
        "ibis Styles Glasgow Centre": 98.0,
        "citizenM Glasgow": 110.0,
        "Leonardo Royal Hotel Glasgow": 105.0,
        "Custom / Other Hotel": 90.0
    }

    api_key = None
    try:
        api_key = st.secrets["SERPAPI_KEY"]
    except Exception:
        api_key = None

    if api_key:
        # A. Fetch Live Flight Prices (BFS/BHD -> GLA)
        try:
            f_Type = "1" if out_date_str != ret_date_str else "2"
            f_params = {
                "engine": "google_flights",
                "departure_id": "BFS,BHD",
                "arrival_id": "GLA",
                "outbound_date": out_date_str,
                "type": f_Type,
                "currency": "GBP",
                "hl": "en",
                "api_key": api_key
            }
            if f_Type == "1":
                f_params["return_date"] = ret_date_str

            f_query = urllib.parse.urlencode(f_params)
            f_url = f"https://serpapi.com/search.json?{f_query}"
            req = urllib.request.urlopen(f_url, timeout=10)
            f_data = json.loads(req.read().decode("utf-8"))
            
            best_flights = f_data.get("best_flights", [])
            if best_flights:
                cheapest = float(best_flights[0].get("price", 58.0))
                if f_Type == "2":
                    cheapest = cheapest * 2.0
                flight_options["easyJet (Belfast Int BFS <-> Glasgow)"] = cheapest
                is_live = True
        except Exception:
            pass

        # B. Fetch Live Hotel Prices in Glasgow
        if out_date_str != ret_date_str:
            try:
                h_params = urllib.parse.urlencode({
                    "engine": "google_hotels",
                    "q": "Glasgow hotels",
                    "check_in_date": out_date_str,
                    "check_out_date": ret_date_str,
                    "currency": "GBP",
                    "hl": "en",
                    "api_key": api_key
                })
                h_url = f"https://serpapi.com/search.json?{h_params}"
                req
