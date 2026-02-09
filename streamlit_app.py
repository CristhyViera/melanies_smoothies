import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

cnx = st.connection("snowflake")
session = cnx.session()

# Carga de datos
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
fruit_list = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    # Unimos la lista con espacios para evitar espacios extra al inicio o final
    ingredients_string = ' '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(fruit_chosen + ' Nutrition Information')
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except:
            st.error(f"Could not find nutrition info for {fruit_chosen}")

    # Checkbox para cumplir con el estado de "ORDER_FILLED"
    order_filled_status = st.checkbox("Mark order as FILLED")

    if st.button("Submit Order"):
        # Importante: name_on_order no debe estar vacío
        if name_on_order:
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED)
                VALUES ('{name_on_order}', '{ingredients_string}', {order_filled_status})
            """
            
            try:
                session.sql(my_insert_stmt).collect()
                st.success(f"✅ Your Smoothie Order has been placed, {name_on_order}!")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
        else:
            st.warning("Please add a name for the order.")
