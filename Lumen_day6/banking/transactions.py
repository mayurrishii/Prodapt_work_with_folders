def deposit(accounts, account_id, amount):
    accounts[account_id]["balance"] += amount
    return accounts[account_id]["balance"]


def withdraw(accounts, account_id, amount):
    if accounts[account_id]["balance"] < amount:
        return False
    accounts[account_id]["balance"] -= amount
    return True


def transfer(accounts, from_account_id, to_account_id, amount):
    if not withdraw(accounts, from_account_id, amount):
        return False
    deposit(accounts, to_account_id, amount)
    return True
