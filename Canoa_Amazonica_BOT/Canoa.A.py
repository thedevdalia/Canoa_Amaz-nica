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
        background-image: url('https://raw.githubusercontent.com/thedevdalia/Canoa_Amaz-nica/main/Canoa_Amazonica_BOT/image.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;  /* Cambiar el color del texto si es necesario */
    }
    .overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5); /* Color negro con opacidad del 50% */
        z-index: 1; /* Asegura que el superpuesto esté por encima de la imagen de fondo */
    }
    .falling-coconut {
        position: absolute;
        top: -300px;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        animation: fall 10s ease-out forwards;
        z-index: 100;
        cursor: pointer;
    }
    @keyframes fall {
        0% { top: -300px; }
        100% { top: 50%; }
    }
    #main-content { display: none; }
    </style>
    <script>
    function showPage() {
        document.getElementById('coconut').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
    }
    </script>
    """,
    unsafe_allow_html=True
)

# URL del coco
url_coconut = "https://github.com/thedevdalia/Canoa_Amaz-nica/blob/main/Canoa_Amazonica_BOT/static/coconut-isolated-transparent-background_530816-1449.jpg?raw=true"

# Mostrar el coco animado
st.markdown(f"<img src='{url_coconut}' class='falling-coconut' id='coconut' onclick='showPage()'>", unsafe_allow_html=True)

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

# URLs de las imágenes
url_chica_comida = "https://github.com/thedevdalia/Canoa_Amaz-nica/raw/main/Canoa_Amazonica_BOT/La%20Canoaa.jpg"

# Mostrar imágenes en la barra lateral
st.sidebar.image(url_chica_comida, caption="Deliciosos Manjares de la Selva", use_column_width=True)

# Menú lateral
menu = ["La Canoa Amazónica", "Ofertas", "Pedidos", "Reclamos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "La Canoa Amazónica":
    st.markdown("""
    <h2 style='color: white;'>¡Bienvenidos a La Canoa Amazónica! 🌿🍃</h4>
    <p style='color: white;'>Si eres amante de la comida exótica y auténtica de nuestra querida selva, aquí te ofrecemos una experiencia gastronómica única que no querrás perderte. 
    Desde suculentas carnes, como el pez amazónico, hasta opciones vegetarianas, tenemos algo para todos los gustos.</p>
    """, unsafe_allow_html=True)

elif choice == "Ofertas":
    st.markdown("¡Promo familiar! 3 juanes a 70 soles, más una botella de 2 litros de chicha morada.")

elif choice == "Pedidos":
    st.markdown("<h2 style='color: white;'>¡Descubre los Sabores de la Selva en La Canoa Amazónica! 🌿🍃</h2>", unsafe_allow_html=True)

    # Funciones para cargar el menú y procesar pedidos
    def load_menu(csv_file):
        try:
            return pd.read_csv(csv_file, delimiter=';')
        except FileNotFoundError:
            st.error("Archivo de menú no encontrado.")
            return pd.DataFrame(columns=["Plato", "Descripción", "Precio"])

    def load_districts(csv_file):
        try:
            return pd.read_csv(csv_file)
        except FileNotFoundError:
            st.error("Archivo de distritos no encontrado.")
            return pd.DataFrame(columns=["Distrito"])

    def verify_district(prompt, districts):
        district_list = districts['Distrito'].tolist()
        best_match, similarity = process.extractOne(prompt, district_list)
        return best_match if similarity > 65 else None

    def save_order_to_csv(order_dict, district, filename="orders.csv"):
        orders_list = [{'Fecha y Hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Distrito': district, 'Plato': dish, 'Cantidad': quantity} for dish, quantity in order_dict.items()]
        pd.DataFrame(orders_list).to_csv(filename, mode='a', header=False, index=False)

    def improved_extract_order_and_quantity(prompt, menu):
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

    # Cargar menú y distritos
    menu = load_menu("carta_amazonica.csv")
    districts = load_districts("distritos.csv")

    # Procesar entradas del usuario
    user_input = st.chat_input("Escribe aquí...")

    if user_input and not st.session_state["order_placed"]:
        order_dict = improved_extract_order_and_quantity(user_input, menu)
        available_orders, unavailable_orders = verify_order_with_menu(order_dict, menu)
        if unavailable_orders:
            response = f"Platos no disponibles: {', '.join(unavailable_orders)}."
        else:
            st.session_state["order_placed"] = True
            st.session_state["current_order"] = available_orders
            response = f"Tu pedido: {', '.join([f'{qty} x {dish}' for dish, qty in available_orders.items()])}. ¿De qué distrito nos visitas?"

    elif user_input and st.session_state["order_placed"]:
        district = verify_district(user_input, districts)
        if district:
            st.session_state["district_selected"] = True
            st.session_state["current_district"] = district
            save_order_to_csv(st.session_state["current_order"], district)
            response = f"Pedido registrado desde **{district}**."
        else:
            response = f"Distrito no válido. Distritos disponibles: {', '.join(districts['Distrito'].tolist())}."

    # Mostrar respuesta
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
