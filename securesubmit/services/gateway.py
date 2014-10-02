"""
    gateway.py

    Defines the gateway services for the HPS Portico Gateway.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

import traceback
import urllib2
import xml.etree.cElementTree as Et
import xmltodict as xmltodict
from securesubmit.infrastructure import *
from securesubmit.entities.credit import *
from securesubmit.entities.batch import *
from securesubmit.entities.check import *
from securesubmit.entities.gift import *


class HpsGatewayService(object):
    _config = None
    _base_config = None
    _url = None

    def __init__(self, config=None):
        self._base_config = HpsConfiguration()
        self._config = config

        self._url = self._base_config.soap_service_uri
        if self._config is not None:
            self._url = self._config.soap_service_uri

        secret_api_key = self._base_config.secret_api_key
        if self._config is not None:
            secret_api_key = self._config.secret_api_key

        if secret_api_key is not None and secret_api_key != "":
            if "_uat_" in secret_api_key:
                self._url = ("https://posgateway.uat.secureexchange.net/"
                             "Hps.Exchange.PosGateway/"
                             "PosGatewayService.asmx?wsdl")
            elif "_cert_" in secret_api_key:
                self._url = ("https://posgateway.cert.secureexchange.net/"
                             "Hps.Exchange.PosGateway/"
                             "PosGatewayService.asmx?wsdl")
            else:
                self._url = ("https://posgateway.secureexchange.net/"
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
                ('The HPS SDK has not been properly configured. '
                 'Please make sure to initialize the config either '
                 'in a service constructor or in your App.config '
                 'or Web.config file.'))
        try:
            # Envelope
            envelope = Et.Element("soap:Envelope")
            envelope.set("xmlns:soap",
                         "http://schemas.xmlsoap.org/soap/envelope/")
            envelope.set("xmlns:xsi",
                         "http://www.w3.org/2001/XMLSchema-instance")
            envelope.set("xmlns:xsd",
                         "http://www.w3.org/2001/XMLSchema")
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
                api_key.text = secret_api_key
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
            request_headers = {'Content-type': 'text/xml; charset=UTF-8',
                               'Content-length': str(len(xml)),
                               'Host': 'posgateway.cert.secureexchange.net'}
            request = urllib2.Request(self._url, xml, request_headers)
            raw_response = urllib2.urlopen(request).read()

            namespaces = {"http://Hps.Exchange.PosGateway": None,
                          "http://schemas.xmlsoap.org/soap/envelope/": None}

            response = xmltodict.parse(raw_response,
                                       process_namespaces=True,
                                       namespaces=namespaces)

            if ('Envelope' in response and
                    'Body' in response['Envelope'] and
                    'PosResponse' in response['Envelope']['Body']):
                return response['Envelope']['Body']['PosResponse']
            else:
                raise HpsException("Unexpected response")
        except Exception, e:
            traceback.print_exc()
            raise HpsGatewayException(
                HpsExceptionCodes.unknown_gateway_error,
                'Unable to process transaction', None, None, e)

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


class HpsCreditService(HpsGatewayService):
    _filter_by = None

    def __init__(self, config=None):
        HpsGatewayService.__init__(self, config)

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
               details=None):
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
            card_data_element.append(
                _hydrate_card_manual_entry(card_data))
        else:
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = card_data

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

        # Submit the transaction
        client_txn_id = _get_client_txn_id(details)
        return self._submit_transaction(transaction, client_txn_id)

    def verify(self, card_data,
               card_holder=None,
               request_multi_use_token=False,
               client_transaction_id=None):
        # Build the transaction request.
        transaction = Et.Element('CreditAccountVerify')
        block1 = Et.SubElement(transaction, 'Block1')

        # Add Card Holder
        if card_holder is not None:
            block1.append(_hydrate_card_holder_data(card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if isinstance(card_data, HpsCreditCard):
            card_data_element.append(
                _hydrate_card_manual_entry(card_data))
        else:
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = card_data

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
                  details=None):
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

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if isinstance(card_data, HpsCreditCard):
            card_data_element.append(
                _hydrate_card_manual_entry(card_data))
        else:
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = card_data

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

    def capture(self, transaction_id,
                amount=None,
                gratuity=None,
                client_transaction_id=None):
        # Build the transaction request.
        transaction = Et.Element('CreditAddToBatch')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(transaction_id)
        if amount is not None:
            Et.SubElement(transaction, 'Amt').text = str(amount)

        # Add Gratuity
        if gratuity is not None:
            Et.SubElement(transaction, 'GratuityAmtInfo').text = str(gratuity)

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

    def _submit_transaction(self, transaction, client_transaction_id=None):
        rsp = self.do_transaction(transaction, client_transaction_id)['Ver1.0']

        amount = None
        if transaction.tag == 'CreditSale' or \
                transaction.tag == 'CreditAuth':
            amount = transaction.iter('Amt').next().text

        self._process_charge_gateway_response(
            rsp, transaction.tag, amount, 'usd')

        self._process_charge_issuer_response(
            rsp, transaction.tag, amount, 'usd')

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

        return rvalue

    def _process_charge_issuer_response(self, response, expected_type, *args):
        transaction_id = response['Header']['GatewayTxnId']
        transaction = response['Transaction'][expected_type]

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
                            ('Error occurred while reversing ',
                             'a charge due to HPS issuer time-out.'),
                            e)
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


class HpsBatchService(HpsGatewayService):
    def __init__(self, config=None):
        HpsGatewayService.__init__(self, config)

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


class HpsCheckService(HpsGatewayService):
    def __init__(self, config):
        HpsGatewayService.__init__(self, config)

    def sale(self, action, check, amount):
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

        account_info = Et.SubElement(block1, 'AccountInfo')
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
            acc_type.text = check.account_type

        Et.SubElement(block1, 'CheckAction').text = action
        Et.SubElement(block1, 'SECCode').text = check.sec_code

        if check.check_type is not None:
            Et.SubElement(block1, 'CheckType').text = check.check_type
        if check.data_entry_mode is not None:
            Et.SubElement(block1, 'DataEntryMode').text = check.data_entry_mode

        if check.check_holder is not None:
            consumer_info = Et.SubElement(block1, 'ConsumerInfo')
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

        # rsp = self.do_transaction(transaction)['Ver1.0']
        return self._submit_transaction(transaction)

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

    def _submit_transaction(self, transaction):
        rsp = self.do_transaction(transaction)['Ver1.0']
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


class HpsGiftCardService(HpsGatewayService):
    def __init__(self, config=None):
        HpsGatewayService.__init__(self, config)

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


def _hydrate_gift_card_data(gift_card, element_name='CardData'):
    card_element = Et.Element(element_name)
    if gift_card.is_track_data is True:
        Et.SubElement(card_element, 'TrackData').text = gift_card.number
    else:
        Et.SubElement(card_element, 'CardNbr').text = gift_card.number

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


def _hydrate_card_manual_entry(card):
    """Hydrate a new HPS manual entry card data type."""

    manual_entry = Et.Element('ManualEntry')
    Et.SubElement(manual_entry, 'CardNbr').text = card.number
    Et.SubElement(manual_entry, 'ExpMonth').text = str(card.exp_month)
    Et.SubElement(manual_entry, 'ExpYear').text = str(card.exp_year)
    if card.cvv is not None:
        cvv_element = Et.SubElement(manual_entry, 'CVV2')
        cvv_element.text = str(card.cvv)
    Et.SubElement(manual_entry, 'CardPresent').text = "N"
    Et.SubElement(manual_entry, 'ReaderPresent').text = "N"

    return manual_entry


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


def _get_client_txn_id(details=None):
    client_txn_id = None
    if details is not None:
        client_txn_id = details.client_transaction_id
    return client_txn_id
