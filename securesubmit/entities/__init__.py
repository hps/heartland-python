"""
    core.py

    defines the base entity models.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

import datetime

from securesubmit.infrastructure.enums import HpsTransactionType


class HpsAddress(object):
    address = None
    city = None
    state = None
    zip = None
    country = None


class HpsConsumer(object):
    first_name = None
    last_name = None
    phone = None
    email = None
    address = None

    def __init__(self):
        self.address = HpsAddress()


class HpsTokenData(object):
    token_rsp_code = None
    token_rsp_msg = None
    token_value = None


class HpsTransaction(object):
    _header = None
    transaction_id = None
    client_transaction_id = None
    response_code = None
    response_text = None
    reference_number = None

    @classmethod
    def from_dict(cls, rsp):
        # hydrate the header
        transaction = cls()
        transaction._header = HpsTransactionHeader()
        if 'ClientTxnId' in rsp['Header']:
            transaction._header.client_txn_id = rsp['Header']['ClientTxnId']

        transaction._header.gateway_rsp_msg = rsp['Header']['GatewayRspMsg']
        transaction._header.gateway_rsp_code = rsp['Header']['GatewayRspCode']
        if 'RspDT' in rsp['Header']:
            transaction._header.rsp_dt = rsp['Header']['RspDT']

        transaction.transaction_id = int(rsp['Header']['GatewayTxnId'])
        transaction.client_transaction_id = transaction._header.client_txn_id

        # hydrate the body
        if 'Transaction' in rsp:
            item = rsp['Transaction'].itervalues().next()
            if item is not None:
                if 'RspCode' in item:
                    transaction.response_code = item['RspCode']

                if 'RspText' in item:
                    transaction.response_text = item['RspText']

                if 'RefNbr' in item:
                    transaction.reference_number = item['RefNbr']
        else:
            transaction.response_code = rsp['Header']['GatewayRspCode']
            transaction.response_text = rsp['Header']['GatewayRspMsg']

        return transaction

    @staticmethod
    def _transaction_type_to_service_name(transaction_type):
        options = {HpsTransactionType.Authorize: "CreditAuth",
                   HpsTransactionType.Capture: "CreditAddToBatch",
                   HpsTransactionType.Charge: "CreditSale",
                   HpsTransactionType.Refund: "CreditReturn",
                   HpsTransactionType.Reverse: "CreditReversal",
                   HpsTransactionType.Verify: "CreditAccountVerify",
                   HpsTransactionType.List: "ReportActivity",
                   HpsTransactionType.Get: "ReportTxnDetail",
                   HpsTransactionType.Void: "CreditVoid",
                   HpsTransactionType.BatchClose: "BatchClose",
                   HpsTransactionType.SecurityError: "SecurityError"}
        if transaction_type in options.viewkeys():
            return options[transaction_type]
        else:
            return ""

    @staticmethod
    def _service_name_to_transaction_type(service_name):
        options = {"CreditAuth": HpsTransactionType.Authorize,
                   "CreditAddToBatch": HpsTransactionType.Capture,
                   "CreditSale": HpsTransactionType.Charge,
                   "CreditReturn": HpsTransactionType.Refund,
                   "CreditReversal": HpsTransactionType.Reverse,
                   "CreditAccountVerify": HpsTransactionType.Verify,
                   "ReportActivity": HpsTransactionType.List,
                   "ReportTxnDetail": HpsTransactionType.Get,
                   "CreditVoid": HpsTransactionType.Void,
                   "BatchClose": HpsTransactionType.BatchClose,
                   "SecurityError": HpsTransactionType.SecurityError}
        if service_name in options.viewkeys():
            return options[service_name]
        else:
            return None


class HpsTransactionDetails(object):
    client_transaction_id = None
    memo = None
    invoice_number = None
    customer_id = None


class HpsTransactionHeader(object):
    gateway_rsp_code = None
    gateway_rsp_msg = None
    rsp_dt = None
    client_txn_id = None


class HpsDirectMarketData(object):
    invoice_number = None
    ship_month = None
    ship_day = None

    def __init__(self, invoice_number=None, ship_day=None, ship_month=None):
        self.invoice_number = invoice_number

        if ship_day is not None:
            self.ship_day = ship_day
        else:
            self.ship_day = datetime.datetime.now().day

        if ship_month is not None:
            self.ship_month = ship_month
        else:
            self.ship_month = datetime.datetime.now().month