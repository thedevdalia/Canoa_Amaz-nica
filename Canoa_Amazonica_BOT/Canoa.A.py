import pandas as pd
import streamlit as st
from datetime import datetime
from fuzzywuzzy import fuzz, process
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
st.set_page_config(page_title="La Canoa Amazónica!", page_icon=":canoe:")

# Estilo para la imagen de fondo y el superpuesto oscuro
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
    </style>
    """,
    unsafe_allow_html=True
)

# Agregar el div del superpuesto en la parte superior
st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)

# URLs de las imágenes
url_chica_comida = "https://github.com/thedevdalia/Canoa_Amaz-nica/raw/main/Canoa_Amazonica_BOT/La%20Canoaa.jpg"

# Mostrar imágenes en la barra lateral
st.sidebar.image(url_chica_comida, caption="Deliciosos Manjares de la Selva", use_column_width=True)

# Menú lateral
menu = ["La Canoa Amazónica", "Ofertas", "Pedidos", "Reclamos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "La Canoa Amazónica":
    # Mensaje de bienvenida
    welcome_message = """¡Bienvenidos a La Canoa Amazónica! 🌿🍃  
    Si eres amante de la comida exótica de nuestra querida selva, aquí te ofrecemos una experiencia única.  
    Disfrutarás de sabores auténticos que te harán sentir como si estuvieras en lo profundo de la selva amazónica.  
    Además de nuestro servicio de delivery, te invitamos a visitarnos en cualquiera de nuestras cuatro sedes, donde recibirás una atención inolvidable.  
    Nos encontramos en San Martín, San Isidro, y Chorrillos.  
    Recuerda: tú eres parte de la selva, y la selva es parte de ti. ¡Ven a disfrutar la comida con el verdadero sabor de la Amazonía!"""
    st.markdown(welcome_message)

elif choice == "Ofertas":
    # Mensaje de ofertas
    offers_message = """¡Promo familiar! 3 juanes a 70 soles, más una botella de 2 litros de chicha morada.  
    ¡Tacacho con cecina 2 por 30 soles! ¡Super promo!"""
    st.markdown(offers_message)

elif choice == "Pedidos":
    
   
# Mostrar mensaje de bienvenida
    intro = 
  
"""
    <h2 style='color: white;'>¡Bienvenido a La Canoa Amazónica! 🌿🍃</h2>  
    <p style='color: white;'>Llegaste al rincón del sabor, donde la selva te recibe con sus platos más deliciosos.</p>  
    <p style='color: white;'>¿Qué se te antoja hoy? ¡Escribe "Carta" para comenzar!</p>
    """
    st.markdown(intro, unsafe_allow_html=
    st.markdown(intro, unsafe_allow_htm

    st.markdown(intro, unsa

    st.m
True)

    # Función para cargar los distritos de reparto desde otro CSV
    def load_districts(csv_file):
        try:
            return pd.read_csv(csv_file)
        except FileNotFoundError:
            st.error("Archivo de distritos no encontrado.")
            return pd.DataFrame(columns=["Distrito"])

    # Función para verificar el distrito con similitud
    def verify_district(prompt, districts):
        district_list = districts['Distrito'].tolist()
        best_match, similarity = process.extractOne(prompt, district_list)
        return best_match if similarity > 65 else None

    # Función para guardar el pedido en un archivo CSV
    def save_order_to_csv(order_dict, district, filename="orders.csv"):
        try:
            orders_list = [
                {'Fecha y Hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 'Distrito': district, 'Plato': dish, 'Cantidad': quantity}
                for dish, quantity in order_dict.items()
            ]
            df_orders = pd.DataFrame(orders_list)
            df_orders.to_csv(filename, mode='a', header=False, index=False)
        except Exception as e:
            st.error(f"Error al guardar el pedido: {e}")

    # Función para extraer el pedido y la cantidad usando similitud
    def improved_extract_order_and_quantity(prompt, menu):
        if not prompt:
            return {}

        pattern = r"(\d+|uno|dos|tres|cuatro|cinco)?\s*([^\d,]+)"
        orders = re.findall(pattern, prompt.lower())

        order_dict = {}
        menu_items = menu['Plato'].tolist()

        num_text_to_int = {
            'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5
        }

        for quantity, dish in orders:
            dish_cleaned = dish.strip()
            best_match, similarity = process.extractOne(dish_cleaned, menu_items, scorer=fuzz.token_set_ratio)

            if similarity > 65:
                if not quantity:
                    quantity = 1
                elif quantity.isdigit():
                    quantity = int(quantity)
                else:
                    quantity = num_text_to_int.get(quantity, 1)

                if best_match in order_dict:
                    order_dict[best_match] += quantity
                else:
                    order_dict[best_match] = quantity

        return order_dict

    # Función para verificar los pedidos contra el menú disponible
    def verify_order_with_menu(order_dict, menu):
        available_orders = {}
        unavailable_orders = []

        for dish, quantity in order_dict.items():
            if dish in menu['Plato'].values:
                available_orders[dish] = quantity
            else:
                unavailable_orders.append(dish)

        return available_orders, unavailable_orders

    # Función para mostrar el menú en un formato amigable
    def format_menu(menu):
        if menu.empty:
            return "No hay platos disponibles."
        formatted_menu = [f"**{row['Plato']}**  \n{row['Descripción']}  \n**Precio:** S/{row['Precio']}" for idx, row in menu.iterrows()]
        return "\n\n".join(formatted_menu)

    # Cargar el menú y los distritos
    menu = load_menu("carta_amazonica.csv")
    districts = load_districts("distritos.csv")

    # Botón para limpiar la conversación
    if st.button("Limpiar Conversación", key="clear"):
        init_session_state()

    # Mostrar el historial de la conversación
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🍃" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Entrada del usuario
    user_input = st.chat_input("Escribe aquí...")

    # Procesar la conversación
    if not st.session_state["order_placed"]:
        if user_input:
            order_dict = improved_extract_order_and_quantity(user_input, menu)
            if not order_dict:
                response = "😊 ¡Selecciona un plato de la selva! Escribe la cantidad seguida del plato.\n\n"
                response += format_menu(menu)
            else:
                available_orders, unavailable_orders = verify_order_with_menu(order_dict, menu)
                if unavailable_orders:
                    response = f"Lo siento, los siguientes platos no están disponibles: {', '.join(unavailable_orders)}."
                else:
                    st.session_state["order_placed"] = True
                    st.session_state["current_order"] = available_orders
                    response = f"<p style='color: white;'>Tu pedido ha sido registrado: {', '.join([f'{qty} x {dish}' for dish, qty in available_orders.items()])}. ¿De qué distrito nos visitas? Por favor, menciona tu distrito (por ejemplo: Miraflores).</p>"
    else:
        if user_input:
            district = verify_district(user_input, districts)
            if not district:
                response = f"Lo siento, pero no entregamos en ese distrito. Distritos disponibles: {', '.join(districts['Distrito'].tolist())}."
            else:
                st.session_state["district_selected"] = True
                st.session_state["current_district"] = district
                save_order_to_csv(st.session_state["current_order"], district)
                response = f"Gracias por tu pedido desde **{district}**. ¡Tu pedido ha sido registrado con éxito! 🍽️"

    # Mostrar la respuesta del asistente
    if user_input:
        with st.chat_message("assistant", avatar="🍃"):
            response_html = f"<p style='color: white;'>{response}</p>"
            st.markdown(response_html, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})

elif choice == "Reclamos":
    # Manejo de reclamos
    st.markdown("<h1 style='color: white;'>Deja tu Reclamo</h1>", unsafe_allow_html=True)
    complaint = st.text_area("Escribe tu reclamo aquí...")
    
    if st.button("Enviar Reclamo"):
        if complaint:
            response = "Tu reclamo está en proceso. Te devolveremos tu dinero en una hora al verificar la información. Si tu pedido no llegó a tiempo o fue diferente a lo que pediste, también te ofreceremos cupones por la mala experiencia de tu pedido."
            st.success(response)
            response_html = f"<p style='color: white;'>{response}</p>"
            st.markdown(response_html, unsafe_allow_html=True)
        else:
            st.error("Por favor, escribe tu reclamo antes de enviarlo.")

# Agregar mensaje de despedida en la parte inferior
st.markdown("---")
st.markdown("¡Gracias por visitar La Canoa Amazónica! 🌿🍽️")
