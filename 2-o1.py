# Read number of stocks
n_stocks = int(input())
stocks = {}
for _ in range(n_stocks):
    stock_id, price = input().strip().split(',')
    stocks[stock_id] = float(price)

# Read accounts
n_accounts = int(input())
accounts = {}
for _ in range(n_accounts):
    account_id, account_type, parent_account = input().strip().split(',')
    accounts[account_id] = {
        'type': account_type,
        'parent': parent_account
    }

# Read eligible accounts per stock
n_eligible_accounts = int(input())
eligible_accounts = {}
for _ in range(n_eligible_accounts):
    stock_id, account_id = input().strip().split(',')
    eligible_accounts.setdefault(stock_id, set()).add(account_id)

# Read eligible flows per stock
n_eligible_flows = int(input())
eligible_flows = {}
for _ in range(n_eligible_flows):
    stock_id, source_id, dest_id = input().strip().split(',')
    eligible_flows.setdefault(stock_id, set()).add((source_id, dest_id))

# Read balances
n_balances = int(input())
balances = {}
for _ in range(n_balances):
    stock_id, account_id, quantity = input().strip().split(',')
    quantity = int(quantity)
    balances.setdefault(stock_id, {}).setdefault(account_id, 0)
    balances[stock_id][account_id] += quantity

# Prepare movements
movements = []

for stock_id in sorted(stocks.keys()):
    stock_balances = balances.get(stock_id, {})
    sources = {acc_id: qty for acc_id, qty in stock_balances.items() if qty > 0}
    demands = {acc_id: -qty for acc_id, qty in stock_balances.items() if qty < 0}

    # Satisfy demands
    for demand_acc, demand_qty in demands.items():
        remaining_demand = demand_qty
        # Prefer sources within the same parent account
        preferred_sources = sorted(sources.items(), key=lambda x: (accounts[x[0]]['parent'] != accounts[demand_acc]['parent'], -x[1]))
        for source_acc, source_qty in preferred_sources:
            if remaining_demand <= 0:
                break
            if (source_acc, demand_acc) not in eligible_flows.get(stock_id, set()):
                continue
            transfer_qty = min(remaining_demand, source_qty)
            movements.append((stock_id, source_acc, demand_acc, transfer_qty))
            sources[source_acc] -= transfer_qty
            remaining_demand -= transfer_qty
        if remaining_demand > 0:
            # Could not satisfy demand
            pass

    # Update sources after satisfying demands
    sources = {acc_id: qty for acc_id, qty in sources.items() if qty > 0}

    # Handle excess stocks
    for source_acc, source_qty in sources.items():
        if source_qty <= 0:
            continue
        # Find triparty accounts
        triparty_accounts = [acc_id for acc_id in eligible_accounts.get(stock_id, []) if accounts[acc_id]['type'] == 'TRIPARTY']
        if not triparty_accounts:
            continue
        # Prefer triparty accounts within the same parent
        triparty_accounts.sort(key=lambda acc_id: accounts[acc_id]['parent'] != accounts[source_acc]['parent'])
        for triparty_acc in triparty_accounts:
            if source_qty <= 0:
                break
            if (source_acc, triparty_acc) not in eligible_flows.get(stock_id, set()):
                continue
            transfer_qty = source_qty
            movements.append((stock_id, source_acc, triparty_acc, transfer_qty))
            source_qty -= transfer_qty
            sources[source_acc] = source_qty

# Sort and print the movements
movements.sort(key=lambda x: (x[0], x[1], x[2]))
for move in movements:
    print(f"{move[0]},{move[1]},{move[2]},{move[3]}")
