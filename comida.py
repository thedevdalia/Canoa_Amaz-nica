import streamlit as st
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz, process
import re

# Inicializar las claves de session_state si no existen
def init_session_state():
    if 'order_placed' not in st.session_state:
        st.session_state['order_placed'] = False
        st.session_state['district_selected'] = False
        st.session_state['current_district'] = None
        st.session_state['current_order'] = {}

init_session_state()

# Configuración de la página
st.set_page_config(page_title="Delicias de la Sierra!", page_icon=":mountain:", layout="wide")

# Función para cargar datos desde un archivo CSV
def load_data(csv_file, delimiter=';'):
    try:
        return pd.read_csv(csv_file, delimiter=delimiter)
    except FileNotFoundError:
        st.error(f"Archivo {csv_file} no encontrado.")
        return pd.DataFrame()

# Función para extraer el pedido y la cantidad
def extract_order_and_quantity(prompt, menu):
    pattern = r"(\d+|uno|dos|tres|cuatro|cinco)?\s*([^\d,]+)"
    orders = re.findall(pattern, prompt.lower())
    order_dict = {}
    menu_items = menu['Plato'].tolist()
    num_text_to_int = {'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5}

    for quantity, dish in orders:
        best_match, similarity = process.extractOne(dish.strip(), menu_items, scorer=fuzz.token_set_ratio)
        if similarity > 65:
            quantity = int(quantity) if quantity.isdigit() else num_text_to_int.get(quantity, 1)
            order_dict[best_match] = order_dict.get(best_match, 0) + quantity
    return order_dict

# Función para verificar el distrito
def verify_district(prompt, districts):
    district_list = districts['Distrito'].tolist()
    best_match, similarity = process.extractOne(prompt, district_list)
    return best_match if similarity > 65 else None

# Cargar el menú y los distritos
menu_data = load_data("menu_sierra.csv")  # Archivo con los platos
districts_data = load_data("distritos.csv", delimiter=',')  # Archivo con los distritos

# Interfaz de usuario para seleccionar pedidos
if not st.session_state['order_placed']:
    st.markdown("### ¡Haz tu pedido!")
    user_input = st.text_input("Escribe tu pedido (ej. 2 pachamancas, 1 cuy chactado)")

    if user_input:
        order_dict = extract_order_and_quantity(user_input, menu_data)
        if order_dict:
            st.session_state['current_order'] = order_dict
            st.session_state['order_placed'] = True
            st.markdown(f"Tu pedido: {', '.join([f'{qty} x {dish}' for dish, qty in order_dict.items()])}. ¿De qué distrito nos visitas?")
        else:
            st.markdown("No se encontraron platos válidos en el pedido.")

# Selección de distrito
if st.session_state['order_placed'] and not st.session_state['district_selected']:
    district_input = st.text_input("Escribe tu distrito:")
    if district_input:
        district = verify_district(district_input, districts_data)
        if district:
            st.session_state['current_district'] = district
            st.session_state['district_selected'] = True
            st.markdown(f"¡Pedido registrado desde {district}!")
        else:
            st.markdown("Distrito no válido. Intenta nuevamente.")

# Confirmar pedido
if st.session_state['district_selected']:
    st.success("¡Tu pedido ha sido registrado correctamente!")
