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

# Open Google Sheets (Replace "menu_data" with your actual sheet name)
menu_sheet = client.open("menu_data").sheet1  
menu_data = menu_sheet.get_all_records()
df_menu = pd.DataFrame(menu_data)

# Convert DataFrame to Menu Dictionary
menu = {}
for _, row in df_menu.iterrows():
    category = row["Category"]
    item = row["Item Name"]
    price = row["Price"]
    available = row["Available"]

    if category not in menu:
        menu[category] = {}

    # Add only available items
    if available.lower() == "yes":
        menu[category][item] = price  

# Category Emojis (Optional)
category_emojis = {
    "Biryani": "🥘",
    "Fried Rice": "🍚",
    "Chinese - Chicken": "🐔",
    "Beverages": "🥤"
}

# Streamlit UI
st.title("🍽️ Hotel Menu (Dynamic from Google Sheets)")
st.write("Select items and place your order!")



# Display Menu from Google Sheets
for category, items in menu.items():
    with st.expander(f"{category_emojis.get(category, '')} {category}"):
        for item, price in items.items():
            quantity = st.number_input(f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}")
            if quantity > 0:
                selected_items[item] = quantity
# User Input
name = st.text_input("Enter your name:")
selected_items = {}                

# Order Processing
if st.button("✅ Place Order"):
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



