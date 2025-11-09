# services/payment_service.py
class PaymentGateway:
    def process_payment(self, patron_id, amount):
        if not str(patron_id).isdigit():
            raise ValueError("Invalid patron ID")
        if amount is None or amount <= 0:
            raise ValueError("Invalid amount")
        return {"status": "success", "transaction_id": "TX12345"}

    def refund_payment(self, transaction_id, amount):
        
        if not transaction_id or not transaction_id.startswith("TX"):
            raise ValueError("Invalid transaction ID")
        if amount is None or amount <= 0 or amount > 15:
            raise ValueError("Invalid refund amount")
        return {"status": "refund_success"}
