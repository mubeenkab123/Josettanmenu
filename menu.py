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
            background-color: #FFC107; /* Yellow from logo */
            color: black;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }
        /* Style inputs */
        input[type="text"] {
            background-color: #333;
            color: white;
            border: 1px solid #FFC107;
        }
        /* Style expanders */
        .st-expander {
            background-color: #2D1B33;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Display Logo
st.image("https://theround.in/assets/images/logo.png", width=250)  # Using the online logo

st.write("### Welcome to Round - The Global Diner 🍽️")
st.write("Select your favorite dishes and place an order!")
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

