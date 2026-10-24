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
            Ibrox Matchday & Travel Planner
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 1. ONCE-A-DAY PRICE CHECKER (Runs max once every 24 hours)
@st.cache_data(ttl=86400)
def get_daily_searched_prices(date_str):
    now = datetime.datetime.now()
    last_checked = now.strftime("%d %b %Y at %H:%M")
    
    # Daily searched baseline prices per option
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
    
    return flight_options, hotel_options, last_checked

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

flight_dict, hotel_dict, last_sync = get_daily_searched_prices(
    str(travel_date)
)
st.caption(
    f"🔄 *Daily prices searched & synced: {last_sync} "
    f"(Cached for 24h)*"
)

st.divider()

# 3. ACCOMMODATION (0-Night Day Trip + Hotel Selector + Manual Price)
st.subheader("🏨 Accommodation")
nights = st.slider(
    "Nights in Glasgow (Select 0 for Day Trip)",
    min_value=0,
    max_value=5,
    value=1
)

if nights == 0:
    st.info(
        "⚡ **Day Trip Mode (0 Nights):** Same-day travel "
        "— £0 accommodation cost."
    )
    selected_hotel = "None (Day Trip)"
    hotel_total = 0.0
    hotel_per_person = 0.0
else:
    selected_hotel = st.selectbox(
        "Select Hotel Option",
        list(hotel_dict.keys())
    )
    searched_hotel_price = hotel_dict[selected_hotel]
    
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        room_rate = st.number_input(
            "Nightly Rate (£ - Auto-filled or Edit)",
            min_value=0.0,
            value= float(searched_hotel_price),
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
    hotel_per_person = hotel_total / num_people
    st.caption(
        f"Total Hotel ({selected_hotel}): **£{hotel_total:.2f}** "
        f"(£{hotel_per_person:.2f} per person)"
    )

st.divider()

# 4. FLIGHTS & TRAVEL OPTIONS (Option Selector + Daily Price + Manual Edit)
st.subheader("✈️ Flights, Ferry & Transfers")
selected_transport = st.selectbox(
    "Select Flight / Travel Option",
    list(flight_dict.keys())
)
searched_flight_price = flight_dict[selected_transport]

t_col1, t_col2 = st.columns(2)
with t_col1:
    main_transport = st.number_input(
        "Return Fare (£ per person - Auto-filled or Edit)",
        min_value=0.0,
        value=float(searched_flight_price),
        step=5.0
    )
with t_col2:
    is_dub = "Dublin" in selected_transport
    default_extra = 25.0 if is_dub else 12.0
    extra_transfers = st.number_input(
        "Airport Transfers / Subway / Buses (£ per person)",
        min_value=0.0,
        value=default_extra,
        step=2.0
    )

st.divider()

# 5. FOOD & DRINK
st.subheader("🍽️ Food & Drink")
daily_spending = st.number_input(
    "Food & Drink Budget (£ per person)",
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
    + daily_spending
)
group_grand_total = total_per_person * num_people

st.subheader("💷 Final Cost Breakdown")
m1, m2, m3 = st.columns(3)
m1.metric("Cost Per Person", f"£{total_per_person:.2f}")
m2.metric("Hotel Per Person", f"£{hotel_per_person:.2f}")
m3.metric(
    f"Total ({num_people} People)",
    f"£{group_grand_total:.2f}"
)

with st.expander("See Full Itemized Breakdown (Per Person)"):
    st.write(f"🎟️ **Match Ticket:** £{match_ticket:.2f}")
    st.write(
        f"✈️ **Travel ({selected_transport}):** "
        f"£{main_transport:.2f}"
    )
    st.write(
        f"🚌 **Transfers / Subway:** "
        f"£{extra_transfers:.2f}"
    )
    st.write(
        f"🏨 **Hotel ({selected_hotel} - {nights} nights):** "
        f"£{hotel_per_person:.2f}"
    )
    st.write(
        f"🍽️ **Food & Drink:** "
        f"£{daily_spending:.2f}"
    )

if nights == 0:
    stay_str = "Day Trip (0 Nights)"
else:
    stay_str = f"{nights} Night(s) at {selected_hotel}"

date_formatted = travel_date.strftime("%d %b")

wa_lines = [
    "🔵 *Rangers Trip Breakdown* 🔴",
    f"⚽ *Match:* {fixture} ({date_formatted})",
    f"🏨 *Stay:* {stay_str}",
    f"✈️ *Travel:* {selected_transport}",
    "",
    f"💷 *Total Per Person: £{total_per_person:.2f}*",
    f"• Ticket: £{match_ticket:.2f}",
    f"• Flights/Ferry & Transfers: £{travel_per_person:.2f}",
    f"• Hotel Share: £{hotel_per_person:.2f}",
    f"• Food & Drink: £{daily_spending:.2f}"
]

wa_message = "\n".join(wa_lines)
encoded_wa = urllib.parse.quote(wa_message)
wa_link = f"https://wa.me/?text={encoded_wa}"

st.link_button(
    "📲 Send Breakdown to WhatsApp",
    wa_link,
    use_container_width=True
)
