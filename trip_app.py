import streamlit as st
import datetime as dt
import urllib.parse as up
import urllib.request as ur
import json

st.set_page_config(
    page_title="Rangers Tracker",
    page_icon="🔵",
    layout="centered"
)

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
        <h1 style="margin:0;color:white;">
            🔵 Rangers Trip Tracker 🔴
        </h1>
        <p style="margin:5px 0 0 0;color:#eee;">
            Ibrox Matchday & Travel Planner
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 0. UPCOMING 2026/27 RANGERS FIXTURES
FIXTURES = {
    "Rangers vs St Johnstone (24 Oct)": (
        dt.date(2026, 10, 24)
    ),
    "Hearts vs Rangers (28 Oct)": (
        dt.date(2026, 10, 28)
    ),
    "Rangers vs Aberdeen - Hampden (31 Oct)": (
        dt.date(2026, 10, 31)
    ),
    "St Mirren vs Rangers (7 Nov)": (
        dt.date(2026, 11, 7)
    ),
    "Motherwell vs Rangers (21 Nov)": (
        dt.date(2026, 11, 21)
    ),
    "Rangers vs Aberdeen (24 Nov)": (
        dt.date(2026, 11, 24)
    ),
    "Rangers vs Falkirk (28 Nov)": (
        dt.date(2026, 11, 28)
    ),
    "Rangers vs Dundee Utd (2 Dec)": (
        dt.date(2026, 12, 2)
    ),
    "Hibernian vs Rangers (7 Dec)": (
        dt.date(2026, 12, 7)
    ),
    "St Johnstone vs Rangers (13 Dec)": (
        dt.date(2026, 12, 13)
    ),
    "Rangers vs Hearts (20 Dec)": (
        dt.date(2026, 12, 20)
    ),
    "Kilmarnock vs Rangers (26 Dec)": (
        dt.date(2026, 12, 26)
    ),
    "Rangers vs Dundee (30 Dec)": (
        dt.date(2026, 12, 30)
    ),
    "Rangers vs Celtic (3 Jan 2027)": (
        dt.date(2027, 1, 3)
    ),
    "Dundee Utd vs Rangers (9 Jan)": (
        dt.date(2027, 1, 9)
    ),
    "Rangers vs St Johnstone (23 Jan)": (
        dt.date(2027, 1, 23)
    ),
    "Aberdeen vs Rangers (30 Jan)": (
        dt.date(2027, 1, 30)
    ),
    "Rangers vs Kilmarnock (3 Feb)": (
        dt.date(2027, 2, 3)
    ),
    "Falkirk vs Rangers (13 Feb)": (
        dt.date(2027, 2, 13)
    ),
    "Rangers vs St Mirren (20 Feb)": (
        dt.date(2027, 2, 20)
    ),
    "Celtic vs Rangers (27 Feb)": (
        dt.date(2027, 2, 27)
    ),
    "Rangers vs Motherwell (13 Mar)": (
        dt.date(2027, 3, 13)
    ),
    "Hearts vs Rangers (20 Mar)": (
        dt.date(2027, 3, 20)
    ),
    "Rangers vs Hibernian (3 Apr)": (
        dt.date(2027, 4, 3)
    ),
    "Custom / Other Match": (
        dt.date.today()
    )
}


def fetch_json(params):
    q = up.urlencode(params)
    url = f"https://serpapi.com/search.json?{q}"
    req = ur.urlopen(url, timeout=10)
    raw = req.read().decode("utf-8")
    return json.loads(raw)


def update_flights(f_opts, d1, d2, key):
    f_type = "1" if d1 != d2 else "2"
    p = {
        "engine": "google_flights",
        "departure_id": "BFS,BHD",
        "arrival_id": "GLA",
        "outbound_date": d1,
        "type": f_type,
        "currency": "GBP",
        "hl": "en",
        "api_key": key
    }
    if f_type == "1":
        p["return_date"] = d2
    data = fetch_json(p)
    best = data.get("best_flights", [])
    if not best:
        return False
    val = float(best[0].get("price", 58.0))
    if f_type == "2":
        val = val * 2.0
    k = "easyJet (Belfast Int BFS <-> Glasgow)"
    f_opts[k] = val
    return True


def update_hotels(h_opts, d1, d2, key):
    if d1 == d2:
        return False
    p = {
        "engine": "google_hotels",
        "q": "Glasgow hotels",
        "check_in_date": d1,
        "check_out_date": d2,
        "currency": "GBP",
        "hl": "en",
        "api_key": key
    }
    data = fetch_json(p)
    props = data.get("properties", [])
    hit = False
    for item in props:
        nm = item.get("name", "").lower()
        rt = item.get("rate_per_night", {})
        pr = rt.get("extracted_lowest")
        if not pr:
            continue
        for hk in h_opts.keys():
            w1 = hk.split()[0].lower()
            if w1 in nm and w1 != "custom":
                h_opts[hk] = float(pr)
                hit = True
    return hit


# 1. LIVE DAILY PRICE FETCHER (24h Cache)
@st.cache_data(ttl=86400)
def get_daily_prices(d1, d2):
    now = dt.datetime.now()
    sync = now.strftime("%d %b %Y at %H:%M")
    live = False

    f_opts = {
        "easyJet (Belfast Int BFS <-> Glasgow)": 58.0,
        "easyJet (Belfast City BHD <-> Glasgow)": 68.0,
        "Aer Lingus (Belfast City <-> Glasgow)": 82.0,
        "Out via GLA / Back via Dublin + Coach": 75.0,
        "Stena Line Ferry + Coach (Return)": 74.0,
        "Stena Line Day Trip Coach": 35.0
    }

    h_opts = {
        "Village Hotel Glasgow (Near Ibrox)": 115.0,
        "Premier Inn Glasgow City Centre": 88.0,
        "Travelodge Glasgow Central": 75.0,
        "ibis Styles Glasgow Centre": 98.0,
        "citizenM Glasgow": 110.0,
        "Leonardo Royal Hotel Glasgow": 105.0,
        "Custom / Other Hotel": 90.0
    }

    key = st.secrets.get("SERPAPI_KEY", None)
    if key:
        try:
            if update_flights(f_opts, d1, d2, key):
                live = True
        except Exception:
            pass
        try:
            if update_hotels(h_opts, d1, d2, key):
                live = True
        except Exception:
            pass

    return f_opts, h_opts, sync, live


# 2. MATCH & DATE DETAILS
st.subheader("📅 Match Details")

fix_list = list(FIXTURES.keys())
sel_fix = st.selectbox(
    "Select Upcoming Rangers Fixture",
    fix_list,
    index=2
)
def_date = FIXTURES[sel_fix]

col1, col2 = st.columns(2)
with col1:
    if sel_fix == "Custom / Other Match":
        fixture = st.text_input(
            "Custom Fixture Name",
            value="Rangers vs "
        )
    else:
        fixture = sel_fix
        st.text_input(
            "Selected Match",
            value=fixture,
            disabled=True
        )
    travel_date = st.date_input(
        "Match Date",
        value=def_date
    )

with col2:
    num_people = st.number_input(
        "People Travelling",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )
    match_ticket = st.number_input(
        "Match Ticket (£ per person)",
        min_value=0.0,
        value=48.0,
        step=1.0
    )

st.divider()

# 3. ACCOMMODATION
st.subheader("🏨 Accommodation")
nights = st.slider(
    "Nights in Glasgow (0 for Day Trip)",
    min_value=0,
    max_value=5,
    value=1
)

ret_date = travel_date + dt.timedelta(days=nights)
d1_str = travel_date.strftime("%Y-%m-%d")
d2_str = ret_date.strftime("%Y-%m-%d")

f_dict, h_dict, sync_t, is_live = get_daily_prices(
    d1_str,
    d2_str
)

if is_live:
    st.caption(
        f"🟢 *Live web prices synced: {sync_t} "
        f"(Cached 24h)*"
    )
else:
    st.caption(
        f"🟡 *Baseline prices shown ({sync_t}).*"
    )

if nights == 0:
    st.info(
        "⚡ **Day Trip Mode (0 Nights):** "
        "Same-day return — £0 hotel cost."
    )
    sel_hotel = "None (Day Trip)"
    hotel_total = 0.0
    hotel_pp = 0.0
else:
    sel_hotel = st.selectbox(
        "Select Hotel Option",
        list(h_dict.keys())
    )
    h_price = float(h_dict[sel_hotel])

    hc1, hc2 = st.columns(2)
    with hc1:
        room_rate = st.number_input(
            "Nightly Rate (£ - Auto or Edit)",
            min_value=0.0,
            value=h_price,
            step=5.0
        )
    with hc2:
        rooms = st.number_input(
            "Number of Rooms",
            min_value=1,
            max_value=5,
            value=1,
            step=1
        )

    hotel_total = room_rate * nights * rooms
    hotel_pp = hotel_total / num_people
    st.caption(
        f"Total Hotel: **£{hotel_total:.2f}** "
        f"(£{hotel_pp:.2f} per person)"
    )

    hq = up.quote(sel_hotel)
    b_url = (
        f"https://www.booking.com/searchresults.html"
        f"?ss={hq}&checkin={d1_str}"
        f"&checkout={d2_str}"
        f"&group_adults={num_people}"
        f"&no_rooms={rooms}"
    )
    g_url = (
        f"https://www.google.com/travel/hotels/"
        f"Glasgow?q={hq}"
    )

    hb1, hb2 = st.columns(2)
    with hb1:
        st.link_button(
            "🏨 Booking.com Prices",
            b_url,
            use_container_width=True
        )
    with hb2:
        st.link_button(
            "🔍 Google Hotels",
            g_url,
            use_container_width=True
        )

st.divider()

# 4. FLIGHTS & TRAVEL OPTIONS
st.subheader("✈️ Flights, Ferry & Transfers")
sel_trans = st.selectbox(
    "Select Flight / Travel Option",
    list(f_dict.keys())
)
f_price = float(f_dict[sel_trans])

tc1, tc2 = st.columns(2)
with tc1:
    main_trans = st.number_input(
        "Return Fare (£ - Auto or Edit)",
        min_value=0.0,
        value=f_price,
        step=5.0
    )
with tc2:
    is_dub = "Dublin" in sel_trans
    def_ex = 25.0 if is_dub else 12.0
    extra_trans = st.number_input(
        "Transfers / Subway (£ per person)",
        min_value=0.0,
        value=def_ex,
        step=2.0
    )

s_out = travel_date.strftime("%y%m%d")
s_ret = ret_date.strftime("%y%m%d")
sky_url = (
    f"https://www.skyscanner.net/transport/"
    f"flights/belf/glas/{s_out}/{s_ret}/"
    f"?adults={num_people}"
)
ej_url = "https://www.easyjet.com/en"
st_url = (
    "https://www.stenaline.co.uk/routes/"
    "belfast-cairnryan"
)

fb1, fb2, fb3 = st.columns(3)
with fb1:
    st.link_button(
        "✈️ Skyscanner",
        sky_url,
        use_container_width=True
    )
with fb2:
    st.link_button(
        "🟠 easyJet",
        ej_url,
        use_container_width=True
    )
with fb3:
    st.link_button(
        "⛴️ Stena Line",
        st_url,
        use_container_width=True
    )

st.divider()

# 5. FOOD & DRINK
st.subheader("🍽️ Food & Drink")
daily_spend = st.number_input(
    "Food & Drink Budget (£ per person)",
    min_value=0.0,
    value=60.0,
    step=10.0
)

st.divider()

# 6. FINAL BREAKDOWN & WHATSAPP SHARE
travel_pp = main_trans + extra_trans
total_pp = (
    match_ticket
    + hotel_pp
    + travel_pp
    + daily_spend
)
group_total = total_pp * num_people

st.subheader("💷 Final Cost Breakdown")
m1, m2, m3 = st.columns(3)
m1.metric("Cost Per Person", f"£{total_pp:.2f}")
m2.metric("Hotel Per Person", f"£{hotel_pp:.2f}")
m3.metric(
    f"Total ({num_people} People)",
    f"£{group_total:.2f}"
)

with st.expander("See Itemized Breakdown"):
    st.write(
        f"🎟️ **Match Ticket:** £{match_ticket:.2f}"
    )
    st.write(
        f"✈️ **Travel ({sel_trans}):** "
        f"£{main_trans:.2f}"
    )
    st.write(
        f"🚌 **Transfers:** £{extra_trans:.2f}"
    )
    st.write(
        f"🏨 **Hotel ({sel_hotel}):** "
        f"£{hotel_pp:.2f}"
    )
    st.write(
        f"🍽️ **Food & Drink:** £{daily_spend:.2f}"
    )

if nights == 0:
    stay_s = "Day Trip (0 Nights)"
else:
    stay_s = f"{nights} Night(s) - {sel_hotel}"

wa_lines = [
    "🔵 *Rangers Trip Breakdown* 🔴",
    f"⚽ *Match:* {fixture}",
    f"🏨 *Stay:* {stay_s}",
    f"✈️ *Travel:* {sel_trans}",
    "",
    f"💷 *Total Per Person: £{total_pp:.2f}*",
    f"• Ticket: £{match_ticket:.2f}",
    f"• Travel & Transfers: £{travel_pp:.2f}",
    f"• Hotel Share: £{hotel_pp:.2f}",
    f"• Food & Drink: £{daily_spend:.2f}"
]

wa_msg = "\n".join(wa_lines)
enc_wa = up.quote(wa_msg)
wa_link = f"https://wa.me/?text={enc_wa}"

st.link_button(
    "📲 Send Breakdown to WhatsApp",
    wa_link,
    use_container_width=True
)
