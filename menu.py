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
    price = row.get("Price (₹)", 0)
    image_url = row.get("Image URL", "").strip()  # New: Add image URLs
    available = row.get("Available", "").strip().lower()

    if isinstance(price, str):  
        price = price.strip().replace("₹", "").replace(",", "")  
        price = float(price) if price.isnumeric() else "Not Available"

    if category and item and available in ["yes", "y"]:  
        if category not in menu:
            menu[category] = []
        menu[category].append({"name": item, "price": price, "image": image_url})

# Streamlit UI
st.set_page_config(page_title="Hotel Menu", layout="wide")

# Header Styling
st.markdown("""
    <style>
        .header-container {
            text-align: center;
            background-color: #1A012D; /* Match logo background */
            padding: 20px;
            border-radius: 10px;
            width: 100%;
        }
        .logo {
            display: block;
            margin: auto;
            max-width: 150px;
            height: auto;
        }
        .category-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 20px;
        }
        .category-btn {
            padding: 12px;
            margin: 5px;
            background: #f5f5f5;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
            transition: 0.3s;
        }
        .category-btn:hover {
            background: #ddd;
        }
        .floating-cart {
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: #ff4b4b;
            color: white;
            padding: 10px 15px;
            border-radius: 10px;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

# Display Logo
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.image("https://raw.githubusercontent.com/mubeenkab123/Hotel-menu/main/download.jpg", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Page Title
st.markdown("<h1 style='text-align: center;'>Hotel Menu (Dynamic from Google Sheets)</h1>", unsafe_allow_html=True)

# Display Categories as Buttons
st.markdown("<div class='category-container'>", unsafe_allow_html=True)
for category in menu.keys():
    if st.button(category):
        selected_category = category
st.markdown("</div>", unsafe_allow_html=True)

# Display Menu Items
selected_items = {}
if 'selected_category' in locals():
    st.subheader(f"📌 {selected_category}")

    for item in menu[selected_category]:
        col1, col2 = st.columns([1, 3])
        with col1:
            if item["image"]:
                st.image(item["image"], width=80)
        with col2:
            quantity = st.number_input(f"{item['name']} - ₹{item['price']}", min_value=0, max_value=10, step=1, key=item["name"])
            if quantity > 0:
                selected_items[item["name"]] = {"quantity": quantity, "price": item["price"]}

# Add Name Input Field
name = st.text_input("Enter your name:")
st.markdown("<style> label { color: white; font-size: 18px; } </style>", unsafe_allow_html=True)

# Floating Cart Summary
if selected_items:
    total_price = sum(item["price"] * item["quantity"] for item in selected_items.values())
    st.markdown(f"<div class='floating-cart'>🛒 {len(selected_items)} Items - ₹{total_price}</div>", unsafe_allow_html=True)

# Order Processing
if st.button("✅ Place Order"):
    if not name:
        st.warning("⚠️ Please enter your name.")
    elif selected_items:
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_str = ", ".join([f"{item}({details['quantity']})" for item, details in selected_items.items()])
        
        # Save order to Google Sheets
        db = client.open("RestaurantOrders").sheet1
        db.append_row([name, order_time, order_str, total_price])
        
        st.success(f"✅ Order placed successfully!\n\n🛒 Items: {order_str}\n💰 Total: ₹{total_price}")
    else:
        st.warning("⚠️ Please select at least one item to order.")
