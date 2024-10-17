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

# Estilo para la imagen de fondo general y el superpuesto oscuro
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://raw.githubusercontent.com/thedevdalia/Canoa_Amaz-nica/main/Canoa_Amazonica_BOT/image.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }
    
    .overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5); /* Color negro con opacidad del 50% */
        z-index: 1;
    }
    </style>
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
    # CSS para la imagen de fondo personalizada solo para el mensaje de bienvenida
    st.markdown(
        """
        <style>
        .welcome-section {
            background-image: url('https://github.com/thedevdalia/Canoa_Amaz-nica/blob/main/Canoa_Amazonica_BOT/Amazonica.JPG');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Mensaje de bienvenida con la imagen de fondo personalizada
    welcome_message = """
    <div class='welcome-section'>
    <h2>¡Bienvenidos a La Canoa Amazónica! 🌿🍃</h2>   
    <p>Si eres amante de la comida exótica y auténtica de nuestra querida selva, aquí te ofrecemos una experiencia gastronómica única que no querrás perderte.
    En La Canoa Amazónica, vendemos una variedad de deliciosos platos de la selva, elaborados con ingredientes frescos y autóctonos que capturan la esencia de la Amazonía. Cada bocado es un viaje sensorial que te transporta a lo más profundo de la selva, donde los sabores vibrantes y las especias exóticas se fusionan para crear una explosión de gusto en tu paladar. Desde suculentas carnes, como el pez amazónico, hasta opciones vegetarianas llenas de nutrientes, tenemos algo para todos los gustos.</p>
    <p>Nuestro compromiso va más allá de ofrecer comida deliciosa; también te invitamos a disfrutar de un ambiente acogedor y familiar en cualquiera de nuestras cuatro sedes en San Martín, San Isidro y Chorrillos.</p>
    <p>Recuerda: ¡tú eres parte de la selva, y la selva es parte de ti! Ven a disfrutar de la comida con el verdadero sabor de la Amazonía. ¡Te esperamos con los brazos abiertos en La Canoa Amazónica! 🌿🍽️</p>
    </div>
    """

    # Mostrar el mensaje de bienvenida con fondo personalizado
    st.markdown(welcome_message, unsafe_allow_html=True)

elif choice == "Ofertas":
    # Mensaje de ofertas
    offers_message = """<h2 style='color: white;'>Ofertas Especiales</h2>
    <p style='color: white;'>¡Promo familiar! 3 juanes a 70 soles, más una botella de 2 litros de chicha morada.<br>
    ¡Tacacho con cecina 2 por 30 soles! ¡Super promo!</p>
    """
    st.markdown(offers_message, unsafe_allow_html=True)

elif choice == "Pedidos":
    # Mostrar mensaje de bienvenida en la sección de pedidos
    intro = """
    <h2 style='color: white;'>¡Descubre los Sabores de la Selva en La Canoa Amazónica! 🌿🍃</h2>  
    <p style='color: white;'>Llegaste al rincón del sabor, donde la selva te recibe con sus platos más deliciosos.</p>  
    <p style='color: white;'>¿Qué se te antoja hoy? ¡Escribe "Carta" para comenzar!</p>
    """
    st.markdown(intro, unsafe_allow_html=True)

    # Función para cargar el menú desde un archivo CSV
    def load_menu(csv_file):
        try:
            return pd.read_csv(csv_file, delimiter=';')
        except FileNotFoundError:
            st.error("Archivo de menú no encontrado.")
            return pd.DataFrame(columns=["Plato", "Descripción", "Precio"])

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
        with st.chat_message(message["role"],
                   avatar="https://github.com/thedevdalia/Canoa_Amaz-nica/raw/main/Canoa_Amazonica_BOT/canoa_logo.jpg"):
            st.markdown(message["content"])

    # Caja de entrada de texto para el usuario
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Respuesta inicial basada en el mensaje del usuario
        response = ""

        if re.search(r"\b(carta|menu|platos)\b", prompt, re.IGNORECASE):
            # Mostrar el menú al usuario
            response = f"**Este es nuestro menú actual:**  \n{format_menu(menu)}"

        elif re.search(r"\bpedir\b", prompt, re.IGNORECASE):
            # Extraer los pedidos del mensaje
            order_dict = improved_extract_order_and_quantity(prompt, menu)

            if order_dict:
                available_orders, unavailable_orders = verify_order_with_menu(order_dict, menu)

                if available_orders:
                    response += "Se ha procesado tu pedido: \n"
                    for dish, quantity in available_orders.items():
                        response += f"- {quantity}x {dish} \n"
                    st.session_state["order_placed"] = True

                if unavailable_orders:
                    response += "\nNo encontramos los siguientes platos en nuestro menú: "
                    response += ", ".join(unavailable_orders)
            else:
                response = "No entendí tu pedido. Por favor, indica claramente los platos y la cantidad."

        elif st.session_state["order_placed"] and re.search(r"\bdistrito\b", prompt, re.IGNORECASE):
            # Verificar distrito
            district = verify_district(prompt, districts)
            if district:
                st.session_state["current_district"] = district
                st.session_state["district_selected"] = True
                response = f"Perfecto, hacemos entregas en {district}. ¡Gracias por tu pedido!"

                # Guardar el pedido
                save_order_to_csv(st.session_state.messages[-1], district)

            else:
                response = "Lo siento, no realizamos entregas en ese distrito."

        else:
            response = "No entendí tu mensaje. Por favor, pide la carta o realiza tu pedido mencionando el plato y la cantidad."

        # Mostrar la respuesta generada
        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant", avatar="https://github.com/thedevdalia/Canoa_Amaz-nica/raw/main/Canoa_Amazonica_BOT/canoa_logo.jpg"):
            st.markdown(response)

elif choice == "Reclamos":
    st.header("Reclamos")
    st.write("Si tienes algún inconveniente o deseas hacer un reclamo, escríbenos aquí.")
    complaint = st.text_area("Escribe tu reclamo:")

    if st.button("Enviar Reclamo"):
        if complaint:
            st.success("Gracias por tu reclamo. Nos pondremos en contacto contigo.")
        else:
            st.error("Por favor, escribe un reclamo antes de enviar.")

