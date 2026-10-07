import re

import requests

from config import Config

API_URL = 'https://api.life-pay.ru/v1'
BILL_STATUS_SUCCESS = 10


class SbpServiceException(Exception):
    pass


def log(message: str):
    print(f"[SbpService] {message}", flush=True)


def _call(http_method: str, path: str, /, **params):
    payload = {"apikey": Config.LIFEPAY_APIKEY, "login": Config.LIFEPAY_LOGIN, **params}
    payload_kwarg = {"params": payload} if http_method == "get" else {"json": payload}

    response = getattr(requests, http_method)(f"{API_URL}/{path}", **payload_kwarg)
    data = response.json()

    log(f"{path}: params={params} status_code={response.status_code} response={data}")

    if data["code"] != 0:
        raise SbpServiceException(data["message"])

    return data


def _format_phone(phone: str):
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 11 and digits[0] == '8':
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits

    if len(digits) != 11 or digits[0] != '7':
        return None

    return digits


def create_payment(amount: int, customer_phone: str = None):
    params = {
        "amount": f"{amount:.2f}",
        "description": "Оплата услуг клининга по площади",
        "method": "sbp",
        "callback_url": Config.LIFEPAY_CALLBACK_URL,
    }

    formatted_phone = _format_phone(customer_phone) if customer_phone else None
    if formatted_phone:
        params["customer_phone"] = formatted_phone

    bill = _call("post", "bill", **params)["data"]

    return {"id": str(bill["number"]), "payment_url": bill["paymentUrl"]}


def get_payment_status(payment_id: str):
    data = _call("get", "bill/status", number=payment_id)
    bill_status = data.get("data", {}).get(str(payment_id), {}).get("status")

    if bill_status is None:
        log(f"get_payment_status: no status for payment_id={payment_id} in response data={data.get('data')}")

    is_success = bill_status == BILL_STATUS_SUCCESS or bill_status == "success"
    return {"status": "successful" if is_success else "pending"}


def cancel_payment(payment_id: str):
    return _call("post", "bill/cancellation", number=payment_id)["data"]


def make_refund(payment_id: str):
    """Неоплаченный счёт отменяет, оплаченный возвращает"""
    status = get_payment_status(payment_id)

    log(f"make_refund: payment_id={payment_id} status_check={status}")

    if status["status"] != "successful":
        return cancel_payment(payment_id)

    return _call("post", "transactions/refund", number=payment_id)["data"]
