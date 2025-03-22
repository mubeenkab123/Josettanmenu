import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# Google Sheets Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Get credentials from Streamlit secrets
creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open Google Sheet
db = client.open("RestaurantOrders").sheet1

# Category Emoji Mapping
category_emojis = {
    "Mandi (Manthi)": "🍗",
    "Shawarma": "🌯",
    "Fish Specialties": "🐟",
    "Fried Rice": "🍚",
    "Noodles": "🍜",
    "Chinese - Vegetarian": "🥬",
    "Chinese - Chicken Dishes": "🐔",
    "North Indian Dishes": "🍛",
    "Chop Suey": "🥡",
    "Soups - Veg": "🍲",
    "Soups - Non-Veg": "🍖",
    "Beef Specialties": "🐄",
    "Biryani": "🥘",
    "Al-Faham (Grilled Chicken)": "🔥",
    "Rice Combos": "🍱",
    "Kothu Porotta": "🥘🔥",
    "Rotis & Breads": "🫓",
    "Starters": "🍢"
}

# Complete Menu Structure
menu = {
    "Mandi (Manthi)": {
        "Full Kuzhi Manthi": 840,
        "Half Kuzhi Manthi": 420,
        "Quarter Kuzhi Manthi": 210,
        "Full Al-Faham Manthi": 840,
        "Half Al-Faham Manthi": 420,
        "Quarter Al-Faham Manthi": 210,
        "1 Kg Manthi Rice": 190,
        "Manthi Rice": 120,
        "Full Peri Peri Manthi": 860,
        "Half Peri Peri Manthi": 430,
        "Quarter Peri Peri Manthi": 220,
        "Full Mexican Manthi": 860,
        "Half Mexican Manthi": 430,
        "Quarter Mexican Manthi": 220,
        "Full Shawai Manthi": 860,
        "Half Shawai Manthi": 430,
        "Quarter Shawai Manthi": 220
    },
    "Shawarma": {
        "Shawarma Plate (Kuboos)": 200,
        "Shawarma Plate (Rumali)": 220,
        "Shawarma Roll (Kuboos)": 150,
        "Shawarma Roll (Meat Only)": 170,
        "Shawarma Roll (Spice - Kuboos)": 160,
        "Shawarma Roll (Cheesy - Kuboos)": 170,
        "Shawarma Roll (Rumali)": 160,
        "Shawarma Roll (Spicy - Rumali)": 180,
        "Shawarma Roll (Cheesy - Rumali)": 180,
        "Shawarma Plate Meat (Rumali)": 270,
        "Shawarma Plate Meat (Kuboos)": 240
    },
    "Fish Specialties": {
        "Al-Faham Fish + Manthi Rice or Kaima Rice": 380,
        "Al-Faham Fish (Peri Peri) + Manthi Rice or Kaima Rice": 400,
        "Al-Faham Fish (Kanthari) + Manthi Rice or Kaima Rice": 400
    },
    "Fried Rice": {
        "Veg Fried Rice (Small)": 140,
        "Veg Fried Rice (Medium)": 220,
        "Veg Fried Rice (Normal)": 270,
        "Egg Fried Rice (Small)": 160,
        "Egg Fried Rice (Medium)": 240,
        "Egg Fried Rice (Normal)": 300,
        "Chicken Fried Rice (Small)": 170,
        "Chicken Fried Rice (Medium)": 260,
        "Chicken Fried Rice (Normal)": 320,
        "Singapore Fried Rice (Normal)": 330,
        "Singapore Fried Rice (Medium)": 280,
        "Mixed Fried Rice (Normal)": 370,
        "Mixed Fried Rice (Medium)": 300,
        "Szechuan Chicken Fried Rice (Normal)": 370,
        "Szechuan Chicken Fried Rice (Medium)": 300,
        "Extra Egg Fried Rice (Normal)": 350,
        "Extra Egg Fried Rice (Medium)": 270
    },
    "Noodles": {
        "Veg Noodles (Small)": 140,
        "Veg Noodles (Medium)": 220,
        "Veg Noodles (Normal)": 270,
        "Egg Noodles (Small)": 160,
        "Egg Noodles (Medium)": 240,
        "Egg Noodles (Normal)": 300,
        "Chicken Noodles (Small)": 170,
        "Chicken Noodles (Medium)": 260,
        "Chicken Noodles (Normal)": 320,
        "Singapore Noodles (Normal)": 330,
        "Singapore Noodles (Medium)": 280,
        "Mixed Noodles (Normal)": 370,
        "Mixed Noodles (Medium)": 300,
        "Szechuan Chicken Noodles (Normal)": 370,
        "Szechuan Chicken Noodles (Medium)": 300,
        "Extra Egg Noodles (Normal)": 350,
        "Extra Egg Noodles (Medium)": 270
    },
    "Chinese - Vegetarian": {
        "Chilly Gobi (Single)": 130,
        "Chilly Gobi (Normal)": 170,
        "Gobi Manchurian (Single)": 140,
        "Gobi Manchurian (Normal)": 180,
        "Paneer Butter Masala (Single, 8 pcs)": 180,
        "Paneer Butter Masala (Normal, 12 pcs)": 240,
        "Chilly Paneer": 200,
        "Chilly Paneer Dry": 210,
        "Veg Kuruma": 60,
        "Szechuan Veg": 100,
        "Chilly Mushroom": 190,
        "Mushroom Masala": 200,
        "Tomato Fry": 110,
        "Veg Kadai Masala": 210,
        "Egg Roast": 60,
        "Mushroom Manchurian": 180
    },
    "Chinese - Chicken Dishes": {
        "Chilly Chicken (Small - 4 pcs)": 120,
        "Chilly Chicken (Single - 8 pcs)": 170,
        "Chilly Chicken (Normal - 12 pcs)": 230,
        "Garlic Chicken (Small - 4 pcs)": 120,
        "Garlic Chicken (Single - 8 pcs)": 170,
        "Garlic Chicken (Normal - 12 pcs)": 230,
        "Ginger Chicken (Small - 4 pcs)": 120,
        "Ginger Chicken (Single - 8 pcs)": 170,
        "Ginger Chicken (Normal - 12 pcs)": 230,
        "Chicken Manchurian": 220,
        "Dragon Chicken": 220,
        "Pepper Chicken": 220,
        "Ginger Garlic Chicken": 240,
        "Sweet and Sour Chicken": 200,
        "SZ Chilly Chicken": 200 
    },
    "North Indian Dishes": {
        "Chicken Roast (1 pcs)": 120,
        "Chicken Roast (2 pcs)": 150,
        "Chicken Roast (3 pcs)": 190,
        "Chicken Fry (3 pcs)": 200,
        "Chicken Chettinad": 200,
        "Chicken Mughlai": 210,
        "Chicken Kondattam": 210,
        "Chicken Lollipop": 210,
        "Chicken 65": 230,
        "Chicken Kolhapuri": 220,
        "Butter Chicken": 220,
        "Kadai Chicken": 220
    },
    "Chop Suey": {
        "American Veg Chopsuey": 200,
        "Chinese Veg Chopsuey": 200,
        "American Chicken Chopsuey": 240,
        "Chinese Chicken Chopsuey": 240
    },
    "Soups - Veg": {
        "Mushroom Soup": 110,
        "Tomato Soup": 110,
        "Sweet Corn Veg Soup": 130,
        "Clear Veg Soup": 130,
        "Hot & Sour Veg Soup": 130
    },
    "Soups - Non-Veg": {
        "Chicken Noodle Soup": 160,
        "Clear DF Chicken Soup": 160,
        "Hot & Sour Chicken Soup": 160,
        "Sweet Corn Chicken Soup": 160,
        "Manchow Chicken Soup": 160,
        "Clear Chicken Soup": 160
    },
    "Beef Specialties": {
        "Beef Roast": 170,
        "Beef Fry": 180,
        "Beef with Vegetables": 190,
        "Beef Dry Fry": 200,
        "Beef in Oyster Sauce": 220,
        "Chilly Beef": 230,
        "Garlic Beef": 230,
        "Ginger Beef": 230,
        "Pepper Beef": 230,
        "Dragon Beef": 230,
        "Beef Kondattam": 230
    },
    "Biryani": {
        "Chicken Biryani (600 gm)": 200,
        "Beef Biryani (600 gm)": 210,
        "Fish Biryani (600 gm)": 240,
        "Mutton Biryani (600 gm)": 280,
        "Prawns Biryani (600 gm)": 240,
        "Veg Biryani (600 gm)": 150,
        "Egg Biryani": 170,
        "1 Kg Chicken Biryani": 300,
        "1 Kg Beef Biryani": 320,
        "1 Kg Egg Biryani": 270,
        "1 Kg Veg Biryani": 260,
        "Biryani Rice": 130,
        "1 Kg Biryani Rice": 210,
        "Half Biryani Rice": 70,
        "Ghee Rice (600 gm)": 180,
        "Curd Rice (600 gm)": 180
    },
    "Al-Faham (Grilled Chicken)": {
        "Grilled Chicken Full": 590,
        "Grilled Chicken Half": 310,
        "Grilled Chicken Full Mexican": 600,
        "Grilled Chicken Half Mexican": 320,
        "Al-Faham Chicken Full": 520,
        "Al-Faham Chicken Half": 270,
        "Al-Faham Chicken Quarter": 140,
        "Al-Faham Chicken Full (Peri Peri)": 580,
        "Al-Faham Chicken Half (Peri Peri)": 300,
        "Al-Faham Chicken Quarter (Peri Peri)": 170,
        "Al-Faham Chicken Full (Green Pepper)": 580,
        "Al-Faham Chicken Half (Green Pepper)": 300,
        "Al-Faham Chicken Quarter (Green Pepper)": 170,
        "Al-Faham Chicken Full (Lebanese)": 580,
        "Al-Faham Chicken Half (Lebanese)": 300,
        "Al-Faham Chicken Quarter (Lebanese)": 170,
        "Al-Faham Chicken Full (Mexican)": 580,
        "Al-Faham Chicken Half (Mexican)": 300,
        "Al-Faham Chicken Quarter (Mexican)": 170,
        "Al-Faham Chicken Full (Kanthari)": 580,
        "Al-Faham Chicken Half (Kanthari)": 300,
        "Al-Faham Chicken Quarter (Kanthari)": 170,
        "Al-Faham Chicken Full (Honey Flavored)": 580,
        "Al-Faham Chicken Half (Honey Flavored)": 300,
        "Al-Faham Chicken Quarter (Honey Flavored)": 170
    },
    "Rice Combos": {
        "Full Al-Faham with 2 Kg Kaima Rice": 860,
        "Half Al-Faham with 1 Kg Kaima Rice": 430,
        "Full Peri Peri Chicken + 2 Kg Kaima Rice": 840,
        "Half Peri Peri Chicken + 1 Kg Kaima Rice": 420,
        "Ghee Rice (250g) + Butter Chicken (Single Person)": 100,
        "Chicken Fried Rice (250g) + Chilly Chicken (2 pcs) (Single Person)": 100,
        "Ghee Rice (250g) + Beef Roast (Single Person)": 100,
        "Chicken Fried Rice + Chilly Chicken (8 pcs) (3 Persons)": 470,
        "Egg Fried Rice + Chilly Chicken (8 pcs) (3 Persons)": 440,
        "Veg Fried Rice + Chilly Gobi (8 pcs) (3 Persons)": 380
    },
    "Kothu Porotta":{
        "Kothu Porotta Beef": 200,
        "Kothu Porotta Chicken": 180,
        "Kothu Porotta Egg": 160
    },
    "Rotis & Breads": {
        "Nool Porotta": 30,
        "Chapati": 15,
        "Porotta": 15,
        "Rumali Roti": 20,
        "Kuboos": 10
    },
    "Starters": {
        "Chicken Wings (8 pcs)": 200,
        "Chicken Lollipop (8 pcs)": 210,
        "Chicken 65 (10 pcs)": 230,
        "Chilly Chicken Dry (8 pcs)": 200,
        "Beef Dry Fry (BDF)": 200,
        "Gobi 65": 180
    }
}

# Streamlit UI
st.title("🍽️ CookDoor Menu")
st.write("Select items and place your order!")

# User Details (Only name now)
name = st.text_input("Enter your name:")

# Order Form with Collapsible Categories
selected_items = {}

for category, items in menu.items():
    with st.expander(f"{category_emojis[category]} {category}", expanded=False):
        for item, price in items.items():
            quantity = st.number_input(
                f"{item} (₹ {price})" if price else f"{item} (Price TBD)",
                min_value=0,
                max_value=10,
                step=1,
                key=f"{category}_{item}"
            )
            if quantity > 0:
                selected_items[item] = quantity

# Place Order Button
if st.button("✅ Place Order"):
    if not name:
        st.warning("⚠️ Please enter your name.")
    elif selected_items:
        total_price = sum(menu[category][item] * qty 
                     for category in menu
                     for item, qty in selected_items.items() 
                     if item in menu[category])
        
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_details = [f"{item}({qty})" for item, qty in selected_items.items()]
        order_str = ", ".join(order_details)
        
        # Updated order data without contact
        order_data = [name, order_time, order_str, total_price]
        db.append_row(order_data)
        
        st.success(f"✅ Order placed successfully!\n\n🛒 Items: {order_str}\n💰 Total: ₹ {total_price}")
    else:
        st.warning("⚠️ Please select at least one item to order.")

# Display Past Orders
if st.checkbox("📜 View Previous Orders"):
    st.subheader("Order History")
    orders = db.get_all_values()
    if len(orders) > 1:
        # Updated columns without contact
        df = pd.DataFrame(orders[1:], columns=["Name", "Time", "Items", "Total Price"])
        st.dataframe(df)
    else:
        st.write("No past orders found.")