import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Título de la app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Entrada de texto para el nombre en la orden
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Cargar la tabla de opciones de frutas
fruit_df = session.table("smoothies.public.fruit_options")
fruit_list = fruit_df.select("FRUIT_NAME").to_pandas()["FRUIT_NAME"].tolist()

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
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        # Petición a la API usando la fruta seleccionada
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        # Muestra la información nutricional en un dataframe
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Botón de envío de orden
    if st.button("Submit Order"):
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED)
            VALUES ('{name_on_order}', '{ingredients_string.strip()}', FALSE)
            """
        ).collect()

        st.success("✅ Your Smoothie Order has been placed!")




