import re

import requests

from config import Config

BILL_STATUS_SUCCESS = 10


class SbpServiceException(Exception):
    pass


class SbpService:

    @staticmethod
    def _credentials():
        return {
            "apikey": Config.LIFEPAY_APIKEY,
            "login": Config.LIFEPAY_LOGIN,
        }

    @staticmethod
    def _format_phone(phone: str):
        digits = re.sub(r'\D', '', phone)

        if len(digits) == 11 and digits[0] == '8':
            digits = '7' + digits[1:]
        elif len(digits) == 10:
            digits = '7' + digits

        if len(digits) != 11 or digits[0] != '7':
            return None

        return digits

    @staticmethod
    def create_payment(amount: int, customer_phone: str = None):
        payload = {
            **SbpService._credentials(),
            "amount": f"{amount:.2f}",
            "description": f"Оплата заказа в частном кинотеатре Film Is",
            "method": "sbp",
            "callback_url": Config.LIFEPAY_CALLBACK_URL,
        }

        if customer_phone:
            formatted_phone = SbpService._format_phone(customer_phone)
            if formatted_phone:
                payload["customer_phone"] = formatted_phone

        response = requests.post('https://api.life-pay.ru/v1/bill', json=payload)
        data = response.json()

        if data["code"] != 0:
            raise SbpServiceException(data["message"])

        return {
            "id": str(data["data"]["number"]),
            "payment_url": data["data"]["paymentUrl"],
        }

    @staticmethod
    def get_payment_status(payment_id: str):
        params = {
            **SbpService._credentials(),
            "number": payment_id,
        }

        response = requests.get('https://api.life-pay.ru/v1/bill/status', params=params)
        data = response.json()

        if data["code"] != 0:
            raise SbpServiceException(data["message"])

        status = "successful" if data["data"]["status"] == BILL_STATUS_SUCCESS else "pending"
        return {"status": status}

    @staticmethod
    def cancel_payment(payment_id: str):
        payload = {
            **SbpService._credentials(),
            "number": payment_id,
        }

        response = requests.post('https://api.life-pay.ru/v1/bill/cancellation', json=payload)
        data = response.json()

        if data["code"] != 0:
            raise SbpServiceException(data["message"])

        return data["data"]

    @staticmethod
    def make_refund(payment_id: str):
        transaction = SbpService.get_payment_status(payment_id)

        if transaction["status"] != "successful":
            return SbpService.cancel_payment(payment_id)

        payload = {
            **SbpService._credentials(),
            "number": payment_id,
        }

        response = requests.post('https://api.life-pay.ru/v1/transactions/refund', json=payload)
        data = response.json()

        if data["code"] != 0:
            raise SbpServiceException(data["message"])

        return data["data"]
