import requests


class SbpServiceException(Exception):
    pass


class SbpService:
    authorization_headers = {
        "Authorization": "Basic NjIzYzIxMzcwZGYxNDU2M2I4M2QxNTIxNWQwNzZmNTI6Y2ZmZTA2ZTgwNjc0NGEzZjkwZDU4ZDUwZmM0YWRkODY="}

    @staticmethod
    def create_payment(transaction_id: str, amount: int, terminal_id: str):
        payload = {
            "order": {
                "amount": amount,
                "id": transaction_id
            },
            "settings": {
                "terminal_id": terminal_id
            }
        }

        response = requests.post('https://api.invoice.su/api/v2/CreatePayment', json=payload,
                                 headers=SbpService.authorization_headers)

        data = response.json()

        if "error" in data:
            raise SbpServiceException(data["description"])

        return data

    @staticmethod
    def get_payment_status(payment_id: str):
        payload = {'id': payment_id}

        response = requests.post('https://api.invoice.su/api/v2/GetPayment', json=payload,
                                 headers=SbpService.authorization_headers)
        data = response.json()

        if "error" in data:
            raise SbpServiceException(data["description"])

        return data

    @staticmethod
    def cancel_payment(payment_id: str):
        payload = {'id': payment_id}

        response = requests.post('https://api.invoice.su/api/v2/ClosePayment', json=payload,
                                 headers=SbpService.authorization_headers)
        data = response.json()

        if "error" in data:
            raise SbpServiceException(data["description"])

        return data

    @staticmethod
    def make_refund(payment_id: str, amount: int):
        transaction = SbpService.get_payment_status(payment_id)
        is_success = transaction['status'] == 'successful'

        url = 'https://api.invoice.su/api/v2/CreateRefund' \
            if is_success \
            else 'https://api.invoice.su/api/v2/ClosePayment'

        payload = {
            'id': payment_id,
        }
        if is_success:
            payload['refund'] = {'amount': amount}

        response = requests.post(url, json=payload,
                                 headers=SbpService.authorization_headers)
        data = response.json()
       
        if "error" in data:
            raise SbpServiceException(data["description"])

        if data["status"] == "error":
            raise SbpServiceException(data["status_description"])

        return data
