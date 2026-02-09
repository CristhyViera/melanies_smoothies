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
    # Esta es la forma correcta de crear el string para el HASH de DORA
    ingredients_string = ' '.join(ingredients_list)
    
    # ... (lógica de visualización de nutrición)

    order_filled_status = st.checkbox("Mark order as FILLED")

    if st.button("Submit Order"):
        # Aseguramos que el SQL reciba el string limpio
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED)
            VALUES ('{name_on_order}', '{ingredients_string}', {order_filled_status})
        """
        
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Order placed for {name_on_order}!")

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
