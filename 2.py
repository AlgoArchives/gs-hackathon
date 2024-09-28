def manage_stock_inventory(stock_prices, accounts, eligible_accounts, eligible_flows, stock_balances):
    stock_prices_dict = {s: float(p) for s, p in stock_prices}
    account_dict = {a: (t, p) for a, t, p in accounts}
    eligible_accounts_dict = {s: set() for s in stock_prices_dict}
    for s, a in eligible_accounts:
        eligible_accounts_dict[s].add(a)
    
    eligible_flows_dict = {s: [] for s in stock_prices_dict}
    for s, src, dst in eligible_flows:
        eligible_flows_dict[s].append((src, dst))
    
    stock_balance_dict = {}
    for s, a, q in stock_balances:
        if s not in stock_balance_dict:
            stock_balance_dict[s] = {}
        stock_balance_dict[s][a] = int(q)
    
    movements = []

    for stock_id, balances in stock_balance_dict.items():
        demands = {a: q for a, q in balances.items() if q < 0}
        excesses = {a: q for a, q in balances.items() if q > 0}

        for demand_account, demand_quantity in demands.items():
            remaining_demand = abs(demand_quantity)
            
            for excess_account, excess_quantity in excesses.items():
                if remaining_demand <= 0:
                    break
                
                if excess_quantity > 0:
                    transfer_quantity = min(remaining_demand, excess_quantity)
                    movements.append((stock_id, excess_account, demand_account, transfer_quantity))
                    excesses[excess_account] -= transfer_quantity
                    remaining_demand -= transfer_quantity
            
            if remaining_demand > 0:
                for excess_account, excess_quantity in excesses.items():
                    if remaining_demand <= 0:
                        break
                    
                    if excess_quantity > 0:
                        transfer_quantity = min(remaining_demand, excess_quantity)
                        movements.append((stock_id, excess_account, demand_account, transfer_quantity))
                        excesses[excess_account] -= transfer_quantity
                        remaining_demand -= transfer_quantity

        for excess_account, excess_quantity in excesses.items():
            if excess_quantity > 0 and account_dict[excess_account][0] == "CUSTODY":
                triparty_account = next((a for a in eligible_accounts_dict[stock_id] if account_dict[a][0] == "TRIPARTY"), None)
                if triparty_account:
                    movements.append((stock_id, excess_account, triparty_account, excess_quantity))
                    excesses[excess_account] = 0
    
    # Sort the movements as required
    movements.sort(key=lambda x: (x[0], x[1], x[2]))

    return movements

# Example input
stock_prices = [("P1", 2.5), ("P2", 1.25)]
accounts = [("Loc1", "CUSTODY", "1"), ("Loc2", "CUSTODY", "2"), ("Loc3", "TRIPARTY", "2")]
eligible_accounts = [("P1", "Loc1"), ("P1", "Loc2"), ("P1", "Loc3"), ("P2", "Loc1"), ("P2", "Loc2"), ("P2", "Loc3")]
eligible_flows = [("P1", "Loc1", "Loc2"), ("P1", "Loc1", "Loc3"), ("P1", "Loc2", "Loc1"), ("P1", "Loc2", "Loc3"), 
                  ("P2", "Loc1", "Loc2"), ("P2", "Loc2", "Loc3"), ("P2", "Loc3", "Loc1")]
stock_balances = [("P1", "Loc1", 10), ("P1", "Loc2", -5), ("P2", "Loc1", 5)]

# Call the function
output = manage_stock_inventory(stock_prices, accounts, eligible_accounts, eligible_flows, stock_balances)

# Print the output
for row in output:
    print(",".join(map(str, row)))
