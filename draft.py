import streamlit as st
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops

# 1. El Encabezado de la app
st.set_page_config(page_title="QuantWallet", page_icon="📈")
st.title("QuantWallet 🌊")
st.write("XRPL Liquidity & Risk Analysis Engine")

st.divider()  # Una línea separadora visual

# 2. La Caja de Búsqueda
target_address = st.text_input("Enter XRPL Account Address:", placeholder="r...")

# 3. El Botón de Acción
if st.button("Analyze Account"):

    if target_address:
        # st.info muestra un mensaje azul de carga
        st.info(f"Connecting to XRPL Mainnet for account: {target_address}...")


        URL_MAINNET = "https://s1.ripple.com:51234/"
        client = JsonRpcClient(URL_MAINNET)
        request = AccountInfo(account=target_address, ledger_index="validated")

        try:
            response = client.request(request)

            if response.is_successful():
                data = response.result['account_data']
                total_balance_xrp = int(data['Balance']) / 1000000

                base_reserve = 10
                object_count = data.get('OwnerCount', 0)
                total_reserve = base_reserve + (object_count * 2)

                available_balance = max(0, total_balance_xrp - total_reserve)
                liquidity_percentage = (available_balance / total_balance_xrp) * 100 if total_balance_xrp > 0 else 0



                # 4. Mostrar los Resultados de Forma Visual (Dashboard)
                st.success("Analysis Complete!")

                # Dividimos la pantalla en columnas para las métricas financieras
                col1, col2 = st.columns(2)
                col1.metric(label="Gross Total Balance", value=f"{total_balance_xrp:,.2f} XRP")
                col2.metric(label="Blocked Funds (Reserve)", value=f"{total_reserve} XRP")

                col3, col4 = st.columns(2)
                col3.metric(label="Real Available Liquidity", value=f"{available_balance:,.2f} XRP")
                col4.metric(label="Liquidity Index", value=f"{liquidity_percentage:,.1f} %")

            else:
                # st.error muestra un cuadro rojo si la cuenta no existe
                st.error("Error: Could not retrieve account data. Please check the address.")

        except Exception as e:
            st.error(f"Connection error: {e}")
    else:
        # st.warning muestra un cuadro amarillo si le dan clic sin poner una cuenta
        st.warning("Please enter an XRPL address first.")

import streamlit as st

# ... (Aquí arriba está todo tu código actual de QuantWallet) ...

st.markdown("---")  # Una línea divisoria para separar tu análisis de riesgos
st.subheader("💸 Ejecutar Transacción (Testnet)")

# Usamos un expander para mantener la interfaz limpia
with st.expander("Abrir panel de envío (Write Operation)"):
    st.write("Demostración de transacción verificable en la red.")

    # 1. Los campos de texto que el usuario debe llenar
    # Usamos type="password" para que la semilla no se vea en pantalla
    sender_secret = st.text_input("Tu Clave Secreta (Seed del remitente)", type="password")
    destination_address = st.text_input("Dirección de Destino")

    # 2. El monto a enviar (en XRP)
    amount_xrp = st.number_input("Cantidad a enviar (XRP)", min_value=0.0, value=10.0, step=1.0)

    # 3. El botón que detonará la acción
    if st.button("Enviar Transacción a la Red"):
        # Verificamos que los campos no estén vacíos antes de continuar
        if sender_secret and destination_address and amount_xrp > 0:

            # st.spinner muestra una animación de carga mientras la red responde
            with st.spinner("Procesando y validando transacción en la Testnet..."):
                try:
                    # A. Conectar a la Testnet (Red de pruebas)
                    testnet_client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

                    # B. Cargar tu billetera usando tu Clave Secreta
                    mi_billetera = Wallet.from_seed(sender_secret)

                    # C. Construir el pago. En el XRPL, 1 XRP = 1,000,000 drops.
                    # Usamos xrp_to_drops para hacer la conversión automática.
                    transaccion = Payment(
                        account=mi_billetera.classic_address,
                        amount=xrp_to_drops(amount_xrp),
                        destination=destination_address
                    )

                    # D. Firmar y enviar a la red, esperando confirmación de los validadores
                    respuesta = submit_and_wait(transaccion, testnet_client, mi_billetera)

                    # E. Mostrar el resultado en pantalla
                    if respuesta.is_successful():
                        st.success("¡Transacción verificada y exitosa! 🎉")
                        # Mostramos el Hash, que es el "recibo" oficial en la Blockchain
                        st.info(f"**Hash de la transacción:** {respuesta.result['hash']}")
                    else:
                        st.error(f"Error en la transacción: {respuesta.result['engine_result_message']}")

                except Exception as e:
                    st.error(f"Ocurrió un error interno: {e}")
        else:
            st.warning("⚠️ Por favor, llena todos los campos para continuar.")