"""
    validation.py

    This module defines the validations for the Hps return types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

import datetime
from securesubmit.infrastructure.enums import HpsExceptionCodes
from securesubmit.infrastructure import (HpsGatewayException,
                                         HpsAuthenticationException,
                                         HpsInvalidRequestException,
                                         HpsCreditException)


_issuer_code_to_credit_exception_code = {
    '02': HpsExceptionCodes.card_declined,
    '03': HpsExceptionCodes.card_declined,
    '04': HpsExceptionCodes.card_declined,
    '05': HpsExceptionCodes.card_declined,
    '41': HpsExceptionCodes.card_declined,
    '43': HpsExceptionCodes.card_declined,
    '44': HpsExceptionCodes.card_declined,
    '51': HpsExceptionCodes.card_declined,
    '56': HpsExceptionCodes.card_declined,
    '61': HpsExceptionCodes.card_declined,
    '62': HpsExceptionCodes.card_declined,
    '63': HpsExceptionCodes.card_declined,
    '65': HpsExceptionCodes.card_declined,
    '78': HpsExceptionCodes.card_declined,
    '06': HpsExceptionCodes.processing_error,
    '07': HpsExceptionCodes.processing_error,
    '12': HpsExceptionCodes.processing_error,
    '15': HpsExceptionCodes.processing_error,
    '19': HpsExceptionCodes.processing_error,
    '52': HpsExceptionCodes.processing_error,
    '53': HpsExceptionCodes.processing_error,
    '57': HpsExceptionCodes.processing_error,
    '58': HpsExceptionCodes.processing_error,
    '76': HpsExceptionCodes.processing_error,
    '77': HpsExceptionCodes.processing_error,
    '96': HpsExceptionCodes.processing_error,
    'EC': HpsExceptionCodes.processing_error,
    '13': HpsExceptionCodes.invalid_amount,
    '14': HpsExceptionCodes.incorrect_number,
    '54': HpsExceptionCodes.expired_card,
    '55': HpsExceptionCodes.invalid_pin,
    '75': HpsExceptionCodes.pin_entries_exceeded,
    '80': HpsExceptionCodes.invalid_expiry,
    '86': HpsExceptionCodes.pin_verification,
    '91': HpsExceptionCodes.issuer_timeout,
    'EB': HpsExceptionCodes.incorrect_cvc,
    'N7': HpsExceptionCodes.incorrect_cvc
}

_credit_exception_code_to_message = {
    HpsExceptionCodes.card_declined:
    "The card was declined",
    HpsExceptionCodes.processing_error:
    "An error occurred while processing the card.",
    HpsExceptionCodes.invalid_amount:
    "Must be greater than or equal 0.",
    HpsExceptionCodes.expired_card:
    "The card has expired.",
    HpsExceptionCodes.invalid_pin:
    "The 4-digit pin is invalid.",
    HpsExceptionCodes.pin_entries_exceeded:
    "Maximum number of pin retries exceeded.",
    HpsExceptionCodes.invalid_expiry:
    "Card expiration date is invalid.",
    HpsExceptionCodes.pin_verification:
    "Can't verify card pin number.",
    HpsExceptionCodes.incorrect_cvc:
    "The card's security code is incorrect.",
    HpsExceptionCodes.issuer_timeout:
    "The card issuer timed-out.",
    HpsExceptionCodes.unknown_credit_error:
    "An unknown issuer error has occurred."
}


class HpsInputValidation(object):
    _default_allowed_currencies = {'usd', 'USD'}

    @staticmethod
    def check_amount(amount):
        if amount < 0:
            raise HpsInvalidRequestException(
                HpsExceptionCodes.invalid_amount,
                'Must be greater than or equal to 0.',
                'amount')

    @staticmethod
    def check_currency(currency, allowed_currencies=None):
        currencies = HpsInputValidation._default_allowed_currencies
        if allowed_currencies is not None:
            currencies = allowed_currencies

        if currency is None or currency == '':
            raise HpsInvalidRequestException(
                HpsExceptionCodes.missing_currency,
                'Currency cannot be None.', 'currency')
        elif currency not in currencies:
            raise HpsInvalidRequestException(
                HpsExceptionCodes.invalid_currency,
                'The only supported currency is \'usd\'.',
                'currency')

    @staticmethod
    def check_date_not_future(date):
        if date is not None and \
                date > datetime.datetime.utcnow():
            raise HpsInvalidRequestException(
                HpsExceptionCodes.invalid_date,
                'Date cannot be in the future.',
                'date')


class HpsGatewayResponseValidation(object):
    @staticmethod
    def check_response(response, expected_type):
        rsp_code = response['Header']['GatewayRspCode']
        rsp_text = response['Header']['GatewayRspMsg']
        e = HpsGatewayResponseValidation.get_exception(rsp_code, rsp_text)

        if e is not None:
            raise e

        if 'Transaction' not in response and \
                expected_type not in response['Transaction']:
            raise HpsGatewayException(
                HpsExceptionCodes.unexpected_gateway_response,
                'Unexpected response from HPS gateway.')

    @staticmethod
    def get_exception(response_code, response_text):
        if response_code == '0':
            return None
        elif response_code == '-2':
            return HpsAuthenticationException(
                HpsExceptionCodes.authentication_error,
                ('Authentication error. '
                 'Please double check your service configuration.'))
        elif response_code == '1':
            return HpsGatewayException(
                HpsExceptionCodes.unknown_gateway_error,
                response_text, response_code, response_text)
        elif response_code == '3':
            return HpsGatewayException(
                HpsExceptionCodes.invalid_original_transaction,
                response_text, response_code, response_text)
        elif response_code == '5':
            return HpsGatewayException(
                HpsExceptionCodes.no_open_batch,
                response_text, response_code, response_text)
        elif response_code == '12':
            return HpsGatewayException(
                HpsExceptionCodes.invalid_cpc_data,
                'Invalid CPC data.',
                response_code, response_text)
        elif response_code == '13':
            return HpsGatewayException(
                HpsExceptionCodes.invalid_card_data,
                'Invalid card data.',
                response_code, response_text)
        elif response_code == '14':
            return HpsGatewayException(
                HpsExceptionCodes.invalid_number,
                'The card number is not valid.',
                response_code, response_text)
        elif response_code == '30':
            return HpsGatewayException(
                HpsExceptionCodes.gateway_timeout,
                'Gateway timed out.',
                response_code, response_text)
        else:
            return HpsGatewayException(
                HpsExceptionCodes.unknown_gateway_error,
                response_text, response_code, response_text)


class HpsIssuerResponseValidation(object):
    @staticmethod
    def check_response(transaction_id, response_code, response_text):
        e = HpsIssuerResponseValidation.get_exception(
            transaction_id, response_code, response_text)

        if e is not None:
            raise e

    @staticmethod
    def get_exception(transaction_id, response_code, response_text):
        if (response_code == '85' or
                response_code == '00' or
                response_code == '0'):
            return None

        code = None
        for k, v in _issuer_code_to_credit_exception_code.iteritems():
            if k == response_code:
                code = v

        if code is None:
            return HpsCreditException(
                transaction_id,
                HpsExceptionCodes.unknown_credit_error,
                _credit_exception_code_to_message[
                    HpsExceptionCodes.unknown_credit_error],
                response_code, response_text)

        message = None
        if code in _credit_exception_code_to_message:
            message = _credit_exception_code_to_message[code]
        else:
            message = 'Unknown issuer error.'

        return HpsCreditException(
            transaction_id, code, message,
            response_code, response_text)
