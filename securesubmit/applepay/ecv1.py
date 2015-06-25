import jsonpickle

from securesubmit.infrastructure import HpsException


class PaymentData(object):
    _json_payment_token = None
    application_expiration_date = None
    application_primary_account_number = None
    currency_code = None
    device_manufacturer_identifier = None
    payment_data = None
    transaction_amount = None

    def __init__(self, json):
        self._json_payment_token = json
        self._hydrate_from_json()

    def _hydrate_from_json(self):
        try:
            jelement = jsonpickle.decode(self._json_payment_token)

            self.application_expiration_date = jelement['applicationExpirationDate']
            self.application_primary_account_number = jelement['applicationPrimaryAccountNumber']
            self.currency_code = jelement['currencyCode']
            self.device_manufacturer_identifier = jelement['deviceManufacturerIdentifier']

            cryptogram = jelement['paymentData']['onlinePaymentCryptogram']
            eci_indicator = ''
            if 'eciIndicator' in jelement['paymentData']:
                eci_indicator = str(jelement['paymentData']['eciIndicator'])

            self.payment_data = PaymentData3DS(cryptogram, eci_indicator)
            self.transaction_amount = int(jelement['transactionAmount']) / 100
        except Exception, e:
            raise HpsException(e.message, e)


class PaymentData3DS(object):
    online_payment_cryptogram = None
    payment_data_type = '3DSecure'
    eci_indicator = ''

    def __init__(self, online_payment_cryptogram, eci_indicator):
        self.online_payment_cryptogram = online_payment_cryptogram
        self.eci_indicator = eci_indicator


class PaymentToken(object):
    _json_token_data = None
    data = None
    header = None
    signature = None
    version = None

    def __init__(self, json):
        if json == '' or len(json) == 0:
            raise HpsException("JSON provided is either a null or empty string")

        self._json_token_data = json
        self._hydrate_from_json()

    def _hydrate_from_json(self):
        try:
            jelement = jsonpickle.decode(self._json_token_data)

            self.data = jelement['data']

            public_key = jelement['header']['ephemeralPublicKey']
            hash = jelement['header']['publicKeyHash']
            tran = jelement['header']['transactionId']

            self.header = PaymentTokenHeader(public_key, hash, tran)
            self.signature = jelement['signature']
            self.version = jelement['version']
        except Exception, e:
            raise HpsException(e.message, e)


class PaymentTokenHeader(object):
    ephemeral_public_key = None
    public_key_hash = None
    transaction_id = None
    application_data = None

    def __init__(self, ephemeral_public_key, public_key_hash, transaction_id, application_data=None):
        self.ephemeral_public_key = ephemeral_public_key
        self.public_key_hash = public_key_hash
        self.transaction_id = transaction_id
        self.application_data = application_data

    def has_application_data(self):
        return self.application_data is not None and len(self.application_data) > 0