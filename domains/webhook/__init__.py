from flask import Blueprint
from domains.webhook.handlers import *

webhook_blueprint = Blueprint('webhook_blueprint', __name__)


@webhook_blueprint.route('/sbp', methods=['POST'])
def sbp_transaction_webhook():
    return handlers.sbp_transaction_webhook()
