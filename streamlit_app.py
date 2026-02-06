import streamlit as st
from snowflake.snowpark.functions import col
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake (Streamlit Cloud way)
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options table
fruit_df = session.table("smoothies.public.fruit_options")

# Convert fruit column into a Python list
fruit_list = fruit_df.select("FRUIT_NAME").to_pandas()["FRUIT_NAME"].tolist()

# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# When user selects ingredients
if ingredients_list:

    # Build ingredients string
    ingredients_string = ", ".join(ingredients_list)

    st.write("You selected:", ingredients_string)

    # Submit button
    if st.button("Submit Order"):

        # Insert into orders table
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED)
            VALUES ('{name_on_order}', '{ingredients_string}', FALSE)
            """
        ).collect()

        st.success("✅ Your Smoothie Order has been placed!")




