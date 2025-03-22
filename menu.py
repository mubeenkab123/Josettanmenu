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
st.title("🍽️ Hotel Menu (Dynamic from Google Sheets)")
st.write("Select items and place your order!")

category_emojis = {
    "Starters": "🍤",
    "Main Course": "🍛",
    "Desserts": "🍰",
    "Beverages": "🥤",
    "Biryani": "🍚",
    "Pizza": "🍕",
    "Burgers": "🍔",
    "Sandwiches": "🥪",
    "Seafood": "🦞",
    "Salads": "🥗",
    "Soups": "🍜",
    "Pasta": "🍝",
    "Chinese": "🍜",
}
# Display Menu
selected_items = {}
for category, items in menu.items():
    with st.expander(f"{category}"):
        for item, price in items.items():
            # Show price correctly in UI
            st.write(f"{item} - ₹ {price}" if isinstance(price, (int, float)) else f"{item} - Price Not Available")
            
            quantity = st.number_input(
                f"{item} (₹ {price})" if isinstance(price, (int, float)) else f"{item} (Price Not Available)", 
                min_value=0, max_value=10, step=1, key=f"{category}_{item}"
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


