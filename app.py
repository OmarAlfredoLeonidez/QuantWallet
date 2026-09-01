import streamlit as st
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops


# 1. General Application Configuration

st.set_page_config(page_title="QuantWallet", page_icon="📈", layout="centered")

# Network server constants
URL_MAINNET = "https://s1.ripple.com:51234/"
URL_TESTNET = "https://s.altnet.rippletest.net:51234/"


# 2. App Header

st.title("QuantWallet 🌊")
st.markdown("**XRPL Liquidity & Risk Analysis Engine**")
st.divider()


# 3. Module 1: Risk Analysis (Mainnet)

st.subheader("📊 Account Analysis (Mainnet)")
target_address = st.text_input("Enter XRPL Account Address:", placeholder="r...")

if st.button("Analyze Account"):
    if target_address:
        # st.spinner shows a loading animation while processing
        with st.spinner(f"Connecting to XRPL Mainnet for account: {target_address}..."):
            client = JsonRpcClient(URL_MAINNET)
            request = AccountInfo(account=target_address, ledger_index="validated")

            try:
                response = client.request(request)

                if response.is_successful():
                    data = response.result['account_data']
                    total_balance_xrp = int(data['Balance']) / 1_000_000

                    # Reserve margin calculation
                    base_reserve = 10
                    object_count = data.get('OwnerCount', 0)
                    total_reserve = base_reserve + (object_count * 2)

                    # Real liquidity calculation
                    available_balance = max(0, total_balance_xrp - total_reserve)
                    liquidity_percentage = (available_balance / total_balance_xrp) * 100 if total_balance_xrp > 0 else 0

                    # Display Visual Results
                    st.success("Analysis Complete!")

                    col1, col2 = st.columns(2)
                    col1.metric(label="Gross Total Balance", value=f"{total_balance_xrp:,.2f} XRP")
                    col2.metric(label="Blocked Funds (Reserve)", value=f"{total_reserve} XRP")

                    col3, col4 = st.columns(2)
                    col3.metric(label="Real Available Liquidity", value=f"{available_balance:,.2f} XRP")
                    col4.metric(label="Liquidity Index", value=f"{liquidity_percentage:,.1f} %")

                else:
                    st.error("Error: Could not retrieve account data. Please check the address.")

            except Exception as e:
                st.error(f"Connection error: {e}")
    else:
        st.warning("Please enter an XRPL address first.")

st.markdown("---")


# 4. Module 2: Execute Transaction (Testnet)

st.subheader("💸 Execute Transaction (Testnet)")

# Expander menu to keep the interface clean
with st.expander("Open Send Panel (Write Operation)"):
    st.write("Demonstration of a verifiable transaction on the network.")

    # Group inputs into columns for better space utilization
    col_secret, col_dest = st.columns(2)
    with col_secret:
        sender_secret = st.text_input("Your Secret Key (Seed)", type="password")
    with col_dest:
        destination_address = st.text_input("Destination Address")

    amount_xrp = st.number_input("Amount to send (XRP)", min_value=0.0, value=10.0, step=1.0)

    if st.button("Submit Transaction to Network"):
        if sender_secret and destination_address and amount_xrp > 0:

            with st.spinner("Processing and validating transaction on the Testnet..."):
                try:
                    testnet_client = JsonRpcClient(URL_TESTNET)
                    mi_billetera = Wallet.from_seed(sender_secret)

                    transaccion = Payment(
                        account=mi_billetera.classic_address,
                        amount=xrp_to_drops(amount_xrp),
                        destination=destination_address,
                        source_tag=2606270001  # <--- Agrega esta línea exacta
                    )

                    respuesta = submit_and_wait(transaccion, testnet_client, mi_billetera)

                    if respuesta.is_successful():
                        st.success("Transaction verified and successful! 🎉")
                        st.info(f"**Transaction Hash:** {respuesta.result['hash']}")
                    else:
                        st.error(f"Transaction error: {respuesta.result['engine_result_message']}")

                except Exception as e:
                    st.error(f"An internal error occurred: {e}")
        else:
            st.warning("⚠️ Please fill in all fields to continue.")