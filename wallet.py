from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo

# 1. Connect to the XRPL Mainnet
URL_MAINNET = "https://s1.ripple.com:51234/"
client = JsonRpcClient(URL_MAINNET)
target_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"

print(f"Connecting to XRPL Mainnet...")

# 2. Send the request
request = AccountInfo(account=target_address, ledger_index="validated")
response = client.request(request)

# 3. Risk and Liquidity Analysis Engine (QuantWallet)
if response.is_successful():
    data = response.result['account_data']
    total_balance_xrp = int(data['Balance']) / 1000000

    # --- Analytical Formulas ---
    # The base reserve is 10 XRP, plus 2 XRP for each extra object (OwnerCount)
    base_reserve = 10
    object_count = data.get('OwnerCount', 0)
    total_reserve = base_reserve + (object_count * 2)

    available_balance = total_balance_xrp - total_reserve
    # Prevent negative balances on accounts emptied before network reserve changes
    available_balance = max(0, available_balance)

    liquidity_percentage = (available_balance / total_balance_xrp) * 100 if total_balance_xrp > 0 else 0

    print(f"\n--- QuantWallet Liquidity Report ---")
    print(f"Gross Total Balance: {total_balance_xrp:,.2f} XRP")
    print(f"Blocked Funds (XRPL Reserve): {total_reserve} XRP")
    print(f"Real Available Liquidity: {available_balance:,.2f} XRP")
    print(f"Liquidity Index: {liquidity_percentage:,.1f}%")
else:
    print("Error: Could not retrieve account data.")