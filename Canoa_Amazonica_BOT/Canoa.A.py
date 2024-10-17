import streamlit as st
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz, process
import time
import re

# Inicializar las claves de session_state si no existen
def init_session_state():
    session_defaults = {
        "order_placed": False,
        "district_selected": False,
        "current_district": None,
        "current_order": {},
        "messages": []
    }
    for key, default in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

init_session_state()

# Configuración inicial de la página
st.set_page_config(page_title="La Canoa Amazónica!", page_icon=":canoe:", layout="wide")

# Estilo para animación y fondo
st.markdown(
    """
    <style>
    .stApp {
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }
    .falling-elements {
        position: relative;
        z-index: 100;
        animation: fall 3s ease-out forwards;
        cursor: pointer;
    }
    .falling-elements img {
        position: absolute;
        top: -500px;
        left: 50%;
        transform: translateX(-50%);
    }
    .falling-elements img:first-child {
        width: 100%;
        height: 100%;
    }
    .falling-elements img:last-child {
        width: 200px;
    }
    @keyframes fall {
        0% { top: -500px; }
        100% { top: 0; }
    }
    #main-content { display: none; }
    .hidden { display: none; }
    </style>
    <script>
    function showPage() {
        document.getElementById('falling-elements').classList.add('hidden');
        document.getElementById('main-content').style.display = 'block';
    }
    </script>
    """,
    unsafe_allow_html=True
)

# URLs de las imágenes
url_background = "https://github.com/thedevdalia/Canoa_Amaz-nica/blob/main/Canoa_Amazonica_BOT/static/Fondoooooooooooooooooooo.jpg?raw=true"
url_coconut = "https://github.com/thedevdalia/Canoa_Amaz-nica/blob/main/Canoa_Amazonica_BOT/static/coconut-isolated-transparent-background_530816-1449.jpg?raw=true"

# Mostrar el fondo y el coco animados
st.markdown(f"""
    <div class='falling-elements' id='falling-elements' onclick='showPage()'>
        <img src='{url_background}' alt='Fondo de la selva'>
        <img src='{url_coconut}' alt='Coco'>
    </div>
""", unsafe_allow_html=True)

# Simulación de espera antes de mostrar la página
time.sleep(2)

# Mostrar el contenido principal después del clic en el coco
st.markdown(
    """
    <div id="main-content">
        <h1 style="color: white; text-align: center;">¡Bienvenido a La Canoa Amazónica!</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# URL de la imagen
url_chica_comida = "https://github.com/thedevdalia/Canoa_Amaz-nica/raw/main/Canoa_Amazonica_BOT/La%20Canoaa.jpg"

# Mostrar imagen en la barra lateral
st.sidebar.image(url_chica_comida, caption="Deliciosos Manjares de la Selva", use_column_width=True)

# Menú lateral
menu = ["La Canoa Amazónica", "Ofertas", "Pedidos", "Reclamos"]
choice = st.sidebar.selectbox("Menú", menu)

# Funciones para cargar datos y procesar pedidos
def load_data(csv_file, delimiter=';'):
    try:
        return pd.read_csv(csv_file, delimiter=delimiter)
    except FileNotFoundError:
        st.error(f"Archivo {csv_file} no encontrado.")
        return pd.DataFrame()

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

def verify_order_with_menu(order_dict, menu):
    available_orders = {dish: quantity for dish, quantity in order_dict.items() if dish in menu['Plato'].values}
    unavailable_orders = [dish for dish in order_dict if dish not in menu['Plato'].values]
    return available_orders, unavailable_orders

def save_order_to_csv(order_dict, district, filename="orders.csv"):
    orders_list = [{'Fecha y Hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Distrito': district, 'Plato': dish, 'Cantidad': quantity} for dish, quantity in order_dict.items()]
    pd.DataFrame(orders_list).to_csv(filename, mode='a', header=False, index=False)

def verify_district(prompt, districts):
    district_list = districts['Distrito'].tolist()
    best_match, similarity = process.extractOne(prompt, district_list)
    return best_match if similarity > 65 else None

# Cargar menú y distritos
menu_data = load_data("carta_amazonica.csv")
districts_data = load_data("distritos.csv", delimiter=',')

# Lógica del menú seleccionado
if choice == "La Canoa Amazónica":
    st.markdown("""
    <h2 style='color: white;'>¡Bienvenidos a La Canoa Amazónica! 🌿🍃</h2>
    <p style='color: white;'>Disfruta de los exquisitos sabores de la selva amazónica con nuestros platos especiales.</p>
    """, unsafe_allow_html=True)

elif choice == "Ofertas":
    st.markdown("**¡Promo familiar!** 3 juanes a 70 soles, más una botella de 2 litros de chicha morada.")

elif choice == "Pedidos":
    st.markdown("<h2 style='color: white;'>¡Haz tu pedido!</h2>", unsafe_allow_html=True)

    user_input = st.chat_input("Escribe tu pedido aquí...")

    if user_input and not st.session_state["order_placed"]:
        order_dict = extract_order_and_quantity(user_input, menu_data)
        available_orders, unavailable_orders = verify_order_with_menu(order_dict, menu_data)
        
        if unavailable_orders:
            response = f"Platos no disponibles: {', '.join(unavailable_orders)}."
        else:
            st.session_state["order_placed"] = True
            st.session_state["current_order"] = available_orders
            response = f"Tu pedido: {', '.join([f'{qty} x {dish}' for dish, qty in available_orders.items()])}. ¿De qué distrito nos visitas?"

    elif user_input and st.session_state["order_placed"]:
        district = verify_district(user_input, districts_data)
        if district:
            st.session_state["district_selected"] = True
            st.session_state["current_district"] = district
            save_order_to_csv(st.session_state["current_order"], district)
            response = f"Pedido registrado desde **{district}**."
        else:
            response = f"Distrito no válido. Distritos disponibles: {', '.join(districts_data['Distrito'].tolist())}."

    if user_input:
        st.markdown(f"<p style='color: white;'>{response}</p>", unsafe_allow_html=True)

elif choice == "Reclamos":
    complaint = st.text_area("Escribe tu reclamo aquí...")
    if st.button("Enviar Reclamo"):
        if complaint:
            st.success("Tu reclamo está en proceso.")
        else:
            st.error("Por favor, escribe tu reclamo antes de enviarlo.")

# Footer
st.markdown("---")
st.markdown("¡Gracias por visitar La Canoa Amazónica! 🌿🍽️")
