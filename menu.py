import streamlit as st
import gspread
import pandas as pd
import os
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

# Convert DataFrame to Menu Dictionary
menu = {}
for _, row in df_menu.iterrows():
    category = row.get("Category", "").strip()
    item = row.get("Item Name", "").strip()
    price = row.get("Price (₹)", "0")  # Default to "0" to avoid errors

    # Convert price to a proper format
    try:
        price = float(str(price).replace("₹", "").replace(",", "").strip())
    except ValueError:
        price = "Not Available"

    available = row.get("Available", "").strip().lower()

    if category and item and available in ["yes", "y"]:  # Ensure valid category and available item
        if category not in menu:
            menu[category] = {}
        menu[category][item] = price  

# Streamlit UI
image_url = "https://raw.githubusercontent.com/mubeenkab123/Hotel-menu/refs/heads/main/download.jpg"
st.image(image_url, width=200)  # Display logo
st.title("🍽️ Menu")
st.write("Select items and place your order!")

# Define category emojis
category_emojis = {
    "Biryani": "🍛", "Fried Rice": "🍚", "Chinese": "🥢", "Pizza": "🍕",
    "Burgers": "🍔", "Desserts": "🍰", "Beverages": "🥤", "Seafood": "🦞",
    "Salads": "🥗", "Soups": "🍜", "Pasta": "🍝", "Main Course": "🍽️",
}

# **Initialize selected_items dictionary**
selected_items = {}

# Display Menu Categories with Emojis
for category, items in menu.items():
    emoji = category_emojis.get(category, "🍽️")  # Default emoji if category not found
    with st.expander(f"{emoji} **{category}**"):
        for item, price in items.items():
            if isinstance(price, (int, float)):  # Ensure only numeric prices are selectable
                quantity = st.number_input(f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}")
                if quantity > 0:
                    selected_items[item] = quantity

# **Add Name Input Field**
name = st.text_input("Enter your name:")

# **Order Processing**
if st.button("✅ Place Order"):
    if not name:
        st.warning("⚠️ Please enter your name.")
    elif selected_items:
        total_price = sum(menu[cat][item] * qty for cat in menu for item, qty in selected_items.items() if item in menu[cat])
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_str = ", ".join([f"{item}({qty})" for item, qty in selected_items.items()])
        
        # **Save order to Google Sheets**
        db = client.open("RestaurantOrders").sheet1
        db.append_row([name, order_time, order_str, total_price])
        
        st.success(f"✅ Order placed successfully!\n\n🛒 Items: {order_str}\n💰 Total: ₹ {total_price}")
    else:
        st.warning("⚠️ Please select at least one item to order.")
