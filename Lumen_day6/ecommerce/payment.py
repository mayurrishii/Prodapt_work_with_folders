def process_payment(amount, simulate_success=True):
    if amount <= 0:
        return {"success": False, "message": "Invalid amount"}

    if simulate_success:
        return {"success": True, "message": f"Payment of {amount} completed"}

    return {"success": False, "message": f"Payment of {amount} failed"}
