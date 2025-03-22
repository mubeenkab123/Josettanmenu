import streamlit as st
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ========== 🔹 GOOGLE SHEETS AUTHENTICATION 🔹 ==========
# File uploader for JSON credentials
st.title("🍽️ Restaurant Ordering System")
uploaded_file = st.file_uploader("📂 Upload Google Service Account JSON", type=["json"])

if uploaded_file:
    # Save the uploaded file to /mnt/data/
    json_path = "/mnt/data/service_account.json"
    with open(json_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("✅ JSON file uploaded successfully! Now restart the app.")

# Check if the JSON file exists
json_path = "/mnt/data/service_account.json"
if not os.path.exists(json_path):
    st.error("❌ No Google Service Account JSON file found. Please upload the file above.")
    st.stop()

# Load JSON credentials
try:
    with open(json_path, "r") as file:
        creds_dict = json.load(file)

    # Authenticate with Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    st.success("✅ Google Sheets authentication successful!")

except Exception as e:
    st.error(f"⚠️ Authentication Error: {e}")
    st.stop()

# ========== 🔹 FETCH MENU DATA FROM GOOGLE SHEETS 🔹 ==========
try:
    menu_sheet = client.open("menudata").worksheet("menu_data")  # Ensure this file exists!
    menu_data = menu_sheet.get_all_records()
    df_menu = pd.DataFrame(menu_data)
    st.success("✅ Menu data loaded successfully from Google Sheets!")
except gspread.exceptions.SpreadsheetNotFound:
    st.error("❌ 'menudata' spreadsheet not found! Ensure the correct file name is used.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error loading menu data: {e}")
    st.stop()

# Convert menu data into a dictionary
menu = {}
for _, row in df_menu.iterrows():
    category = row.get("Category", "").strip()
    item = row.get("Item Name", "").strip()
    price = row.get("Price (₹)", "0")
    available = row.get("Available", "").strip().lower()

    try:
        price = float(str(price).replace("₹", "").replace(",", "").strip())
    except ValueError:
        price = "Not Available"

    if category and item and available in ["yes", "y"]:  # Only add available items
        if category not in menu:
            menu[category] = {}
        menu[category][item] = price  

# ========== 🔹 DISPLAY MENU UI 🔹 ==========
# Load and display the restaurant logo
image_url = "https://raw.githubusercontent.com/mubeenkab123/Hotel-menu/main/download.jpg"
st.image(image_url, width=200)

st.write("## 📜 Select items and place your order!")

# Category Emojis
category_emojis = {
    "Biryani": "🍛", "Fried Rice": "🍚", "Chinese": "🥢", "Pizza": "🍕",
    "Burgers": "🍔", "Desserts": "🍰", "Beverages": "🥤", "Seafood": "🦞",
    "Salads": "🥗", "Soups": "🍜", "Pasta": "🍝", "Main Course": "🍽️",
}

# Initialize selected items dictionary
selected_items = {}

# Display Menu Categories
for category, items in menu.items():
    emoji = category_emojis.get(category, "🍽️")
    with st.expander(f"{emoji} **{category}**"):
        for item, price in items.items():
            if isinstance(price, (int, float)):
                quantity = st.number_input(f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}")
                if quantity > 0:
                    selected_items[item] = quantity

# ========== 🔹 ORDER PROCESSING 🔹 ==========
# User Name Input
name = st.text_input("👤 Enter your name:")

# Place Order Button
if st.button("✅ Place Order"):
    if not name:
        st.warning("⚠️ Please enter your name.")
    elif selected_items:
        try:
            total_price = sum(menu[cat][item] * qty for cat in menu for item, qty in selected_items.items() if item in menu[cat])
            order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_str = ", ".join([f"{item}({qty})" for item, qty in selected_items.items()])

            # Open the RestaurantOrders Sheet
            try:
                orders_sheet = client.open("RestaurantOrders").sheet1  # Opens first sheet
            except gspread.exceptions.SpreadsheetNotFound:
                st.error("❌ 'RestaurantOrders' file not found! Ensure the file name is correct.")
                st.stop()

            # Append Order
            orders_sheet.append_row([name, order_time, order_str, total_price])
            st.success(f"✅ Order placed successfully!\n🛒 Items: {order_str}\n💰 Total: ₹ {total_price}")

        except gspread.exceptions.APIError as e:
            st.error(f"⚠️ Google Sheets API Error: {e}")

    else:
        st.warning("⚠️ Please select at least one item to order.")
