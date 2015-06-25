"""
    credit.py

    This module defines the credit entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

import re

from securesubmit.entities import *
from securesubmit.infrastructure.enums import HpsTrackDataMethod
from securesubmit.infrastructure.validation import *


class HpsAuthorization(HpsTransaction):
    authorization_code = None
    avs_result_code = None
    cvv_result_code = None
    avs_result_text = None
    cvv_result_text = None
    cpc_indicator = None
    authorized_amount = None
    card_type = None
    description = None
    invoice_number = None
    customer_id = None
    descriptor = None
    token_data = None

    @classmethod
    def from_dict(cls, rsp):
        auth_response = rsp['Transaction'].itervalues().next()

        auth = super(HpsAuthorization, cls).from_dict(rsp)
        if 'AuthCode' in auth_response:
            auth.authorization_code = auth_response['AuthCode']

        if 'AVSRsltCode' in auth_response:
            auth.avs_result_code = auth_response['AVSRsltCode']

        if 'AVSRsltText' in auth_response:
            auth.avs_result_text = auth_response['AVSRsltText']

        if 'CVVRsltCode' in auth_response:
            auth.cvv_result_code = auth_response['CVVRsltCode']

        if 'CVVRsltText' in auth_response:
            auth.cvv_result_text = auth_response['CVVRsltText']

        if 'AuthAmt' in auth_response:
            auth.authorized_amount = auth_response['AuthAmt']

        if 'CardType' in auth_response:
            auth.card_type = auth_response['CardType']

        if 'TxnDescriptor' in auth_response:
            auth.descriptor = auth_response['TxnDescriptor']

        if 'CPCInd' in auth_response:
            auth.cpc_indicator = auth_response['CPCInd']

        if 'TokenData' in rsp['Header']:
            auth.token_data = HpsTokenData()
            auth.token_data.token_rsp_code = rsp[
                'Header']['TokenData']['TokenRspCode']
            auth.token_data.token_rsp_msg = rsp[
                'Header']['TokenData']['TokenRspMsg']
            auth.token_data.token_value = rsp[
                'Header']['TokenData']['TokenValue']

        return auth


class HpsAccountVerify(HpsAuthorization):
    pass


class HpsCardHolder(HpsConsumer):
    pass


class HpsCharge(HpsAuthorization):
    pass


class HpsChargeExceptions(object):
    issuer_exception = None
    gateway_exception = None


class HpsCreditCard(object):
    number = None
    exp_year = None
    exp_month = None
    cvv = None
    encryption_data = None

    @property
    def card_type(self):
        """Returns a string containing the card type if it
           is identifiable, or "Unknown" otherwise"""

        card_regexes = {
            "Amex": "/^3[47][0-9]{13}/",
            "MasterCard": "/^5[1-5][0-9]{14}/",
            "Visa": "/^4[0-9]{12}(?:[0-9]{3})?/",
            "DinersClub": "/^3(?:0[0-5]|[68][0-9])[0-9]{11}/",
            "EnRoute": "/^(2014|2149)/",
            "Discover": "/^6(?:011|5[0-9]{2})[0-9]{12}/",
            "Jcb": "/^(?:2131|1800|35\d{3})\d{11}/",
        }

        card_type = "Unknown"

        for card, rx in card_regexes.items():
            if re.match(rx, self.number) is not None:
                card_type = card
        return card_type

    def with_cvv(self, cvv):
        self.cvv = cvv
        return self


class HpsOfflineAuthorization(HpsTransaction):
    @classmethod
    def from_dict(cls, rsp):
        offline_auth = super(HpsOfflineAuthorization, cls).from_dict(rsp)
        offline_auth.response_code = '00'
        offline_auth.response_text = ''

        return offline_auth


class HpsRefund(HpsTransaction):
    @classmethod
    def from_dict(cls, rsp):
        refund = super(HpsRefund, cls).from_dict(rsp)
        refund.response_code = '00'
        refund.response_text = ''

        return refund


class HpsReportTransactionDetails(HpsAuthorization):
    issuer_transaction_id = None
    issuer_validation_code = None
    original_transaction_id = None
    masked_card_number = None
    settlement_amount = None
    transaction_type = None
    transaction_utc_date = None
    exceptions = None
    memo = None
    invoice_number = None
    customer_id = None

    @classmethod
    def from_dict(cls, rsp):
        report_response = rsp['Transaction'].itervalues().next()

        details = super(HpsReportTransactionDetails, cls).from_dict(rsp)
        if 'OriginalGatewayTxnId' in report_response:
            details.original_transaction_id = report_response[
                'OriginalGatewayTxnId']

        if 'SettlementAmt' in report_response['Data']:
            details.settlement_amount = report_response[
                'Data']['SettlementAmt']

        if 'MaskedCardNbr' in report_response['Data']:
            details.masked_card_number = report_response[
                'Data']['MaskedCardNbr']

        if 'ServiceName' in report_response:
            details.transaction_type = \
                HpsTransaction._service_name_to_transaction_type(
                    report_response['ServiceName'])

        if 'ReqUtcDT' in report_response['Data']:
            details.transaction_utc_date = report_response[
                'ReqUtcDT'].ToLocalTime()

        if 'AuthAmt' in report_response['Data']:
            details.authorized_amount = report_response['Data']['AuthAmt']

        if 'AVSRsltCode' in report_response['Data']:
            details.avs_result_code = report_response['Data']['AVSRsltCode']

        if 'AVSRsltText' in report_response['Data']:
            details.avs_result_text = report_response['Data']['AVSRsltText']

        if 'CardType' in report_response['Data']:
            details.card_type = report_response['Data']['CardType']

        if 'TxnDescriptor' in report_response['Data']:
            details.descriptor = report_response['Data']['TxnDescriptor']

        if 'CPCInd' in report_response['Data']:
            details.cpc_indicator = report_response['Data']['CPCInd']

        if 'CVVRsltCode' in report_response['Data']:
            details.cvv_result_code = report_response['Data']['CVVRsltCode']

        if 'CVVRsltText' in report_response['Data']:
            details.cvv_result_text = report_response['Data']['CVVRsltText']

        if 'RefNbr' in report_response['Data']:
            details.reference_number = report_response['Data']['RefNbr']

        if 'RspCode' in report_response['Data']:
            details.response_code = report_response['Data']['RspCode']

        if 'RspText' in report_response['Data']:
            details.response_text = report_response['Data']['RspText']

        if 'TokenizationMsg' in report_response['Data']:
            details.token_data = HpsTokenData()
            details.token_data.token_rsp_msg = \
                report_response['Data']['TokenizationMsg']

        if 'AdditionalTxnFields' in report_response['Data']:
            if 'Description' in report_response['Data']['AdditionalTxnFields']:
                details.memo = \
                    report_response[
                        'Data']['AdditionalTxnFields']['Description']
            if 'InvoiceNbr' in report_response['Data']['AdditionalTxnFields']:
                details.invoice_number = \
                    report_response[
                        'Data']['AdditionalTxnFields']['InvoiceNbr']
            if 'CustomerID' in report_response['Data']['AdditionalTxnFields']:
                details.customer_id = \
                    report_response[
                        'Data']['AdditionalTxnFields']['CustomerID']

        if report_response['Data']['RspCode'] != '00':
            if details.exceptions is None:
                details.exceptions = HpsChargeExceptions()
            details.exceptions.card_exception = \
                HpsIssuerResponseValidation.get_exception(
                    rsp['Header']['GatewayTxnId'],
                    str(report_response['Data']['RspCode']),
                    report_response['Data']['RspText'])

        return details


class HpsReportTransactionSummary(HpsTransaction):
    amount = None
    settlement_amount = None
    original_transaction_id = None
    masked_card_number = None
    transaction_type = None
    transaction_utc_date = None
    exceptions = None

    @classmethod
    def from_dict(cls, rsp, filter_by):
        report_response = rsp['Transaction'].itervalues().next()

        transactions = []
        service_name = ''
        if filter_by is not None:
            service_name = HpsTransaction._transaction_type_to_service_name(
                filter_by)

        for charge in report_response['Details']:
            if filter_by is None or charge['ServiceName'] == service_name:
                trans = super(HpsReportTransactionSummary, cls).from_dict(rsp)

                trans.original_transaction_id = None
                if 'OriginalGatewayTxnId' in charge:
                    trans.original_transaction_id = charge[
                        'OriginalGatewayTxnId']

                trans.masked_card_number = None
                if 'MaskedCardNbr' in charge:
                    trans.masked_card_number = charge['MaskedCardNbr']

                trans.response_code = None
                if 'IssuerRspCode' in charge:
                    trans.response_code = charge['IssuerRspCode']

                trans.response_text = None
                if 'IssuerRspText' in charge:
                    trans.response_text = charge['IssuerRspText']

                trans.amount = None
                if 'Amt' in charge:
                    trans.amount = charge['Amt']

                trans.settlement_amount = None
                if 'SettlementAmt' in charge:
                    trans.settlement_amount = charge['SettlementAmt']

                trans.transaction_utc_date = None
                if 'TxnUtcDT' in charge:
                    pattern = '%Y-%m-%dT%H:%M:%SZ'
                    if '.' in charge['TxnUtcDT']:
                        pattern = '%Y-%m-%dT%H:%M:%S.%fZ'

                    trans.transaction_utc_date = datetime.datetime.strptime(
                        charge['TxnUtcDT'],
                        pattern)

                trans.transaction_type = \
                    HpsTransaction._service_name_to_transaction_type(
                        charge['ServiceName'])

                if filter_by is not None:
                    trans.transaction_type = filter_by

                if (charge['GatewayRspCode'] != '0' or
                        charge['IssuerRspCode'] != '00'):
                    trans.exceptions = HpsChargeExceptions()
                    if charge['GatewayRspCode'] != '0':
                        trans.exceptions.hps_exception = \
                            HpsGatewayResponseValidation.get_exception(
                                str(charge['GatewayRspCode']),
                                charge['GatewayRspMsg'])

                    if charge['IssuerRspCode'] != '00':
                        trans.exceptions.card_exeption = \
                            HpsIssuerResponseValidation.get_exception(
                                charge['GatewayTxnId'],
                                str(charge['IssuerRspCode']),
                                charge['IssuerRspText'])
                transactions.append(trans)

        return transactions


class HpsReversal(HpsTransaction):
    avs_result_code = None
    cvv_result_code = None
    avs_result_text = None
    cvv_result_text = None
    cpc_indicator = None

    @classmethod
    def from_dict(cls, rsp):
        reverse_response = rsp['Transaction'].itervalues().next()

        reverse = super(HpsReversal, cls).from_dict(rsp)
        reverse.avs_result_code = None
        if 'AVSRsltCode' in reverse_response:
            reverse.avs_result_code = reverse_response['AVSRsltCode']

        reverse.avs_result_text = None
        if 'AVSRsltText' in reverse_response:
            reverse.avs_result_text = reverse_response['AVSRsltText']

        reverse.cpc_indicator = None
        if 'CPCInd' in reverse_response:
            reverse.cpc_indicator = reverse_response['CPCInd']

        reverse.cvv_result_code = None
        if 'CVVRsltCode' in reverse_response:
            reverse.cvv_result_code = reverse_response['CVVRsltCode']

        reverse.cvv_result_text = None
        if 'CVVRsltText' in reverse_response:
            reverse.cvv_result_text = reverse_response['CVVRsltText']

        return reverse


class HpsVoid(HpsTransaction):
    @classmethod
    def from_dict(cls, rsp):
        void = super(HpsVoid, cls).from_dict(rsp)
        void.response_code = '00'
        void.response_text = ''

        return void


class HpsCPCEdit(HpsTransaction):
    @classmethod
    def from_dict(cls, rsp):
        edit = super(HpsCPCEdit, cls).from_dict(rsp)
        edit.response_code = '00'
        edit.response_text = ''

        return edit


class HpsCPCData:
    card_holder_po_number = None
    tax_type = None
    tax_amount = None

    def __init__(self, card_holder_po_number=None, tax_type=None, tax_amount=None):
        if card_holder_po_number is not None:
            if len(card_holder_po_number) > 17:
                raise HpsArgumentException('Card holder po number must be less that 17 characters.')
            self.card_holder_po_number = card_holder_po_number

        self.tax_type = tax_type

        if tax_amount is not None:
            self.tax_amount = tax_amount


class HpsRecurringBilling(HpsAuthorization):
    pass


class HpsTrackData(object):
    method = HpsTrackDataMethod.swipe
    value = None
    encryption_data = None


class HpsEncryptionData(object):
    version = None
    encrypted_track_number = None
    ktb = None
    ksn = None


class HpsAdditionalAmount(object):
    amount_type = None
    amount = None

    def __init__(self, amount_type=None, amount=None):
        self.amount_type = amount_type
        self.amount = amount


class HpsAutoSubstantiation(object):
    merchant_verification_value = None
    real_time_substantiation = False
    additional_amounts = []

    def __init__(self, additional_amounts=None, real_time_substantiation=False, merchant_verification_value=None):
        self.additional_amounts = additional_amounts
        self.merchant_verification_value = merchant_verification_value
        self.real_time_substantiation = real_time_substantiation


class HpsTxnReferenceData(object):
    authorization_code = None
    card_number_last_4 = None