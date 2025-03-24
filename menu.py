import streamlit as st
import gspread
import pandas as pd
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

import streamlit as st

# Hide Streamlit elements
st.set_page_config(page_title="Menu", page_icon="🍽️", layout="centered")

hide_elements = """
    <style>
    #MainMenu {visibility: hidden;}  /* Hide the menu */
    header {visibility: hidden;}    /* Hide the top-right icons */
    footer {visibility: hidden;}    /* Hide the Streamlit footer */
    </style>
    <script>
    // Hide the "Manage App" button
    setInterval(function() {
        var elements = document.querySelectorAll('[data-testid="stStatusWidget"]');
        elements.forEach(el => el.style.display = 'none');
    }, 100);
    </script>
"""
st.markdown(hide_elements, unsafe_allow_html=True)
st.markdown(
    """
    <style>
    [data-testid="stStatusWidget"] {position: absolute; bottom: -100px; visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)



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
    price = row.get("Price (₹)", 0)  # Default to 0 if missing

    # Convert price to a proper format
    if isinstance(price, str):  
        price = price.strip()  
        price = price.replace("₹", "").replace(",", "")  # Remove ₹ symbols and commas
        price = float(price) if price.isnumeric() else "Not Available"

    available = row.get("Available", "").strip().lower()

    if category and item:  # Ensure valid category and item
        if category not in menu:
            menu[category] = {}
        if available in ["yes", "y"]:  # Allow different yes formats
            menu[category][item] = price  

# Streamlit UI
# Define the correct image path
image_url = "https://github.com/mubeenkab123/Josettanmenu/blob/main/download%20(1).jpg"

st.image(image_url, width=200)  # Display the image in Streamlit
   
st.title("🍽️ Menu")
st.write("Select items and place your order!")

# Define category emojis
category_emojis = {
    "Biryani": "🍛",
    "Fried Rice": "🍚",
    "Chinese": "🥢",
    "Pizza": "🍕",
    "Burgers": "🍔",
    "Desserts": "🍰",
    "Beverages": "🥤",
    "Seafood": "🦞",
    "Salads": "🥗",
    "Soups": "🍜",
    "Pasta": "🍝",
    "Main Course": "🍽️",
}

selected_items = {}  # Define before using it

# Display Menu Categories with Emojis
for category, items in menu.items():
    emoji = category_emojis.get(category, "🍽️")  # Default emoji if category not found
    with st.expander(f"{emoji} **{category}**"):
        for item, price in items.items():
            quantity = st.number_input(f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}")
            if quantity > 0:
                selected_items[item] = quantity  # Now it will work without error

# Add Name and Phone Number Input Fields
name = st.text_input("Enter your name:")
phone = st.text_input("Enter your phone number:", max_chars=10, help="Enter a 10-digit phone number")
# Add Table Number Input Field
table_number = st.text_input("Enter your table number:", help="Enter your assigned table number")

# Ensure the input fields are styled properly
st.markdown("<style> label { color: white; font-size: 18px; } </style>", unsafe_allow_html=True)

# Order Processing
if st.button("✅ Place Order"):
    if not name:
        st.warning("⚠️ Please enter your name.")
    elif not phone or not phone.isdigit() or len(phone) != 10:
        st.warning("⚠️ Please enter a valid 10-digit phone number.")
    elif not table_number.strip():
        st.warning("⚠️ Please enter your table number.")
    elif selected_items:
        total_price = sum(menu[cat][item] * qty for cat in menu for item, qty in selected_items.items() if item in menu[cat])
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_str = ", ".join([f"{item}({qty})" for item, qty in selected_items.items()])

        # Save order to Google Sheets
        db = client.open("RestaurantOrders").sheet1
        db.append_row([name, phone, table_number, order_time, order_str, total_price])

        st.success(f"✅ Order placed successfully!\n\n🛒 Items: {order_str}\n📞 Phone: {phone}\n🪑 Table: {table_number}\n💰 Total: ₹ {total_price}")
    else:
        st.warning("⚠️ Please select at least one item to order.")

