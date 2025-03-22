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



# Ensure column names are clean (remove spaces, avoid KeyErrors)
df_menu.columns = df_menu.columns.str.strip()

# Convert DataFrame to Menu Dictionary
menu = {}
for _, row in df_menu.iterrows():
    category = row.get("Category", "").strip()
    item = row.get("Item Name", "").strip()
    price = row.get("Price", 0)  # Default price to 0 if missing
    available = row.get("Available", "No").strip()

    if category and item:  # Ensure valid category and item
        if category not in menu:
            menu[category] = {}
        if available.lower() == "yes":
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

# User Input
name = st.text_input("Enter your name:")

# Initialize selected_items dictionary before use
selected_items = {}

# Display Menu from Google Sheets
for category, items in menu.items():
    with st.expander(f"{category_emojis.get(category, '')} {category}"):
        for item, price in items.items():
            quantity = st.number_input(
                f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}"
            )
            if quantity > 0:
                selected_items[item] = quantity

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

