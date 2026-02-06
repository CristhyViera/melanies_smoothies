import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Título de la app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Entrada de texto para el nombre en la orden
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# --- CARGA DE DATOS ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

fruit_list = pd_df['FRUIT_NAME'].tolist()

# Widget de selección múltiple
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Lógica cuando el usuario selecciona ingredientes
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # BUSCAR EL VALOR DE SEARCH_ON usando LOC
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # PETICIÓN A LA API
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # --- CAMBIO CLAVE PARA EL DESAFÍO DORA ---
    # Creamos un checkbox para que tú decidas si la orden nace como LLENA (TRUE) o no (FALSE)
    order_filled_status = st.checkbox("Mark order as FILLED")

    # Botón de envío de orden
    if st.button("Submit Order"):
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED)
            VALUES ('{name_on_order}', '{ingredients_string.strip()}', {order_filled_status})
            """
        ).collect()

        st.success("✅ Your Smoothie Order has been placed!")

