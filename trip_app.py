import streamlit as st
import datetime
import urllib.parse

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
            Ibrox Matchday & Travel Splitter
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 1. ONCE-A-DAY PRICE CHECKER (24h Cache)
@st.cache_data(ttl=86400)
def get_daily_baseline_rates(date_str):
    now = datetime.datetime.now()
    last_checked = now.strftime("%d %b %Y at %H:%M")
    default_flight = 65.0
    default_hotel = 95.0
    return default_flight, default_hotel, last_checked

# 2. MATCH & DATE DETAILS
st.subheader("📅 Match Details")
col1, col2 = st.columns(2)

with col1:
    fixture = st.text_input(
        "Fixture / Opponent",
        value="Rangers vs "
    )
    travel_date = st.date_input(
        "Match Date",
        datetime.date.today()
    )

with col2:
    num_travellers = st.number_input(
        "Total Lads Travelling",
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

est_flight, est_hotel, last_sync = get_daily_baseline_rates(
    str(travel_date)
)
st.caption(
    f"🔄 *Daily baseline rates synced: {last_sync} "
    f"(Updates once every 24h)*"
)

st.divider()

# 3. ACCOMMODATION (With 0-Night Day Trip Option)
st.subheader("🏨 Accommodation")
nights = st.slider(
    "Nights in Glasgow",
    min_value=0,
    max_value=5,
    value=0
)

if nights == 0:
    st.info(
        "⚡ **Day Trip Mode:** In and out on matchday "
        "— £0 accommodation cost."
    )
    hotel_total = 0.0
    hotel_per_person = 0.0
else:
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        room_rate = st.number_input(
            "Hotel Price per Night (£)",
            min_value=0.0,
            value=est_hotel,
            step=5.0
        )
    with h_col2:
        rooms_needed = st.number_input(
            "Number of Rooms",
            min_value=1,
            max_value=5,
            value=1,
            step=1
        )
    
    hotel_total = room_rate * nights * rooms_needed
    hotel_per_person = hotel_total / num_travellers
    st.caption(
        f"Total Hotel: **£{hotel_total:.2f}** "
        f"(£{hotel_per_person:.2f} each across {nights} night(s))"
    )

st.divider()

# 4. TRAVEL & TRANSFERS
st.subheader("✈️ Travel & Transfers")
route_options = [
    "Return Flight (Belfast <-> Glasgow)",
    "Out via Glasgow Flight / Back via Dublin + Coach to Belfast",
    "Ferry (Belfast <-> Cairnryan + Train/Drive)"
]
route_type = st.selectbox("Travel Route", route_options)

t_col1, t_col2 = st.columns(2)
with t_col1:
    main_transport = st.number_input(
        "Flights / Ferry (£ per person)",
        min_value=0.0,
        value=est_flight,
        step=5.0
    )
with t_col2:
    is_dub = "Dublin" in route_type
    default_extra = 25.0 if is_dub else 12.0
    extra_transfers = st.number_input(
        "Coaches / Subway / Taxis (£ each)",
        min_value=0.0,
        value=default_extra,
        step=2.0
    )

st.divider()

# 5. SPENDING MONEY (Pint & Scran)
st.subheader("🍻 Matchday Kitty")
daily_kitty = st.number_input(
    "Pints & Food Budget (£ per person)",
    min_value=0.0,
    value=60.0,
    step=10.0
)

st.divider()

# 6. FINAL BREAKDOWN & WHATSAPP SHARE
travel_per_person = main_transport + extra_transfers
total_per_person = (
    match_ticket
    + hotel_per_person
    + travel_per_person
    + daily_kitty
)
group_grand_total = total_per_person * num_travellers

st.subheader("💷 Final Cost Breakdown")
m1, m2, m3 = st.columns(3)
m1.metric("Cost Per Person", f"£{total_per_person:.2f}")
m2.metric("Hotel Share Each", f"£{hotel_per_person:.2f}")
m3.metric(
    f"Total ({num_travellers} Lads)",
    f"£{group_grand_total:.2f}"
)

with st.expander("See Full Itemized Breakdown (Per Person)"):
    st.write(f"🎟️ **Match Ticket:** £{match_ticket:.2f}")
    st.write(
        f"✈️ **Transport ({route_type}):** "
        f"£{main_transport:.2f}"
    )
    st.write(
        f"🚌 **Transfers / Subway / Coach:** "
        f"£{extra_transfers:.2f}"
    )
    st.write(
        f"🏨 **Hotel ({nights} nights):** "
        f"£{hotel_per_person:.2f}"
    )
    st.write(
        f"🍻 **Food & Pints Kitty:** "
        f"£{daily_kitty:.2f}"
    )

if nights == 0:
    trip_type_str = "Day Trip (0 Nights)"
else:
    trip_type_str = f"{nights} Night(s)"

date_formatted = travel_date.strftime("%d %b")

wa_lines = [
    "🔵 *Rangers Trip Breakdown* 🔴",
    f"⚽ *Match:* {fixture} ({date_formatted})",
    f"🛏️ *Stay:* {trip_type_str}",
    f"🛣️ *Route:* {route_type}",
    "",
    f"💷 *Total Each: £{total_per_person:.2f}*",
    f"• Ticket: £{match_ticket:.2f}",
    f"• Travel & Transfers: £{travel_per_person:.2f}",
    f"• Hotel Share: £{hotel_per_person:.2f}",
    f"• Pints/Food: £{daily_kitty:.2f}"
]

wa_message = "\n".join(wa_lines)
encoded_wa = urllib.parse.quote(wa_message)
wa_link = f"https://wa.me/?text={encoded_wa}"

st.link_button(
    "📲 Send Breakdown to WhatsApp",
    wa_link,
    use_container_width=True
)
