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

# --- CARGA DE DATOS (Challenge Lab) ---
# Cargamos FRUIT_NAME para la lista y SEARCH_ON para la API
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convertimos a Pandas para usar la función LOC
pd_df = my_dataframe.to_pandas()

# --- BLOQUE DE DEPURACIÓN (Comenta estas líneas para que la app avance) ---
# st.dataframe(pd_df)
# st.stop() 
# -----------------------------------------------------------------------

# Convertir la columna FRUIT_NAME en una lista para el multiselect
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
        
        # BUSCAR EL VALOR DE SEARCH_ON: Usamos LOC para encontrar el valor de búsqueda correcto
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.') #
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # PETICIÓN A LA API: Usamos la variable search_on en la URL
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        
        # MOSTRAR DATOS: Mostramos el JSON en un dataframe de Streamlit
        if fruityvice_response.status_code == 200:
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.warning(f"No nutritional information found for {fruit_chosen}")

    # Botón de envío de orden
    if st.button("Submit Order"):
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED)
            VALUES ('{name_on_order}', '{ingredients_string.strip()}', FALSE)
            """
        ).collect()

        st.success("✅ Your Smoothie Order has been placed!")



