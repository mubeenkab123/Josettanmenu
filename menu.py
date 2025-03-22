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

# Open Google Sheets
menu_sheet = client.open_by_key("1ILbYNRM-UWth_wm_X48TkzUEyvDT92bcCggVI6COUKg").worksheet("menu_data")    
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

    if available.lower() == "yes":
        menu[category][item] = price  

# Streamlit UI Custom Styling
st.markdown(
    """
    <style>
        /* Set background color */
        .stApp {
            background-color: #1A0E1E; /* Dark Purple from logo */
            color: white;
        }
        /* Style buttons */
        div.stButton > button {
            background-color: #FFC107; /* Yellow */
            color: black;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }
        /* Style text input */
        input[type="text"] {
            background-color: #333;
            color: white;
            border: 2px solid #FFC107;
            padding: 8px;
            font-size: 16px;
        }
        /* Style category headers */
        .st-expander-header {
            color: #FFC107 !important;
            font-weight: bold;
            font-size: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Display Logo
st.image("/mnt/data/image.png", width=250)  # Use the uploaded image path

st.write("### Welcome to Round - The Global Diner 🍽️")
st.write("Select your favorite dishes and place an order!")

# User Input
name = st.text_input("Enter your name:")
selected_items = {}

# Display Menu
for category, items in menu.items():
    with st.expander(f"🍽️ **{category}**"):
        for item, price in items.items():
            quantity = st.number_input(f"{item} (₹ {price})", min_value=0, max_value=10, step=1, key=f"{category}_{item}")
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
