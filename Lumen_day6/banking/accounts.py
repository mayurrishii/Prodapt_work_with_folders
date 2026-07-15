def create_account(accounts, account_id, owner, opening_balance=0):
    accounts[account_id] = {"owner": owner, "balance": opening_balance}


def get_balance(accounts, account_id):
    return accounts[account_id]["balance"]
