"""
    gateway.py

    Defines the gateway services for the HPS Portico Gateway.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""
import base64
import urllib
import urllib3.contrib.pyopenssl
import certifi
import xml.etree.cElementTree as Et
import itertools
import time

import jsonpickle
import xmltodict as xmltodict

from securesubmit.infrastructure import *
from securesubmit.entities.credit import *
from securesubmit.entities.batch import *
from securesubmit.entities.check import *
from securesubmit.entities.gift import *
from securesubmit.entities.payplan import *
from securesubmit.entities.activation import *
from securesubmit.infrastructure.enums import EncodingType

urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


class HpsSoapGatewayService(object):
    _config = None
    _base_config = None
    _url = None
    _logging = False

    def __init__(self, config=None, enable_logging=False):
        self._base_config = HpsConfiguration()
        self._config = config
        self._logging = enable_logging

        self._url = self._base_config.soap_service_uri
        if self._config is not None:
            self._url = self._config.service_uri

        secret_api_key = self._base_config.secret_api_key
        if self._config is not None:
            secret_api_key = self._config.secret_api_key

        if secret_api_key is not None and secret_api_key != "":
            if "_uat_" in secret_api_key:
                self._url = 'https://api-uat.heartlandportico.com/paymentserver.v1/PosGatewayService.asmx?wsdl'
            elif "_cert_" in secret_api_key:
                self._url = ("https://cert.api2.heartlandportico.com/"
                             "Hps.Exchange.PosGateway/"
                             "PosGatewayService.asmx?wsdl")
            else:
                self._url = ("https://api2.heartlandportico.com/"
                             "Hps.Exchange.PosGateway/"
                             "PosGatewayService.asmx?wsdl")

    @property
    def services_config(self):
        return self._config

    @services_config.setter
    def services_config(self, value):
        self._config = value

    def do_transaction(self, transaction, client_transaction_id=None):
        if self._is_config_invalid():
            raise HpsAuthenticationException(
                HpsExceptionCodes.invalid_configuration,
                ('The HPS SDK has not been properly configured. Please make sure to initialize the config either '
                 'in a service constructor or in your App.config or Web.config file.')
            )
        try:
            # Envelope
            envelope = Et.Element("soap:Envelope")
            envelope.set("xmlns:soap", "http://schemas.xmlsoap.org/soap/envelope/")
            envelope.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            envelope.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
            body = Et.SubElement(envelope, "soap:Body")

            # Request
            request = Et.SubElement(body, "PosRequest")
            request.set("xmlns", "http://Hps.Exchange.PosGateway")
            version1 = Et.SubElement(request, "Ver1.0")

            # Header
            header = Et.SubElement(version1, "Header")
            # secret_api_key = None
            if self._config is not None:
                secret_api_key = self._config.secret_api_key
            else:
                secret_api_key = self._base_config.secret_api_key

            if secret_api_key is not None and secret_api_key != "":
                api_key = Et.SubElement(header, "SecretAPIKey")
                api_key.text = secret_api_key.strip()
            else:
                site_id = Et.SubElement(header, 'SiteId')
                device_id = Et.SubElement(header, 'DeviceId')
                license_id = Et.SubElement(header, 'LicenseId')
                username = Et.SubElement(header, 'UserName')
                password = Et.SubElement(header, 'Password')

                if self._config is not None:
                    site_id.text = str(self._config.site_id)
                    device_id.text = str(self._config.device_id)
                    license_id.text = str(self._config.license_id)
                    username.text = self._config.username
                    password.text = self._config.password
                else:
                    site_id.text = str(self._base_config.site_id)
                    device_id.text = str(self._base_config.device_id)
                    license_id.text = str(self._base_config.license_id)
                    username.text = self._base_config.username
                    password.text = self._base_config.password

            developer_id = self._base_config.developer_id
            version_id = self._base_config.version_number
            if self._config is not None:
                developer_id = self._config.developer_id
                version_id = self._config.version_number

            if developer_id != '' and developer_id is not None:
                Et.SubElement(header, 'DeveloperID').text = developer_id
            if version_id != '' and version_id is not None:
                Et.SubElement(header, 'VersionNbr').text = version_id

            if client_transaction_id is not None:
                client_txn_id = Et.SubElement(header, 'ClientTxnId')
                client_txn_id.text = client_transaction_id

            # Transaction
            trans = Et.SubElement(version1, "Transaction")
            trans.append(transaction)

            xml = Et.tostring(envelope).encode('utf-8')
            if self._logging:
                print 'URL: ' + self._url
                print 'Request: ' + xml

            request_headers = {'Content-type': 'text/xml; charset=UTF-8',
                               'Content-length': str(len(xml))}
            request = http.request('POST', self._url, headers=request_headers, body=xml)
            raw_response = request.data
            if self._logging:
                print 'Response: ' + raw_response

            namespaces = {"http://Hps.Exchange.PosGateway": None,
                          "http://schemas.xmlsoap.org/soap/envelope/": None}

            response = xmltodict.parse(raw_response, process_namespaces=True, namespaces=namespaces)

            if ('Envelope' in response and
                    'Body' in response['Envelope'] and
                    'PosResponse' in response['Envelope']['Body']):
                return response['Envelope']['Body']['PosResponse']
            else:
                raise HpsException("Unexpected response")
        except Exception, e:
            if self._logging:
                print e.message
            raise HpsGatewayException(HpsExceptionCodes.unknown_gateway_error, 'Unable to process transaction', None, None, e)

    def _is_config_invalid(self):
        """Determine whether the HPS config has been initialized,
        in one way or another.
        """
        if self._config is None and \
            (self._base_config.secret_api_key is None or
                self._base_config.license_id == -1 or
                self._base_config.device_id == -1 or
                self._base_config.password is None or
                self._base_config.site_id == -1 or
                self._base_config.username is None):
            return True
        else:
            return False

    @staticmethod
    def hydrate_gift_card_data(gift_card, element_name='CardData'):
        card_element = Et.Element(element_name)
        if gift_card.card_number is not None:
            Et.SubElement(card_element, 'CardNbr').text = gift_card.card_number
        elif gift_card.track_data is not None:
            Et.SubElement(card_element, 'TrackData').text = gift_card.track_data
        elif gift_card.alias is not None:
            Et.SubElement(card_element, 'Alias').text = gift_card.alias
        elif gift_card.token_value is not None:
            Et.SubElement(card_element, 'TokenValue').text = gift_card.token_value

        if gift_card.encryption_data is not None:
            card_element.append(HpsSoapGatewayService.hydrate_encryption_data(gift_card.encryption_data))

        if gift_card.pin is not None:
            Et.SubElement(card_element, 'PIN').text = gift_card.pin

        return card_element

    @staticmethod
    def hydrate_card_holder_data(card_holder):
        """Hydrate a new HPS card holder data type."""
        holder = Et.Element('CardHolderData')
        Et.SubElement(
            holder,
            'CardHolderFirstName').text = card_holder.first_name
        Et.SubElement(
            holder,
            'CardHolderLastName').text = card_holder.last_name
        if card_holder.email is not None:
            Et.SubElement(
                holder,
                'CardHolderEmail').text = card_holder.email
        if card_holder.phone is not None:
            Et.SubElement(
                holder,
                'CardHolderPhone').text = card_holder.phone
        Et.SubElement(
            holder,
            'CardHolderAddr').text = card_holder.address.address
        Et.SubElement(
            holder,
            'CardHolderCity').text = card_holder.address.city
        Et.SubElement(
            holder,
            'CardHolderState').text = card_holder.address.state
        Et.SubElement(
            holder,
            'CardHolderZip').text = card_holder.address.zip

        return holder

    @staticmethod
    def hydrate_card_manual_entry(card, card_present=False, reader_present=False):
        """Hydrate a new HPS manual entry card data type."""

        manual_entry = Et.Element('ManualEntry')
        Et.SubElement(manual_entry, 'CardNbr').text = card.number
        Et.SubElement(manual_entry, 'ExpMonth').text = str(card.exp_month)
        Et.SubElement(manual_entry, 'ExpYear').text = str(card.exp_year)
        if card.cvv is not None:
            cvv_element = Et.SubElement(manual_entry, 'CVV2')
            cvv_element.text = str(card.cvv)
        Et.SubElement(manual_entry, 'CardPresent').text = 'Y' if card_present else 'N'
        Et.SubElement(manual_entry, 'ReaderPresent').text = 'Y' if reader_present else 'N'

        return manual_entry

    @staticmethod
    def hydrate_additional_txn_fields(details):
        """Hydrate additional transaction fields."""

        if details is not None and isinstance(details, HpsTransactionDetails):
            addons = Et.Element('AdditionalTxnFields')

            if details.memo is not None:
                memo = Et.SubElement(addons, 'Description')
                memo.text = details.memo

            if details.customer_id is not None:
                customer_id = Et.SubElement(addons, "CustomerID")
                customer_id.text = details.customer_id

            if details.invoice_number is not None:
                invoice_number = Et.SubElement(addons, "InvoiceNbr")
                invoice_number.text = details.invoice_number

            return addons
        else:
            return None

    @staticmethod
    def hydrate_consumer_info(check):
        consumer_info = Et.Element('ConsumerInfo')
        if check.check_holder.address is not None:
            addr1 = Et.SubElement(consumer_info, 'Address1')
            addr1.text = check.check_holder.address.address

            city = Et.SubElement(consumer_info, 'City')
            city.text = check.check_holder.address.city

            state = Et.SubElement(consumer_info, 'State')
            state.text = check.check_holder.address.state

            _zip = Et.SubElement(consumer_info, 'Zip')
            _zip.text = check.check_holder.address.zip

        if check.check_holder.check_name is not None:
            check_name = Et.SubElement(consumer_info, 'CheckName')
            check_name.text = check.check_holder.check_name

        if check.check_holder.courtesy_card is not None:
            courtesy_card = Et.SubElement(consumer_info, 'CourtesyCard')
            courtesy_card.text = check.check_holder.courtesy_card

        if check.check_holder.dl_number is not None:
            dl_number = Et.SubElement(consumer_info, 'DLNumber')
            dl_number.text = check.check_holder.dl_number

        if check.check_holder.dl_state is not None:
            dl_state = Et.SubElement(consumer_info, 'DLState')
            dl_state.text = check.check_holder.dl_state

        if check.check_holder.email is not None:
            email = Et.SubElement(consumer_info, 'EmailAddress')
            email.text = check.check_holder.email

        if check.check_holder.first_name is not None:
            first_name = Et.SubElement(consumer_info, 'FirstName')
            first_name.text = check.check_holder.first_name

        if check.check_holder.last_name is not None:
            last_name = Et.SubElement(consumer_info, 'LastName')
            last_name.text = check.check_holder.last_name

        if check.check_holder.phone is not None:
            phone_number = Et.SubElement(consumer_info, 'PhoneNumber')
            phone_number.text = check.check_holder.phone

        if check.check_holder.ssnl4 is not None or check.check_holder.dob_year is not None:
            identity_element = Et.SubElement(consumer_info, 'IdentityInfo')
            if check.check_holder.ssnl4 is not None:
                Et.SubElement(identity_element, 'SSNL4').text = check.check_holder.ssnl4
            if check.check_holder.dob_year is not None:
                Et.SubElement(identity_element, 'DOBYear').text = check.check_holder.dob_year

        return consumer_info

    @staticmethod
    def hydrate_check_data(check):
        account_info = Et.Element('AccountInfo')
        if check.account_number is not None:
            acc_number = Et.SubElement(account_info, 'AccountNumber')
            acc_number.text = check.account_number
        if check.check_number is not None:
            check_number = Et.SubElement(account_info, 'CheckNumber')
            check_number.text = check.check_number
        if check.micr_number is not None:
            micr_data = Et.SubElement(account_info, 'MICRData')
            micr_data.text = check.micr_number
        if check.routing_number is not None:
            routing_number = Et.SubElement(account_info, 'RoutingNumber')
            routing_number.text = check.routing_number
        if check.account_type is not None:
            acc_type = Et.SubElement(account_info, 'AccountType')
            acc_type.text = str(check.account_type)

        return account_info

    @staticmethod
    def hydrate_direct_market_data(direct_market_data):
        if direct_market_data is not None and isinstance(direct_market_data, HpsDirectMarketData):
            market_data = Et.Element('DirectMktData')

            Et.SubElement(market_data, 'DirectMktInvoiceNbr').text = direct_market_data.invoice_number
            Et.SubElement(market_data, 'DirectMktShipDay').text = str(direct_market_data.ship_day)
            Et.SubElement(market_data, 'DirectMktShipMonth').text = str(direct_market_data.ship_month)

            return market_data
        else:
            return None

    @staticmethod
    def hydrate_cpc_data(cpc_data):
        if cpc_data is not None and isinstance(cpc_data, HpsCPCData):
            cpc_element = Et.Element('CPCData')

            if cpc_data.card_holder_po_number is not None:
                Et.SubElement(cpc_element, 'CardHolderPONbr').text = cpc_data.card_holder_po_number
            if cpc_data.tax_amount is not None:
                Et.SubElement(cpc_element, 'TaxAmt').text = str(cpc_data.tax_amount)
            Et.SubElement(cpc_element, 'TaxType').text = str(cpc_data.tax_type)

            return cpc_element
        else:
            return None

    @staticmethod
    def hydrate_secure_ecommerce(source, payment_data):
        if payment_data is None:
            return None

        secure_ecommerce = Et.Element('SecureECommerce')
        Et.SubElement(secure_ecommerce, 'TypeOfPaymentData').text = str(payment_data.payment_data_type)

        payment_data_element = Et.SubElement(secure_ecommerce, 'PaymentData')
        payment_data_element.set('encoding', str(EncodingType.base64))
        payment_data_element.text = str(payment_data.online_payment_cryptogram)

        if payment_data.eci_indicator != '':
            Et.SubElement(secure_ecommerce, 'ECommerceIndicator').text = payment_data.eci_indicator
        Et.SubElement(secure_ecommerce, 'PaymentDataSource').text = str(source)

        return secure_ecommerce

    @staticmethod
    def hydrate_track_data(track_data):
        if track_data is not None and isinstance(track_data, HpsTrackData):
            track_data_element = Et.Element('TrackData')
            track_data_element.text = track_data.value
            track_data_element.set('method', str(track_data.method))

            return track_data_element
        else:
            return None

    @staticmethod
    def hydrate_encryption_data(encryption_data):
        if encryption_data is not None and isinstance(encryption_data, HpsEncryptionData):
            enc_data_element = Et.Element('EncryptionData')
            Et.SubElement(enc_data_element, 'Version').text = encryption_data.version
            if encryption_data.encrypted_track_number is not None:
                track_number = Et.SubElement(enc_data_element, 'EncryptedTrackNumber')
                track_number.text = str(encryption_data.encrypted_track_number)
            if encryption_data.ktb is not None:
                Et.SubElement(enc_data_element, 'KTB').text = encryption_data.ktb
            if encryption_data.ksn is not None:
                Et.SubElement(enc_data_element, 'KSN').text = encryption_data.ksn

            return enc_data_element
        else:
            return None

    @staticmethod
    def hydrate_token_data(token, card_present=False, reader_present=False):
        token_data = Et.Element('TokenData')
        Et.SubElement(token_data, 'TokenValue').text = token
        Et.SubElement(token_data, 'CardPresent').text = 'Y' if card_present else 'N'
        Et.SubElement(token_data, 'ReaderPresent').text = 'Y' if reader_present else 'N'

        return token_data

    @staticmethod
    def hydrate_token_params(token_params):
        if token_params is not None:
            params_element = Et.Element('TokenParameters')
            Et.SubElement(params_element, 'Mapping').text = token_params

            return params_element
        return None

    @staticmethod
    def hydrate_auto_substantiation(auto_substantiation):
        auto_element = Et.Element('AutoSubstantiation')
        if auto_substantiation.merchant_verification_code is not None:
            mvv = Et.SubElement(auto_element, 'MerchantVerificationValue')
            mvv.text = auto_substantiation.merchant_verification_code

        rts = Et.SubElement(auto_element, 'RealTimeSubstantiation')
        rts.text = 'Y' if auto_substantiation.real_time_substantiation else 'N'

        amount_count = ['First', 'Second', 'Third', 'Fourth']
        for k, v in dict(itertools.izip_longest(amount_count, auto_substantiation.additional_amounts)):
            if v is not None:
                amt_element = Et.SubElement(auto_element, '{0}AdditionalAmtInfo'.format(k))
                Et.SubElement(amt_element, 'AmtType').text = v.amount_type
                Et.SubElement(amt_element, 'Amt').text = str(v.amount)

        return auto_element

    @staticmethod
    def get_client_txn_id(details=None):
        client_txn_id = None
        if details is not None:
            client_txn_id = details.client_transaction_id
        return client_txn_id


class HpsRestGatewayService(object):
    _config = None
    _url = ''
    _limit = None
    _offset = None
    _search_fields = None
    _logging = False

    def __init__(self, config=None, enable_logging=False):
        self._config = config
        self._logging = enable_logging

        config.validate()
        self._url = config.service_uri()

    def page(self, limit, offset):
        self._limit = limit
        self._offset = offset

        return self

    def search(self, search_fields):
        self._search_fields = search_fields
        return self

    def do_request(self, verb, endpoint, data=None, additional_headers=None):
        url = self._url + endpoint
        if self._logging:
            print 'URL: ' + url

        if self._limit is not None and self._offset is not None:
            url += '?limit=' + str(self._limit) + '&offset=' + str(self._offset)

        headers = self._config.get_headers(additional_headers)
        headers['Authorization'] = 'Basic ' + base64.b64encode(self._config.secret_api_key)

        if data is not None:
            encoded_data = jsonpickle.encode(data, False, False, True)
            if self._logging:
                print 'Request: ' + encoded_data

            response = http.request(verb, url, headers=headers, body=encoded_data)
        else:
            if self._logging:
                print 'Request: ' + url
            response = http.request(verb, url, headers=headers)

        if self._logging:
            print 'Response: ' + response.data

        if response.status == 200 or response.status == 204:
            return response.data
        elif response.status == 400:
            raise HpsException(response.data)
        else:
            raise HpsException('Unexpected response.')

    @staticmethod
    def hydrate_response(object_type, response):
        if response is None or response == '':
            return None

        rsp = jsonpickle.decode(response)
        return object_type.from_dict(rsp)


class HpsCreditService(HpsSoapGatewayService):
    _filter_by = None

    def __init__(self, config=None, enable_logging=False):
        HpsSoapGatewayService.__init__(self, config, enable_logging)

    def get(self, transaction_id):
        if transaction_id is None or transaction_id <= 0:
            raise HpsArgumentException('Invalid transaction id.')

        # Build the transaction request.
        transaction = Et.Element("ReportTxnDetail")
        Et.SubElement(transaction, "TxnId").text = str(transaction_id)

        return self._submit_transaction(transaction)

    def list(self, utc_start=None, utc_end=None, filter_by=None):
        HpsInputValidation.check_date_not_future(utc_start)
        HpsInputValidation.check_date_not_future(utc_end)
        self._filter_by = filter_by

        transaction = Et.Element("ReportActivity")

        if utc_start is not None:
            start = Et.SubElement(transaction, "RptStartUtcDT")
            start.text = utc_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if utc_end is not None:
            end = Et.SubElement(transaction, "RptEndUtcDT")
            end.text = utc_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return self._submit_transaction(transaction)

    def charge(self, amount, currency, card_data,
               card_holder=None,
               request_multi_use_token=False,
               descriptor=None,
               allow_partial_auth=False,
               details=None,
               direct_market_data=None,
               cpc_req=False,
               card_present=False,
               reader_present=False):
        HpsInputValidation.check_amount(amount)
        HpsInputValidation.check_currency(currency)

        # Built the transaction request
        transaction = Et.Element('CreditSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'AllowDup').text = 'Y'
        partial_auth = Et.SubElement(block1, 'AllowPartialAuth')
        if allow_partial_auth:
            partial_auth.text = 'Y'
        else:
            partial_auth.text = 'N'

        Et.SubElement(block1, 'Amt').text = str(amount)

        # Add Card Holder
        if card_holder is not None:
            block1.append(_hydrate_card_holder_data(card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if isinstance(card_data, HpsCreditCard):
            card_data_element.append(_hydrate_card_manual_entry(card_data, card_present, reader_present))
            if card_data.encryption_data is not None:
                card_data_element.append(_hydrate_encryption_data(card_data.encryption_data))
        elif isinstance(card_data, HpsTrackData):
            card_data_element.append(_hydrate_track_data(card_data))
            if card_data.encryption_data is not None:
                card_data_element.append(_hydrate_encryption_data(card_data.encryption_data))
        else:
            card_data_element.append(_hydrate_token_data(card_data, card_present, reader_present))

        # CPC request
        if cpc_req is True:
            Et.SubElement(block1, 'CPCReq').text = 'Y'

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        if request_multi_use_token:
            token_request.text = 'Y'
        else:
            token_request.text = 'N'

        # Handle the AdditionalTxnFields
        if details is not None:
            block1.append(_hydrate_additional_txn_fields(details))

        if descriptor is not None:
            Et.SubElement(block1, "TxnDescriptor").text = descriptor

        if direct_market_data is not None:
            block1.append(_hydrate_direct_market_data(direct_market_data))

        # Submit the transaction
        client_txn_id = _get_client_txn_id(details)
        return self._submit_transaction(transaction, client_txn_id)

    def verify(self, card_data,
               card_holder=None,
               request_multi_use_token=False,
               client_transaction_id=None,
               card_present=False,
               reader_present=False):
        # Build the transaction request.
        transaction = Et.Element('CreditAccountVerify')
        block1 = Et.SubElement(transaction, 'Block1')

        # Add Card Holder
        if card_holder is not None:
            block1.append(_hydrate_card_holder_data(card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if isinstance(card_data, HpsCreditCard):
            card_data_element.append(_hydrate_card_manual_entry(card_data, card_present, reader_present))
            if card_data.encryption_data is not None:
                card_data_element.append(_hydrate_encryption_data(card_data.encryption_data))
        elif isinstance(card_data, HpsTrackData):
            card_data_element.append(_hydrate_track_data(card_data))
            if card_data.encryption_data is not None:
                card_data_element.append(_hydrate_encryption_data(card_data.encryption_data))
        else:
            card_data_element.append(_hydrate_token_data(card_data, card_present, reader_present))

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        if request_multi_use_token:
            token_request.text = 'Y'
        else:
            token_request.text = 'N'

        return self._submit_transaction(transaction, client_transaction_id)

    def authorize(self, amount, currency, card_data,
                  card_holder=None,
                  request_multi_use_token=False,
                  descriptor=None,
                  allow_partial_auth=False,
                  details=None,
                  cpc_req=False,
                  card_present=False,
                  reader_present=False):
        HpsInputValidation.check_amount(amount)
        HpsInputValidation.check_currency(currency)

        # Build the transaction Request
        transaction = Et.Element('CreditAuth')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'AllowDup').text = 'Y'
        partial_auth = Et.SubElement(block1, 'AllowPartialAuth')
        if allow_partial_auth:
            partial_auth.text = 'Y'
        else:
            partial_auth.text = 'N'

        Et.SubElement(block1, 'Amt').text = str(amount)

        # Add Card Holder
        if card_holder is not None:
            block1.append(_hydrate_card_holder_data(card_holder))

        card_data_element = Et.SubElement(block1, 'CardData')
        if isinstance(card_data, HpsCreditCard):
            card_data_element.append(_hydrate_card_manual_entry(card_data, card_present, reader_present))
            if card_data.encryption_data is not None:
                card_data_element.append(_hydrate_encryption_data(card_data.encryption_data))
        elif isinstance(card_data, HpsTrackData):
            card_data_element.append(_hydrate_track_data(card_data))
            if card_data.encryption_data is not None:
                card_data_element.append(_hydrate_encryption_data(card_data.encryption_data))
        else:
            card_data_element.append(_hydrate_token_data(card_data, card_present, reader_present))

        # CPC request
        if cpc_req is True:
            Et.SubElement(block1, 'CPCReq').text = 'Y'

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        if request_multi_use_token:
            token_request.text = 'Y'
        else:
            token_request.text = 'N'

        # Handle the AdditionalTxnFields
        if details is not None:
            block1.append(_hydrate_additional_txn_fields(details))

        if descriptor is not None:
            Et.SubElement(block1, "TxnDescriptor").text = descriptor

        client_txn_id = _get_client_txn_id(details)
        return self._submit_transaction(transaction, client_txn_id)

    def additional_auth(self, amount, transaction_id):
        HpsInputValidation.check_amount(amount)

        transaction = Et.Element('CreditAdditionalAuth')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'GatewayTxnId').text = str(transaction_id)
        Et.SubElement(block1, 'Amt').text = str(amount)

        return self._submit_transaction(transaction)

    def capture(self, transaction_id,
                amount=None,
                gratuity=None,
                client_transaction_id=None,
                direct_market_data=None):
        # Build the transaction request.
        transaction = Et.Element('CreditAddToBatch')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(transaction_id)
        if amount is not None:
            Et.SubElement(transaction, 'Amt').text = str(amount)

        # Add Gratuity
        if gratuity is not None:
            Et.SubElement(transaction, 'GratuityAmtInfo').text = str(gratuity)

        # Direct market data
        if direct_market_data is not None:
            transaction.append(_hydrate_direct_market_data(direct_market_data))

        # Submit the transaction
        rsp = self.do_transaction(transaction, client_transaction_id)["Ver1.0"]
        self._process_charge_gateway_response(rsp, transaction.tag)

        return self.get(transaction_id)

    def refund(self, amount, currency, card_data,
               card_holder=None,
               details=None):
        HpsInputValidation.check_amount(amount)
        HpsInputValidation.check_currency(currency)

        # Build the transaction request
        transaction = Et.Element('CreditReturn')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'AllowDup').text = "Y"
        Et.SubElement(block1, 'Amt').text = str(amount)

        # Add Card Holder
        if card_holder is not None:
            block1.append(_hydrate_card_holder_data(card_holder))

        # Card Data
        if isinstance(card_data, HpsCreditCard):
            card_data_element = Et.SubElement(block1, 'CardData')
            card_data_element.append(
                _hydrate_card_manual_entry(card_data))
        elif isinstance(card_data, (basestring, str)):
            card_data_element = Et.SubElement(block1, 'CardData')
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = card_data
        else:
            Et.SubElement(block1, 'GatewayTxnId').text = str(card_data)

        # Additional Txn
        if details is not None:
            block1.append(_hydrate_additional_txn_fields(details))

        client_txn_id = _get_client_txn_id(details)
        return self._submit_transaction(transaction, client_txn_id)

    def reverse(self, card_data, amount, currency, details=None):
        HpsInputValidation.check_amount(amount)
        HpsInputValidation.check_currency(currency)

        # Build the transaction request
        transaction = Et.Element('CreditReversal')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(amount)

        # Card Data
        if isinstance(card_data, HpsCreditCard):
            card_data_element = Et.SubElement(block1, 'CardData')
            card_data_element.append(
                _hydrate_card_manual_entry(card_data))
        elif isinstance(card_data, (basestring, str)):
            card_data_element = Et.SubElement(block1, 'CardData')
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = card_data
        else:
            Et.SubElement(block1, 'GatewayTxnId').text = str(card_data)

        # Additional Txn
        if details is not None:
            block1.append(_hydrate_additional_txn_fields(details))

        client_txn_id = _get_client_txn_id(details)
        return self._submit_transaction(transaction, client_txn_id)

    def void(self, transaction_id, client_transaction_id=None):
        transaction = Et.Element('CreditVoid')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(transaction_id)

        return self._submit_transaction(transaction, client_transaction_id)

    def edit(self,
             transaction_id,
             amount=None,
             gratuity=None,
             client_transaction_id=None):
        transaction = Et.Element('CreditTxnEdit')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(transaction_id)

        if amount is not None:
            Et.SubElement(transaction, 'Amt').text = str(amount)

        # Add Gratuity
        if gratuity is not None:
            Et.SubElement(transaction, 'GratuityAmtInfo').text = str(gratuity)

        # Submit the transaction
        trans = self._submit_transaction(transaction, client_transaction_id)
        trans.response_code = '00'
        trans.response_text = ''

        return trans

    def cpc_edit(self, transaction_id, cpc_data):
        transaction = Et.Element('CreditCPCEdit')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(transaction_id)
        transaction.append(_hydrate_cpc_data(cpc_data))

        return self._submit_transaction(transaction)

    def recurring(self, payment_data, amount, schedule=None, card_holder=None, one_time=False, details=None):
        HpsInputValidation.check_amount(amount)

        transaction = Et.Element('RecurringBilling')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'AllowDup').text = 'Y'
        Et.SubElement(block1, 'Amt').text = str(amount)
        if card_holder is not None:
            block1.append(_hydrate_card_holder_data(card_holder))
        if details is not None:
            block1.append(_hydrate_additional_txn_fields(details))

        if isinstance(payment_data, HpsCreditCard):
            card_data = Et.SubElement(block1, 'CardData')
            card_data.append(_hydrate_card_manual_entry(payment_data))
        elif isinstance(payment_data, HpsTokenData):
            card_data = Et.SubElement(block1, 'CardData')
            token_data = Et.SubElement(card_data, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = payment_data.token_value
        else:
            Et.SubElement(block1, 'PaymentMethodKey').text = payment_data

        schedule_id = schedule
        if isinstance(schedule, HpsPayPlanSchedule):
            schedule_id = schedule.schedule_identifier

        recurring_data = Et.SubElement(block1, 'RecurringData')
        Et.SubElement(recurring_data, 'ScheduleID').text = str(schedule_id)
        Et.SubElement(recurring_data, 'OneTime').text = 'Y' if one_time else 'N'

        client_txn_id = _get_client_txn_id(details)
        return self._submit_transaction(transaction, client_txn_id)

    def update_token_expiry(self, token, exp_month, exp_year):
        transaction = Et.Element('ManageTokens')
        Et.SubElement(transaction, 'TokenValue').text = token

        token_actions = Et.SubElement(transaction, 'TokenActions')
        set_element = Et.SubElement(token_actions, 'Set')

        exp_month_element = Et.SubElement(set_element, 'Attribute')
        Et.SubElement(exp_month_element, 'Name').text = 'ExpMonth'
        Et.SubElement(exp_month_element, 'Value').text = str(exp_month)

        exp_year_element = Et.SubElement(set_element, 'Attribute')
        Et.SubElement(exp_year_element, 'Name').text = 'ExpYear'
        Et.SubElement(exp_year_element, 'Value').text = str(exp_year)

        return self._submit_transaction(transaction)

    # def balance inquiry

    def _submit_transaction(self, transaction, client_transaction_id=None):
        rsp = self.do_transaction(transaction, client_transaction_id)['Ver1.0']

        amount = None
        if transaction.tag == 'CreditSale' or \
                transaction.tag == 'CreditAuth':
            amount = transaction.iter('Amt').next().text

        self._process_charge_gateway_response(rsp, transaction.tag, amount, 'usd')
        self._process_charge_issuer_response(rsp, transaction.tag, amount, 'usd')

        rvalue = None
        if transaction.tag == 'ReportTxnDetail':
            rvalue = HpsReportTransactionDetails.from_dict(rsp)
        elif transaction.tag == 'ReportActivity':
            rvalue = HpsReportTransactionSummary.from_dict(
                rsp, self._filter_by)
        elif transaction.tag == 'CreditSale':
            rvalue = HpsCharge.from_dict(rsp)
        elif transaction.tag == 'CreditAccountVerify':
            rvalue = HpsAccountVerify.from_dict(rsp)
        elif transaction.tag == 'CreditAuth':
            rvalue = HpsAuthorization.from_dict(rsp)
        elif transaction.tag == 'CreditReturn':
            rvalue = HpsRefund.from_dict(rsp)
        elif transaction.tag == 'CreditReversal':
            rvalue = HpsReversal.from_dict(rsp)
        elif transaction.tag == 'CreditVoid':
            rvalue = HpsVoid.from_dict(rsp)
        elif transaction.tag == 'CreditTxnEdit':
            rvalue = HpsTransaction.from_dict(rsp)
        elif transaction.tag == 'CreditCPCEdit':
            rvalue = HpsCPCEdit.from_dict(rsp)
        elif transaction.tag == 'RecurringBilling':
            rvalue = HpsRecurringBilling.from_dict(rsp)
        elif transaction.tag == 'CreditAdditionalAuth':
            rvalue = HpsAuthorization.from_dict(rsp)
        elif transaction.tag == 'ManageTokens':
            rvalue = HpsTransaction.from_dict(rsp)

        return rvalue

    def _process_charge_issuer_response(self, response, expected_type, *args):
        transaction_id = response['Header']['GatewayTxnId']
        transaction = response['Transaction'][expected_type] if 'Transaction' in response else None

        if transaction is not None:
            response_code = None
            if 'RspCode' in transaction:
                response_code = transaction['RspCode']

            response_text = None
            if 'RspText' in transaction:
                response_text = transaction['RspText']

            if response_code is not None:
                if response_code == '91':
                    try:
                        self.reverse(int(transaction_id), *args)
                    except HpsGatewayException, e:
                        if e.details.gateway_response_code == '3':
                            HpsIssuerResponseValidation.check_response(
                                transaction_id,
                                response_code,
                                response_text)
                        raise HpsCreditException(
                            transaction_id,
                            HpsExceptionCodes.issuer_timeout_reversal_error,
                            ('Error occurred while reversing ',
                             'a charge due to HPS issuer time-out.'),
                            e)
                    except Exception, e:
                        raise HpsCreditException(
                            transaction_id,
                            HpsExceptionCodes.issuer_timeout_reversal_error,
                            'Error occurred while reversing a charge due to HPS issuer time-out.',
                            e
                        )
                HpsIssuerResponseValidation.check_response(
                    transaction_id, response_code, response_text)

    def _process_charge_gateway_response(self, response, expected_type, *args):
        response_code = response['Header']['GatewayRspCode']
        if response_code == 0:
            return
        if response_code == 30:
            try:
                self.reverse(
                    response['Header']['GatewayTxnId'],
                    *args)
            except Exception, e:
                raise HpsGatewayException(
                    HpsExceptionCodes.gateway_timeout_reversal_error,
                    ('Error occurred while reversing ',
                     'a charge due to HPS gateway time-out.'),
                    e)
        HpsGatewayResponseValidation.check_response(response, expected_type)


class HpsBatchService(HpsSoapGatewayService):
    def __init__(self, config=None, enable_logging=False):
        HpsSoapGatewayService.__init__(self, config, enable_logging)

    def close_batch(self):
        transaction = Et.Element('BatchClose')
        rsp = self.do_transaction(transaction)["Ver1.0"]
        HpsGatewayResponseValidation.check_response(rsp, transaction.tag)

        # Process the Response
        batch_close = rsp['Transaction']['BatchClose']
        batch = HpsBatch()
        batch.id = None
        if 'BatchId' in batch_close:
            batch.id = batch_close['BatchId']

        batch.sequence_number = None
        if 'BatchSeqNbr' in batch_close:
            batch.sequence_number = batch_close['BatchSeqNbr']

        batch.total_amount = None
        if 'TotalAmt' in batch_close:
            batch.total_amount = batch_close['TotalAmt']

        batch.transaction_count = None
        if 'TxnCnt' in batch_close:
            batch.transaction_count = batch_close['TxnCnt']

        return batch


class HpsCheckService(HpsSoapGatewayService):
    def __init__(self, config, enable_logging=False):
        HpsSoapGatewayService.__init__(self, config, enable_logging)

    def override(self, check, amount, client_transaction_id=None):
        return self._build_transaction('OVERRIDE', check, amount, client_transaction_id)

    def recurring(self, payment_method, amount, schedule=None, one_time=False):
        HpsInputValidation.check_amount(amount)

        transaction = Et.Element('CheckSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(amount)
        Et.SubElement(block1, 'CheckAction').text = 'SALE'

        payment_method_key = payment_method
        if isinstance(payment_method, HpsPayPlanPaymentMethod):
            payment_method_key = payment_method.payment_method_key
        Et.SubElement(block1, 'PaymentMethodKey').text = str(payment_method_key)

        recurring_data = Et.SubElement(block1, 'RecurringData')
        if schedule is not None:
            schedule_key = schedule
            if isinstance(schedule, HpsPayPlanSchedule):
                schedule_key = schedule.schedule_key
            Et.SubElement(recurring_data, 'ScheduleID').text = str(schedule_key)

        Et.SubElement(recurring_data, 'OneTime').text = 'Y' if one_time else 'N'

        return self._submit_transaction(transaction)

    def return_check(self, check, amount, client_transaction_id=None):
        return self._build_transaction('RETURN', check, amount, client_transaction_id)

    def sale(self, check, amount, client_transaction_id=None):
        return self._build_transaction('SALE', check, amount, client_transaction_id)

    def void(self, transaction_id=None, client_transaction_id=None):
        if transaction_id is None and \
            client_transaction_id is None or \
            (transaction_id is not None and
             client_transaction_id is not None):
            raise HpsException(
                'Please provide a transaction id or a client transaction id.')

        transaction = Et.Element('CheckVoid')
        block1 = Et.SubElement(transaction, 'Block1')

        if transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(transaction_id)
        else:
            txn_id = Et.SubElement(block1, 'ClientTxnId')
            txn_id.text = str(client_transaction_id)

        return self._submit_transaction(transaction)

    def _build_transaction(self, action, check, amount, client_transaction_id=None):
        HpsInputValidation.check_amount(amount)
        if (check.sec_code == "CCD"
            and (check.check_holder is None
                 or check.check_holder.check_name is None)):
            raise HpsInvalidRequestException(
                HpsExceptionCodes.missing_check_name,
                'For sec code CCD the check name is required.', 'check_name')

        transaction = Et.Element('CheckSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(amount)
        block1.append(_hydrate_check_data(check))
        Et.SubElement(block1, 'CheckAction').text = action
        Et.SubElement(block1, 'SECCode').text = str(check.sec_code)

        if check.check_verify is True:
            verify_element = Et.SubElement(block1, 'VerifyInfo')
            Et.SubElement(verify_element, 'CheckVerify').text = 'Y' if check.check_verify else 'N'

        if check.check_type is not None:
            Et.SubElement(block1, 'CheckType').text = str(check.check_type)
        if check.data_entry_mode is not None:
            Et.SubElement(block1, 'DataEntryMode').text = str(check.data_entry_mode)
        if check.check_holder is not None:
            block1.append(_hydrate_consumer_info(check))

        return self._submit_transaction(transaction, client_transaction_id)

    def _submit_transaction(self, transaction, client_transaction_id=None):
        rsp = self.do_transaction(transaction, client_transaction_id)['Ver1.0']
        HpsGatewayResponseValidation.check_response(rsp, transaction.tag)

        response = HpsCheckResponse.from_dict(rsp)

        item = rsp['Transaction'][transaction.tag]
        if item['RspCode'] is None or item['RspCode'] != '0':
            raise HpsCheckException(
                rsp['Header']['GatewayTxnId'],
                response.details,
                item['RspCode'],
                item['RspMessage'])

        return response


class HpsGiftCardService(HpsSoapGatewayService):
    def __init__(self, config=None, enable_logging=False):
        HpsSoapGatewayService.__init__(self, config, enable_logging)

    def activate(self, amount, currency, gift_card):
        HpsInputValidation.check_amount(amount)
        HpsInputValidation.check_currency(currency)

        transaction = Et.Element('GiftCardActivate')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'Amt').text = str(amount)
        block1.append(_hydrate_gift_card_data(gift_card))

        return self._submit_transaction(transaction)

    def add_value(self, amount, currency, gift_card):
        HpsInputValidation.check_amount(amount)
        HpsInputValidation.check_currency(currency)

        transaction = Et.Element('GiftCardAddValue')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'Amt').text = str(amount)
        block1.append(_hydrate_gift_card_data(gift_card))

        return self._submit_transaction(transaction)

    def alias(self, action, gift_card, alias_str):
        transaction = Et.Element('GiftCardAlias')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Action').text = action
        Et.SubElement(block1, 'Alias').text = alias_str
        block1.append(_hydrate_gift_card_data(gift_card))

        return self._submit_transaction(transaction)

    def balance(self, gift_card):
        transaction = Et.Element('GiftCardBalance')
        block1 = Et.SubElement(transaction, 'Block1')
        block1.append(_hydrate_gift_card_data(gift_card))

        return self._submit_transaction(transaction)

    def deactivate(self, gift_card):
        transaction = Et.Element('GiftCardDeactivate')
        block1 = Et.SubElement(transaction, 'Block1')
        block1.append(_hydrate_gift_card_data(gift_card))

        return self._submit_transaction(transaction)

    def replace(self, old_gift_card, new_gift_card):
        transaction = Et.Element('GiftCardReplace')
        block1 = Et.SubElement(transaction, 'Block1')

        block1.append(
            _hydrate_gift_card_data(
                old_gift_card,
                'OldCardData'))
        block1.append(
            _hydrate_gift_card_data(
                new_gift_card,
                'NewCardData'))

        return self._submit_transaction(transaction)

    def reward(self, gift_card, amount, currency='usd',
               gratuity=None, tax=None):
        currency = currency.lower()
        HpsInputValidation.check_amount(amount)

        transaction = Et.Element('GiftCardReward')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(amount)
        block1.append(_hydrate_gift_card_data(gift_card))

        if currency == 'usd' or currency == 'points':
            currency_element = Et.SubElement(block1, 'Currency')
            if currency == 'usd':
                currency_element.text = 'USD'
            else:
                currency_element.text = 'POINTS'

        if gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(gratuity)

        if tax is not None:
            Et.SubElement(block1, 'TaxAmtInfo').text = str(tax)

        return self._submit_transaction(transaction)

    def sale(self, gift_card, amount, currency='usd', gratuity=None, tax=None):
        currency = currency.lower()
        HpsInputValidation.check_amount(amount)

        transaction = Et.Element('GiftCardSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(amount)
        block1.append(_hydrate_gift_card_data(gift_card))

        if currency == 'usd' or currency == 'points':
            currency_element = Et.SubElement(block1, 'Currency')
            if currency == 'usd':
                currency_element.text = 'USD'
            else:
                currency_element.text = 'POINTS'

        if gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(gratuity)

        if tax is not None:
            Et.SubElement(block1, 'TaxAmtInfo').text = str(tax)

        return self._submit_transaction(transaction)

    def void(self, transaction_id):
        trans = Et.Element('GiftCardVoid')
        block1 = Et.SubElement(trans, 'Block1')
        Et.SubElement(block1, 'GatewayTxnId').text = str(transaction_id)

        return self._submit_transaction(trans)

    def reverse(self, card_data, amount):
        HpsInputValidation.check_amount(amount)

        transaction = Et.Element('GiftCardReversal')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(amount)

        if isinstance(card_data, HpsGiftCard):
            block1.append(_hydrate_gift_card_data(card_data))
        else:
            Et.SubElement(block1, 'GatewayTxnId').text = str(card_data)

        return self._submit_transaction(transaction)

    def _submit_transaction(self, transaction):
        rsp = self.do_transaction(transaction)['Ver1.0']
        HpsGatewayResponseValidation.check_response(rsp, transaction.tag)

        HpsIssuerResponseValidation.check_response(
            rsp['Header']['GatewayTxnId'],
            rsp['Transaction'][transaction.tag]['RspCode'],
            rsp['Transaction'][transaction.tag]['RspText'])

        rvalue = None
        if transaction.tag == 'GiftCardActivate':
            rvalue = HpsGiftCardActivate.from_dict(rsp)
        elif transaction.tag == 'GiftCardAddValue':
            rvalue = HpsGiftCardAddValue.from_dict(rsp)
        elif transaction.tag == 'GiftCardAlias':
            rvalue = HpsGiftCardAlias.from_dict(rsp)
        elif transaction.tag == 'GiftCardBalance':
            rvalue = HpsGiftCardBalance.from_dict(rsp)
        elif transaction.tag == 'GiftCardDeactivate':
            rvalue = HpsGiftCardDeactivate.from_dict(rsp)
        elif transaction.tag == 'GiftCardReplace':
            rvalue = HpsGiftCardReplace.from_dict(rsp)
        elif transaction.tag == 'GiftCardReward':
            rvalue = HpsGiftCardReward.from_dict(rsp)
        elif transaction.tag == 'GiftCardSale':
            rvalue = HpsGiftCardSale.from_dict(rsp)
        elif transaction.tag == 'GiftCardVoid':
            rvalue = HpsGiftCardVoid.from_dict(rsp)
        elif transaction.tag == 'GiftCardReversal':
            rvalue = HpsGiftCardReversal.from_dict(rsp)

        return rvalue


class HpsPayPlanService(HpsRestGatewayService):
    def __init__(self, config=None, enable_logging=False):
        HpsRestGatewayService.__init__(self, config, enable_logging)

    """ Customers """

    def add_customer(self, customer):
        response = self.do_request('post', 'customers', customer.get_json_data())
        return self.hydrate_response(HpsPayPlanCustomer, response)

    def edit_customer(self, customer):
        response = self.do_request('put', 'customers/' + str(customer.customer_key), customer.get_json_data())
        return self.hydrate_response(HpsPayPlanCustomer, response)

    def find_all_customers(self, search_fields=None):
        if search_fields is None:
            search_fields = {}

        response = self.do_request('post', 'searchCustomers', search_fields)
        return self.hydrate_response(HpsPayPlanCustomerCollection, response)

    def get_customer(self, customer):
        customer_id = customer if not isinstance(customer, HpsPayPlanCustomer) else customer.customer_key
        response = self.do_request('get', 'customers/' + str(customer_id))
        return self.hydrate_response(HpsPayPlanCustomer, response)

    def delete_customer(self, customer, force_delete=False):
        customer_id = customer if not isinstance(customer, HpsPayPlanCustomer) else customer.customer_key
        response = self.do_request('delete', 'customers/' + str(customer_id), {'forceDelete': force_delete})
        time.sleep(1)
        return self.hydrate_response(HpsPayPlanCustomer, response)

    """ Payment Methods """

    def add_payment_method(self, payment_method):
        if payment_method.payment_method_type == HpsPayPlanPaymentMethodType.ACH:
            response = self._add_ach(payment_method)
        else:
            response = self._add_credit_card(payment_method)
        return self.hydrate_response(HpsPayPlanPaymentMethod, response)

    def edit_payment_method(self, payment_method):
        if payment_method.payment_method_type == HpsPayPlanPaymentMethodType.ACH:
            response = self._edit_ach(payment_method)
        else:
            response = self._edit_credit_card(payment_method)
        return self.hydrate_response(HpsPayPlanPaymentMethod, response)

    def find_all_payment_methods(self, search_fields=None):
        if search_fields is None:
            search_fields = {}

        response = self.do_request('post', 'searchPaymentMethods', search_fields)
        return self.hydrate_response(HpsPayPlanPaymentMethodCollection, response)

    def get_payment_method(self, payment_method):
        payment_method_id = payment_method
        if isinstance(payment_method, HpsPayPlanPaymentMethod):
            payment_method_id = payment_method.payment_method_key

        response = self.do_request('get', 'paymentMethods/' + payment_method_id)
        return self.hydrate_response(HpsPayPlanPaymentMethod, response)

    def delete_payment_method(self, payment_method, force_delete=False):
        payment_method_id = payment_method
        if isinstance(payment_method, HpsPayPlanPaymentMethod):
            payment_method_id = payment_method.payment_method_key

        response = self.do_request('delete', 'paymentMethods/' + payment_method_id, {'forceDelete': force_delete})
        time.sleep(1)
        return self.hydrate_response(HpsPayPlanPaymentMethod, response)

    def _add_credit_card(self, payment_method):
        data = payment_method.get_json_data()
        data['customerKey'] = payment_method.customer_key
        if hasattr(payment_method, 'account_number'):
            data['accountNumber'] = payment_method.account_number
        elif hasattr(payment_method, 'payment_token'):
            data['paymentToken'] = payment_method.payment_token
        return self.do_request('post', 'paymentMethodsCreditCard', data)

    def _edit_credit_card(self, payment_method):
        data = payment_method.get_json_data()
        return self.do_request('put', 'paymentMethodsCreditCard/' + payment_method.payment_method_key, data)

    def _add_ach(self, payment_method):
        data = payment_method.get_json_data()
        data['customerKey'] = payment_method.customer_key
        return self.do_request('post', 'paymentMethodsACH', data)

    def _edit_ach(self, payment_method):
        payment_method.account_type = None
        payment_method.ach_type = None
        payment_method.routing_number = None

        data = payment_method.get_json_data()
        return self.do_request('put', 'paymentMethodsACH/' + payment_method.payment_method_key, data)

    """ Schedules """

    def add_schedule(self, schedule):
        data = schedule.get_json_data()
        data['customerKey'] = schedule.customer_key
        data['numberOfPayments'] = schedule.number_of_payments

        response = self.do_request('post', 'schedules', data)
        return self.hydrate_response(HpsPayPlanSchedule, response)

    def edit_schedule(self, schedule):
        response = self.do_request('put', 'schedules/' + str(schedule.schedule_key), schedule.get_json_data())
        return self.hydrate_response(HpsPayPlanSchedule, response)

    def find_all_schedules(self, search_fields=None):
        if search_fields is None:
            search_fields = {}

        response = self.do_request('post', 'searchSchedules', search_fields)
        return self.hydrate_response(HpsPayPlanScheduleCollection, response)

    def get_schedule(self, schedule):
        schedule_id = schedule if not isinstance(schedule, HpsPayPlanSchedule) else schedule.schedule_key
        response = self.do_request('get', 'schedules/' + str(schedule_id))
        return self.hydrate_response(HpsPayPlanSchedule, response)

    def delete_schedule(self, schedule, force_delete=False):
        schedule_id = schedule if not isinstance(schedule, HpsPayPlanSchedule) else schedule.schedule_key
        response = self.do_request('delete', 'schedules/' + str(schedule_id), {'forceDelete': force_delete})
        time.sleep(1)
        return self.hydrate_response(HpsPayPlanSchedule, response)


class HpsActivationService(HpsRestGatewayService):
    def __init__(self, config=None, enable_logging=False):
        HpsRestGatewayService.__init__(self, config, enable_logging)

    def device_activation_key(self, merchant_id, activation_code):
        args = {
            'merchantId': merchant_id,
            'activationCode': activation_code
        }
        response = self.do_request('GET', 'deviceActivationKey?' + urllib.urlencode(args))
        return self.hydrate_response(DeviceActivationKeyResponse, response)


def _hydrate_gift_card_data(gift_card, element_name='CardData'):
    card_element = Et.Element(element_name)
    if gift_card.track_data is not None:
        Et.SubElement(card_element, 'TrackData').text = gift_card.track_data
    elif gift_card.card_number is not None:
        Et.SubElement(card_element, 'CardNbr').text = gift_card.card_number

    if gift_card.encryption_data is not None:
        data = gift_card.encryption_data
        enc_element = Et.SubElement(card_element, 'EncryptionData')
        Et.SubElement(enc_element, 'EncryptedTrackNumber').text = \
            data.encrypted_track_number
        Et.SubElement(enc_element, 'KSN').text = data.ksn
        Et.SubElement(enc_element, 'KTB').text = data.ktb
        Et.SubElement(enc_element, 'Version').text = data.version

    return card_element


def _hydrate_card_holder_data(card_holder):
    """Hydrate a new HPS card holder data type."""
    holder = Et.Element('CardHolderData')
    Et.SubElement(
        holder,
        'CardHolderFirstName').text = card_holder.first_name
    Et.SubElement(
        holder,
        'CardHolderLastName').text = card_holder.last_name
    if card_holder.email is not None:
        Et.SubElement(
            holder,
            'CardHolderEmail').text = card_holder.email
    if card_holder.phone is not None:
        Et.SubElement(
            holder,
            'CardHolderPhone').text = card_holder.phone
    Et.SubElement(
        holder,
        'CardHolderAddr').text = card_holder.address.address
    Et.SubElement(
        holder,
        'CardHolderCity').text = card_holder.address.city
    Et.SubElement(
        holder,
        'CardHolderState').text = card_holder.address.state
    Et.SubElement(
        holder,
        'CardHolderZip').text = card_holder.address.zip

    return holder


def _hydrate_card_manual_entry(card, card_present=False, reader_present=False):
    """Hydrate a new HPS manual entry card data type."""

    manual_entry = Et.Element('ManualEntry')
    Et.SubElement(manual_entry, 'CardNbr').text = card.number
    Et.SubElement(manual_entry, 'ExpMonth').text = str(card.exp_month)
    Et.SubElement(manual_entry, 'ExpYear').text = str(card.exp_year)
    if card.cvv is not None:
        cvv_element = Et.SubElement(manual_entry, 'CVV2')
        cvv_element.text = str(card.cvv)
    Et.SubElement(manual_entry, 'CardPresent').text = 'Y' if card_present else 'N'
    Et.SubElement(manual_entry, 'ReaderPresent').text = 'Y' if reader_present else 'N'

    return manual_entry


def _hydrate_token_data(token, card_present=False, reader_present=False):
    token_data = Et.Element('TokenData')
    Et.SubElement(token_data, 'TokenValue').text = token
    Et.SubElement(token_data, 'CardPresent').text = 'Y' if card_present else 'N'
    Et.SubElement(token_data, 'ReaderPresent').text = 'Y' if reader_present else 'N'

    return token_data


def _hydrate_additional_txn_fields(details):
    """Hydrate additional transaction fields."""

    if details is not None and isinstance(details, HpsTransactionDetails):
        addons = Et.Element('AdditionalTxnFields')

        if details.memo is not None:
            memo = Et.SubElement(addons, 'Description')
            memo.text = details.memo

        if details.customer_id is not None:
            customer_id = Et.SubElement(addons, "CustomerID")
            customer_id.text = details.customer_id

        if details.invoice_number is not None:
            invoice_number = Et.SubElement(addons, "InvoiceNbr")
            invoice_number.text = details.invoice_number

        return addons
    else:
        return None


def _hydrate_consumer_info(check):
    consumer_info = Et.Element('ConsumerInfo')
    if check.check_holder.address is not None:
        addr1 = Et.SubElement(consumer_info, 'Address1')
        addr1.text = check.check_holder.address.address

        city = Et.SubElement(consumer_info, 'City')
        city.text = check.check_holder.address.city

        state = Et.SubElement(consumer_info, 'State')
        state.text = check.check_holder.address.state

        _zip = Et.SubElement(consumer_info, 'Zip')
        _zip.text = check.check_holder.address.zip

    if check.check_holder.check_name is not None:
        check_name = Et.SubElement(consumer_info, 'CheckName')
        check_name.text = check.check_holder.check_name

    if check.check_holder.courtesy_card is not None:
        courtesy_card = Et.SubElement(consumer_info, 'CourtesyCard')
        courtesy_card.text = check.check_holder.courtesy_card

    if check.check_holder.dl_number is not None:
        dl_number = Et.SubElement(consumer_info, 'DLNumber')
        dl_number.text = check.check_holder.dl_number

    if check.check_holder.dl_state is not None:
        dl_state = Et.SubElement(consumer_info, 'DLState')
        dl_state.text = check.check_holder.dl_state

    if check.check_holder.email is not None:
        email = Et.SubElement(consumer_info, 'EmailAddress')
        email.text = check.check_holder.email

    if check.check_holder.first_name is not None:
        first_name = Et.SubElement(consumer_info, 'FirstName')
        first_name.text = check.check_holder.first_name

    if check.check_holder.last_name is not None:
        last_name = Et.SubElement(consumer_info, 'LastName')
        last_name.text = check.check_holder.last_name

    if check.check_holder.phone is not None:
        phone_number = Et.SubElement(consumer_info, 'PhoneNumber')
        phone_number.text = check.check_holder.phone

    if check.check_holder.ssnl4 is not None or check.check_holder.dob_year is not None:
        identity_element = Et.SubElement(consumer_info, 'IdentityInfo')

        if check.check_holder.ssnl4:
            Et.SubElement(identity_element, 'SSNL4').text = check.check_holder.ssl4

        if check.check_holder.dob_year:
            Et.SubElement(identity_element, 'DOBYear').text = check.check_holder.dob_year

    return consumer_info


def _hydrate_check_data(check):
    account_info = Et.Element('AccountInfo')
    if check.account_number is not None:
        acc_number = Et.SubElement(account_info, 'AccountNumber')
        acc_number.text = check.account_number
    if check.check_number is not None:
        check_number = Et.SubElement(account_info, 'CheckNumber')
        check_number.text = check.check_number
    if check.micr_number is not None:
        micr_data = Et.SubElement(account_info, 'MICRData')
        micr_data.text = check.micr_number
    if check.routing_number is not None:
        routing_number = Et.SubElement(account_info, 'RoutingNumber')
        routing_number.text = check.routing_number
    if check.account_type is not None:
        acc_type = Et.SubElement(account_info, 'AccountType')
        acc_type.text = str(check.account_type)

    return account_info


def _hydrate_direct_market_data(direct_market_data):
    if direct_market_data is not None and isinstance(direct_market_data, HpsDirectMarketData):
        market_data = Et.Element('DirectMktData')

        Et.SubElement(market_data, 'DirectMktInvoiceNbr').text = direct_market_data.invoice_number
        Et.SubElement(market_data, 'DirectMktShipDay').text = str(direct_market_data.ship_day)
        Et.SubElement(market_data, 'DirectMktShipMonth').text = str(direct_market_data.ship_month)

        return market_data
    else:
        return None


def _hydrate_cpc_data(cpc_data):
    if cpc_data is not None and isinstance(cpc_data, HpsCPCData):
        cpc_element = Et.Element('CPCData')

        if cpc_data.card_holder_po_number is not None:
            Et.SubElement(cpc_element, 'CardHolderPONbr').text = cpc_data.card_holder_po_number
        if cpc_data.tax_amount is not None:
            Et.SubElement(cpc_element, 'TaxAmt').text = str(cpc_data.tax_amount)
        Et.SubElement(cpc_element, 'TaxType').text = str(cpc_data.tax_type)

        return cpc_element
    else:
        return None


def _hydrate_track_data(track_data):
    if track_data is not None and isinstance(track_data, HpsTrackData):
        track_data_element = Et.Element('TrackData')
        track_data_element.text = track_data.value
        track_data_element.set('method', track_data.method)

        return track_data_element
    else:
        return None


def _hydrate_encryption_data(encryption_data):
    if encryption_data is not None and isinstance(encryption_data, HpsEncryptionData):
        enc_data_element = Et.Element('EncryptionData')
        Et.SubElement(enc_data_element, 'Version').text = encryption_data.version
        if encryption_data.encrypted_track_number is not None:
            Et.SubElement(enc_data_element, 'EncryptedTrackNumber').text = str(encryption_data.encrypted_track_number)
        if encryption_data.ktb is not None:
            Et.SubElement(enc_data_element, 'KTB').text = encryption_data.ktb
        if encryption_data.ksn is not None:
            Et.SubElement(enc_data_element, 'KSN').text = encryption_data.ksn

        return enc_data_element
    else:
        return None


def _get_client_txn_id(details=None):
    client_txn_id = None
    if details is not None:
        client_txn_id = details.client_transaction_id
    return client_txn_id
