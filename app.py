
import streamlit as st
from database import init_db
from parking import ParkingManager, TOTAL_SLOTS

st.set_page_config(
    page_title="Smart Parking Management",
    page_icon="🚗",
    layout="wide"
)

init_db()
manager = ParkingManager()

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
[data-testid="stMetric"] {
    background: #17243b;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #293b59;
}
.slot {
    padding: 18px 5px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 12px;
    font-weight: bold;
}
.free {
    background: #123d32;
    border: 1px solid #16a36b;
    color: #65e6ad;
}
.busy {
    background: #482326;
    border: 1px solid #d94b55;
    color: #ff9a9f;
}
</style>
""", unsafe_allow_html=True)

st.title("🚗 Smart Parking Management System")
st.caption("Python | OOPS | SQLite Database")

total, occupied, available = manager.get_stats()
records = manager.get_records()

st.markdown("### Parking Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Total Slots", total)
c2.metric("Occupied Slots", occupied)
c3.metric("Available Slots", available)

st.divider()

st.subheader("🅿️ Parking Slot Status")

active_records = [r for r in records if r["status"] == "Parked"]
slot_data = {r["slot_number"]: r for r in active_records}

for start in range(1, TOTAL_SLOTS + 1, 5):
    cols = st.columns(5)
    for i, col in enumerate(cols):
        slot = start + i
        if slot > TOTAL_SLOTS:
            continue

        with col:
            if slot in slot_data:
                vehicle = slot_data[slot]
                st.markdown(f"""
                <div class="slot busy">
                    🔴 SLOT {slot}<br>
                    {vehicle['vehicle_number']}<br>
                    {vehicle['vehicle_type']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="slot free">
                    🟢 SLOT {slot}<br>
                    AVAILABLE
                </div>
                """, unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "🚘 Vehicle Entry",
    "🚪 Vehicle Exit",
    "📋 Parking History",
    "🔍 Search & Report"
])

with tab1:
    st.subheader("Vehicle Entry")

    with st.form("entry_form"):
        number = st.text_input("Vehicle Number", placeholder="DL01AB1234")
        vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike"])
        submit = st.form_submit_button("Park Vehicle")

        if submit:
            success, message = manager.park_vehicle(number, vehicle_type)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

with tab2:
    st.subheader("Vehicle Exit")

    with st.form("exit_form"):
        exit_number = st.text_input("Vehicle Number")
        exit_submit = st.form_submit_button("Exit Vehicle")

        if exit_submit:
            if not exit_number.strip():
                st.error("Please enter vehicle number.")
            else:
                success, message = manager.remove_vehicle(exit_number)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with tab3:
    st.subheader("Complete Parking History")

    if records:
        st.dataframe(
            [dict(r) for r in records],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No parking records available.")

with tab4:
    st.subheader("🔍 Search Vehicle")

    search_number = st.text_input("Enter Vehicle Number")

    if st.button("Search Vehicle"):
        results = [
            dict(r) for r in records
            if r["vehicle_number"] == search_number.strip().upper()
        ]

        if results:
            st.success("Vehicle Found!")
            st.dataframe(results, use_container_width=True)
        else:
            st.error("Vehicle not found!")

    st.divider()

    st.subheader("💰 Parking Collection")

    total_collection = sum(
        r["amount"] for r in records
        if r["status"] == "Exited"
    )

    st.metric("Total Collection", f"₹ {total_collection}")

    car_count = sum(1 for r in records if r["vehicle_type"] == "Car")
    bike_count = sum(1 for r in records if r["vehicle_type"] == "Bike")

    c1, c2 = st.columns(2)
    c1.metric("Total Cars", car_count)
    c2.metric("Total Bikes", bike_count)

st.divider()
st.caption("Smart Parking Management System | Developed using Python OOPS")
