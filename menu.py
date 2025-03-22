import streamlit as st
import gspread
import pandas as pd
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json


# Load JSON file properly
json_path = "/mnt/data/restaurento-1127906dfe27.json"  # Update with the correct path
with open(json_path, "r") as file:
    creds_dict = json.load(file)

# Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

st.success("✅ Google Sheets authentication successful!")


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
        try:
            total_price = sum(menu[cat][item] * qty for cat in menu for item, qty in selected_items.items() if item in menu[cat])
            order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_str = ", ".join([f"{item}({qty})" for item, qty in selected_items.items()])
            
            # Open the correct Google Sheet
            try:
                orders_sheet = client.open("RestaurantOrders").sheet1  # Opens the first sheet
            except gspread.exceptions.SpreadsheetNotFound:
                st.error("⚠️ 'RestaurantOrders' file not found! Make sure the file name is correct.")
                st.stop()

            # Append new order data
            orders_sheet.append_row([name, order_time, order_str, total_price])

            st.success(f"✅ Order placed successfully!\n\n🛒 Items: {order_str}\n💰 Total: ₹ {total_price}")
        except gspread.exceptions.APIError as e:
            st.error(f"⚠️ Google Sheets API Error: {e}")
    else:
        st.warning("⚠️ Please select at least one item to order.")
