import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open Google Sheets (menudata file → menu_data sheet)
menu_sheet = client.open("menudata").worksheet("menu_data")    
menu_data = menu_sheet.get_all_records()
df_menu = pd.DataFrame(menu_data)

# Ensure column names are clean (remove spaces)
df_menu.columns = df_menu.columns.str.strip()

# Convert DataFrame to Menu Dictionary
menu = {}
for _, row in df_menu.iterrows():
    category = row.get("Category", "").strip()
    item = row.get("Item Name", "").strip()
    price = row.get("Price", "Not Available")
    available = row.get("Available", "").strip().lower()

    if category and item:
        if category not in menu:
            menu[category] = {}
        if available in ["yes", "y"]:
            menu[category][item] = price  

# Custom CSS for Round - The Global Diner Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Merriweather&display=swap');
    
    body {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Merriweather', serif;
    }
    .header {
        background-color: #002060;
        padding: 15px;
        text-align: center;
        color: #FFD700;
        font-family: 'Montserrat', sans-serif;
        font-size: 30px;
        border-radius: 10px;
    }
    .menu-section {
        margin: 20px 0;
        padding: 10px;
        border-left: 5px solid #002060;
    }
    .menu-item {
        border-bottom: 1px solid #DDD;
        padding: 10px 0;
        font-size: 18px;
    }
    .menu-item h3 {
        color: #002060;
    }
    .menu-item p {
        color: #555;
    }
    .order-button {
        background-color: #FFD700;
        color: #002060;
        padding: 10px 15px;
        border-radius: 5px;
        font-size: 18px;
        cursor: pointer;
    }
    </style>
    ", unsafe_allow_html=True)

# Header
st.markdown('<div class="header">Round - The Global Diner Thrissur</div>', unsafe_allow_html=True)

# Menu Display
st.write("## Explore Our Menu")
selected_items = {}

for category, items in menu.items():
    st.markdown(f"<div class='menu-section'><h2>{category}</h2></div>", unsafe_allow_html=True)
    for item, price in items.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<div class='menu-item'><h3>{item}</h3></div>", unsafe_allow_html=True)
        with col2:
            quantity = st.number_input(f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}")
            if quantity > 0:
                selected_items[item] = quantity

# User Input
name = st.text_input("Enter your name:")

# Order Processing
if st.button("✅ Place Order", key="order_button"):
    if not name:
        st.warning("⚠️ Please enter your name.")
    elif selected_items:
        total_price = sum(menu[cat][item] * qty for cat in menu for item, qty in selected_items.items() if item in menu[cat])
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_str = ", ".join([f"{item}({qty})" for item, qty in selected_items.items()])
        
        # Save order to Google Sheets
        db = client.open("RestaurantOrders").sheet1
        db.append_row([name, order_time, order_str, total_price])
        
        st.success(f"✅ Order placed successfully!\n\n🛒 Items: {order_str}\n💰 Total: ₹ {total_price}")
    else:
        st.warning("⚠️ Please select at least one item to order.")
