import xml.etree.cElementTree as Et

from securesubmit.entities import HpsTransaction
from securesubmit.entities.check import HpsCheckResponse
from securesubmit.entities.credit import HpsReportTransactionDetails, HpsReportTransactionSummary, HpsCharge, \
    HpsAccountVerify, HpsAuthorization, HpsRefund, HpsReversal, HpsVoid, HpsCPCEdit, HpsRecurringBilling, \
    HpsOfflineAuthorization
from securesubmit.entities.debit import HpsDebitAuthorization
from securesubmit.entities.etb import HpsEbtAuthorization
from securesubmit.entities.gift import HpsGiftCardActivate, HpsGiftCardAddValue, HpsGiftCardAlias, HpsGiftCardBalance, \
    HpsGiftCardDeactivate, HpsGiftCardReplace, HpsGiftCardReward, HpsGiftCardSale, HpsGiftCardVoid, HpsGiftCardReversal
from securesubmit.entities.payplan import HpsPayPlanSchedule
from securesubmit.infrastructure import HpsArgumentException, HpsGatewayException, HpsCreditException, \
    HpsInvalidRequestException, HpsCheckException
from securesubmit.infrastructure.enums import HpsExceptionCodes
from securesubmit.infrastructure.validation import HpsIssuerResponseValidation, HpsGatewayResponseValidation, \
    HpsInputValidation
from securesubmit.services.fluent import HpsBuilderAbstract
from securesubmit.services.gateway import HpsSoapGatewayService


"""
    HpsFluentCreditService
"""


class HpsFluentCreditService(HpsSoapGatewayService):
    _filter_by = None

    def __init__(self, config=None):
        HpsSoapGatewayService.__init__(self, config, True)

    def with_config(self, config):
        self.services_config = config
        return self

    def authorize(self, amount=None):
        return HpsCreditServiceAuthorizeBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def additional_auth(self, amount=None):
        return HpsCreditServiceAdditionalAuthBuilder(self)\
            .with_amount(amount)

    def capture(self, transaction_id=None):
        return HpsCreditServiceCaptureBuilder(self).with_transaction_id(transaction_id)

    def charge(self, amount=None):
        return HpsCreditServiceChargeBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def cpc_edit(self, transaction_id=None):
        return HpsCreditServiceCpcEditBuilder(self).with_transaction_id(transaction_id)

    def edit(self, transaction_id=None):
        return HpsCreditServiceEditBuilder(self).with_transaction_id(transaction_id)

    def get(self, transaction_id):
        return HpsCreditServiceGetBuilder(self).with_transaction_id(transaction_id)

    def list(self):
        return HpsCreditServiceListBuilder(self)

    def offline_auth(self, amount=None):
        return HpsCreditServiceOfflineAuthBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def offline_charge(self, amount=None):
        return HpsCreditServiceOfflineChargeBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def recurring(self, amount=None):
        return HpsCreditServiceRecurringBuilder(self)\
            .with_amount(amount)

    def refund(self, amount=None):
        return HpsCreditServiceRefundBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def reverse(self, amount=None):
        return HpsCreditServiceReverseBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def verify(self):
        return HpsCreditServiceVerifyBuilder(self)

    def void(self, transaction_id=None):
        return HpsCreditServiceVoidBuilder(self)\
            .with_transaction_id(transaction_id)

    def prepaid_balance_inquiry(self):
        return HpsCreditServiceBalanceInquiryBuilder(self)

    def prepaid_add_value(self, amount=None):
        return HpsCreditServiceAddValueBuilder(self).with_amount(amount)

    def submit_transaction(self, transaction, client_transaction_id=None):
        rsp = self.do_transaction(transaction, client_transaction_id)['Ver1.0']

        amount = None
        if transaction.tag == 'CreditSale' or \
                transaction.tag == 'CreditAuth':
            amount = transaction.iter('Amt').next().text

        self.process_charge_gateway_response(rsp, transaction.tag, amount, 'usd')

        self.process_charge_issuer_response(rsp, transaction.tag, amount, 'usd')

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
        elif transaction.tag == 'PrePaidBalanceInquiry':
            rvalue = HpsAuthorization.from_dict(rsp)
        elif transaction.tag == 'PrePaidAddValue':
            rvalue = HpsAuthorization.from_dict(rsp)
        elif transaction.tag in ['CreditOfflineAuth', 'CreditOfflineSale']:
            rvalue = HpsOfflineAuthorization.from_dict(rsp)

        return rvalue

    def process_charge_issuer_response(self, response, expected_type, *args):
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
                        # self.reverse(int(transaction_id), *args)
                        self.reverse().with_transaction_id(int(transaction_id), *args)
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

    def process_charge_gateway_response(self, response, expected_type, *args):
        response_code = response['Header']['GatewayRspCode']
        if response_code == 0:
            return
        if response_code == 30:
            try:
                # self.reverse(response['Header']['GatewayTxnId'], *args)
                self.reverse().with_transaction_id(response['Header']['GatewayTxnId'], *args)
            except Exception, e:
                raise HpsGatewayException(
                    HpsExceptionCodes.gateway_timeout_reversal_error,
                    'Error occurred while reversing a charge due to HPS gateway time-out.',
                    e)
        HpsGatewayResponseValidation.check_response(response, expected_type)


class HpsCreditServiceAddValueBuilder(HpsBuilderAbstract):
    _amount = None
    _allow_duplicates = False
    _card = None
    _track_data = None
    _token = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('PrePaidAddValue')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'

        card_data = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data.append(self._service.hydrate_card_manual_entry(self._card))

        if self._track_data is not None:
            card_data.append(self._service.hydrate_track_data(self._track_data))

        if self._token is not None:
            card_data.append(self._service.hydrate_token_data(self._token))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Balance Inquiry can only use one payment method')
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Add value needs an amount.')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._track_data is not None:
            payment_methods += 1

        return payment_methods == 1

    def amount_is_not_none(self):
        return self._amount is not None


class HpsCreditServiceAdditionalAuthBuilder(HpsBuilderAbstract):
    _amount = None
    _transaction_id = None
    _allow_duplicates = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)
        HpsInputValidation.check_amount(self._amount)

        transaction = Et.Element('CreditAdditionalAuth')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)
        Et.SubElement(block1, 'Amt').text = str(self._amount)

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Credit additional auth needs an amount')

    def amount_not_none(self):
        return self._amount is not None


class HpsCreditServiceAuthorizeBuilder(HpsBuilderAbstract):
    _amount = None
    _currency = None
    _card = None
    _token = None
    _track_data = None
    _card_holder = None
    _request_multi_use_token = False
    _details = None
    _txn_descriptor = None
    _allow_partial_auth = False
    _cpc_req = False
    _allow_duplicates = False
    _payment_data = None
    _card_present = False
    _reader_present = False
    _gratuity = None
    _auto_substantiation = None
    _original_txn_reference_data = None
    _payment_data_source = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditAuth')
        block1 = Et.SubElement(transaction, 'Block1')

        allow_dup = Et.SubElement(block1, 'AllowDup')
        allow_dup.text = 'Y' if self._allow_duplicates is True else 'N'

        partial_auth = Et.SubElement(block1, 'AllowPartialAuth')
        partial_auth.text = 'Y' if self._allow_partial_auth is True else 'N'

        Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(self._gratuity)

        # Add Card Holder
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        elif self._token is not None:
            card_data_element.append(self._service.hydrate_token_data(
                self._token,
                self._card_present,
                self._reader_present
            ))
        elif self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        elif self._payment_data is not None:
            manual_entry = Et.Element('ManualEntry')
            Et.SubElement(manual_entry, 'CardNbr').text = self._payment_data.application_primary_account_number
            exp_date = str(self._payment_data.application_expiration_date)
            Et.SubElement(manual_entry, 'ExpMonth').text = exp_date[2:4]
            Et.SubElement(manual_entry, 'ExpYear').text = '20' + exp_date[0:2]
            card_data_element.append(manual_entry)

            block1.append(self._service.hydrate_secure_ecommerce(self._payment_data_source,
                                                                 self._payment_data.payment_data))

        # CPC request
        if self._cpc_req is True:
            Et.SubElement(block1, 'CPCReq').text = 'Y'

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        token_request.text = 'Y' if self._request_multi_use_token is True else 'N'

        # Handle the AdditionalTxnFields
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        if self._txn_descriptor is not None:
            Et.SubElement(block1, 'TxnDescriptor').text = self._txn_descriptor

        # Auto substantiation
        if self._auto_substantiation is not None:
            block1.append(self._service.hydrate_auto_substantiation(self._auto_substantiation))

        # Offline data
        if self._original_txn_reference_data is not None:
            ref_element = Et.SubElement(block1, 'OrigTxnRefData')
            Et.SubElement(ref_element, 'AuthCode').text = self._original_txn_reference_data.authorization_code
            Et.SubElement(ref_element, 'CardNbrLastFour').text = self._original_txn_reference_data.card_number_last_4

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Authorize can only use one payment method')
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Authorize needs an amount')
        self.add_validation(self.currency_not_none, HpsArgumentException, 'Authorize needs a currency')
        self.add_validation(self.payment_data_source_not_none,
                            HpsArgumentException, 'PaymentDataSource required with payment data')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._payment_data is not None:
            payment_methods += 1
        if self._track_data is not None:
            payment_methods += 1

        return payment_methods == 1

    def amount_not_none(self):
        return self._amount is not None

    def currency_not_none(self):
        return self._currency is not None

    def payment_data_source_not_none(self):
        return self._payment_data is not None or self._payment_data_source is None


class HpsCreditServiceBalanceInquiryBuilder(HpsBuilderAbstract):
    _card = None
    _card_holder = None
    _track_data = None
    _token = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('PrePaidBalanceInquiry')
        block1 = Et.SubElement(transaction, 'Block1')

        card_data = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data.append(self._service.hydrate_card_manual_entry(self._card))

        if self._track_data is not None:
            card_data.append(self._service.hydrate_track_data(self._track_data))

        if self._token is not None:
            card_data.append(self._service.hydrate_token_data(self._token))

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Balance Inquiry can only use one payment method')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._track_data is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsCreditServiceCaptureBuilder(HpsBuilderAbstract):
    _transaction_id = None
    _amount = None
    _gratuity = None
    _client_transaction_id = None
    _direct_market_data = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditAddToBatch')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(self._transaction_id)
        if self._amount is not None:
            Et.SubElement(transaction, 'Amt').text = str(self._amount)

        # Add Gratuity
        if self._gratuity is not None:
            Et.SubElement(transaction, 'GratuityAmtInfo').text = str(self._gratuity)

        # Direct market data
        if self._direct_market_data is not None:
            transaction.append(self._service.hydrate_direct_market_data(self._direct_market_data))

        # Submit the transaction
        rsp = self._service.do_transaction(transaction, self._client_transaction_id)["Ver1.0"]
        self._service.process_charge_gateway_response(rsp, transaction.tag)

        return self._service.get(self._transaction_id).execute()

    def _setup_validations(self):
        self.add_validation(
            self.transaction_id_is_not_none,
            HpsArgumentException,
            'Capture needs a trasaction id'
        )

    def transaction_id_is_not_none(self):
        return self._transaction_id is not None


class HpsCreditServiceChargeBuilder(HpsBuilderAbstract):
    _amount = None
    _currency = None
    _card = None
    _token = None
    _track_data = None
    _card_holder = None
    _request_multi_use_token = False
    _details = None
    _txn_descriptor = None
    _allow_partial_auth = False
    _cpc_req = False
    _direct_market_data = None
    _allow_duplicates = False
    _payment_data = None
    _card_present = None
    _reader_present = None
    _gratuity = None
    _original_txn_reference_data = None
    _payment_data_source = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        # Built the transaction request
        transaction = Et.Element('CreditSale')
        block1 = Et.SubElement(transaction, 'Block1')

        allow_dup = Et.SubElement(block1, 'AllowDup')
        allow_dup.text = 'Y' if self._allow_duplicates is True else 'N'

        partial_auth = Et.SubElement(block1, 'AllowPartialAuth')
        partial_auth.text = 'Y' if self._allow_partial_auth is True else 'N'

        Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(self._gratuity)

        # Add Card Holder
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        elif self._token is not None:
            card_data_element.append(self._service.hydrate_token_data(
                self._token,
                self._card_present,
                self._reader_present
            ))
        elif self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        elif self._payment_data is not None:
            manual_entry = Et.Element('ManualEntry')
            Et.SubElement(manual_entry, 'CardNbr').text = self._payment_data.application_primary_account_number
            exp_date = str(self._payment_data.application_expiration_date)
            Et.SubElement(manual_entry, 'ExpMonth').text = exp_date[2:4]
            Et.SubElement(manual_entry, 'ExpYear').text = '20' + exp_date[0:2]
            card_data_element.append(manual_entry)

            block1.append(self._service.hydrate_secure_ecommerce(self._payment_data_source,
                                                                 self._payment_data.payment_data))

        # CPC request
        if self._cpc_req is True:
            Et.SubElement(block1, 'CPCReq').text = 'Y'

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        token_request.text = 'Y' if self._request_multi_use_token is True else 'N'

        # Handle the AdditionalTxnFields
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        if self._txn_descriptor is not None:
            Et.SubElement(block1, "TxnDescriptor").text = self._txn_descriptor

        if self._direct_market_data is not None:
            block1.append(self._service.hydrate_direct_market_data(self._direct_market_data))

        # Offline data
        if self._original_txn_reference_data is not None:
            ref_element = Et.SubElement(block1, 'OrigTxnRefData')
            Et.SubElement(ref_element, 'AuthCode').text = self._original_txn_reference_data.authorization_code
            Et.SubElement(ref_element, 'CardNbrLastFour').text = self._original_txn_reference_data.card_number_last_4

        # Submit the transaction
        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Authorize can only use one payment method')
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Authorize needs an amount')
        self.add_validation(self.currency_not_none, HpsArgumentException, 'Authorize needs a currency')
        self.add_validation(self.payment_data_source_not_none,
                            HpsArgumentException, 'PaymentDataSource required with payment data')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._payment_data is not None:
            payment_methods += 1
        if self._track_data is not None:
            payment_methods += 1

        return payment_methods == 1

    def amount_not_none(self):
        return self._amount is not None

    def currency_not_none(self):
        return self._currency is not None

    def payment_data_source_not_none(self):
        return self._payment_data is not None or self._payment_data_source is None


class HpsCreditServiceCpcEditBuilder(HpsBuilderAbstract):
    _transaction_id = None
    _cpc_data = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditCPCEdit')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(self._transaction_id)
        transaction.append(self._service.hydrate_cpc_data(self._cpc_data))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.transaction_id_is_not_none, HpsArgumentException, 'CpcEdit needs a transaction id.')
        self.add_validation(self.cpc_data_is_not_none, HpsArgumentException, 'CpcEdit needs cpc data.')

    def transaction_id_is_not_none(self):
        return self._transaction_id is not None

    def cpc_data_is_not_none(self):
        return self._cpc_data is not None


class HpsCreditServiceEditBuilder(HpsBuilderAbstract):
    _transaction_id = None
    _amount = None
    _gratuity = None
    _client_transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditTxnEdit')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(self._transaction_id)

        if self._amount is not None:
            Et.SubElement(transaction, 'Amt').text = str(self._amount)

        # Add Gratuity
        if self._gratuity is not None:
            Et.SubElement(transaction, 'GratuityAmtInfo').text = str(self._gratuity)

        # Submit the transaction
        trans = self._service.submit_transaction(transaction, self._client_transaction_id)
        trans.response_code = '00'
        trans.response_text = ''

        return trans

    def _setup_validations(self):
        self.add_validation(self.transaction_id_is_not_none, HpsArgumentException, 'Get needs a transaction id.')

    def transaction_id_is_not_none(self):
        return self._transaction_id is not None


class HpsCreditServiceGetBuilder(HpsBuilderAbstract):
    _transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element("ReportTxnDetail")
        Et.SubElement(transaction, "TxnId").text = str(self._transaction_id)

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.transaction_id_is_not_none, HpsArgumentException, 'Get needs a transaction id.')

    def transaction_id_is_not_none(self):
        return self._transaction_id is not None


class HpsCreditServiceListBuilder(HpsBuilderAbstract):
    _utc_start_date = None
    _utc_end_date = None
    _filter_by = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_date_not_future(self._utc_start_date)
        HpsInputValidation.check_date_not_future(self._utc_end_date)
        self._service._filter_by = self._filter_by

        transaction = Et.Element("ReportActivity")

        if self._utc_start_date is not None:
            start = Et.SubElement(transaction, "RptStartUtcDT")
            start.text = self._utc_start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if self._utc_end_date is not None:
            end = Et.SubElement(transaction, "RptEndUtcDT")
            end.text = self._utc_end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.start_date_is_not_none, HpsArgumentException, 'ListTransactions needs a start date.')
        self.add_validation(self.end_date_is_not_none, HpsArgumentException, 'ListTransactions needs a end date.')

    def start_date_is_not_none(self):
        return self._utc_start_date is not None

    def end_date_is_not_none(self):
        return self._utc_end_date is not None


class HpsCreditServiceOfflineAuthBuilder(HpsBuilderAbstract):
    _amount = None
    _card = None
    _token = None
    _track_data = None
    _card_holder = None
    _request_multi_use_token = False
    _details = None
    _txn_descriptor = None
    _cpc_req = False
    _direct_market_data = None
    _allow_duplicates = False
    _payment_data = None
    _card_present = False
    _reader_present = False
    _gratuity = None
    _auto_substantiation = None
    _offline_auth_code = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditOfflineAuth')
        block1 = Et.SubElement(transaction, 'Block1')

        allow_dup = Et.SubElement(block1, 'AllowDup')
        allow_dup.text = 'Y' if self._allow_duplicates is True else 'N'

        Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(self._gratuity)

        # Add Card Holder
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        elif self._token is not None:
            card_data_element.append(self._service.hydrate_token_data(
                self._token,
                self._card_present,
                self._reader_present
            ))
        elif self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        elif self._payment_data is not None:
            manual_entry = Et.Element('ManualEntry')
            Et.SubElement(manual_entry, 'CardNbr').text = self._payment_data.application_primary_account_number
            exp_date = str(self._payment_data.application_expiration_date)
            Et.SubElement(manual_entry, 'ExpMonth').text = exp_date[2:4]
            Et.SubElement(manual_entry, 'ExpYear').text = '20' + exp_date[0:2]
            card_data_element.append(manual_entry)

            block1.append(self._service.hydrate_secure_ecommerce(self._payment_data.payment_data))

        # CPC request
        if self._cpc_req is True:
            Et.SubElement(block1, 'CPCReq').text = 'Y'

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        token_request.text = 'Y' if self._request_multi_use_token is True else 'N'

        # Handle the AdditionalTxnFields
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        if self._txn_descriptor is not None:
            Et.SubElement(block1, 'TxnDescriptor').text = self._txn_descriptor

        # Auto substantiation
        if self._auto_substantiation is not None:
            block1.append(self._service.hydrate_auto_substantiation(self._auto_substantiation))

        if self._offline_auth_code is not None:
            Et.SubElement(block1, 'OfflineAuthCode').text = self._offline_auth_code

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Authorize can only use one payment method')
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Authorize needs an amount')
        self.add_validation(
            self.offline_auth_code_not_none,
            HpsArgumentException,
            'Offline Auth needs offline auth code')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._payment_data is not None:
            payment_methods += 1
        if self._track_data is not None:
            payment_methods += 1

        return payment_methods == 1

    def amount_not_none(self):
        return self._amount is not None

    def offline_auth_code_not_none(self):
        return self._offline_auth_code is not None


class HpsCreditServiceOfflineChargeBuilder(HpsCreditServiceOfflineAuthBuilder):
    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditOfflineSale')
        block1 = Et.SubElement(transaction, 'Block1')

        allow_dup = Et.SubElement(block1, 'AllowDup')
        allow_dup.text = 'Y' if self._allow_duplicates is True else 'N'

        Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(self._gratuity)

        # Add Card Holder
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        elif self._token is not None:
            card_data_element.append(self._service.hydrate_token_data(
                self._token,
                self._card_present,
                self._reader_present
            ))
        elif self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        elif self._payment_data is not None:
            manual_entry = Et.Element('ManualEntry')
            Et.SubElement(manual_entry, 'CardNbr').text = self._payment_data.application_primary_account_number
            exp_date = str(self._payment_data.application_expiration_date)
            Et.SubElement(manual_entry, 'ExpMonth').text = exp_date[2:4]
            Et.SubElement(manual_entry, 'ExpYear').text = '20' + exp_date[0:2]
            card_data_element.append(manual_entry)

            block1.append(self._service.hydrate_secure_ecommerce(self._payment_data.payment_data))

        # CPC request
        if self._cpc_req is True:
            Et.SubElement(block1, 'CPCReq').text = 'Y'

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        token_request.text = 'Y' if self._request_multi_use_token is True else 'N'

        # Handle the AdditionalTxnFields
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        if self._txn_descriptor is not None:
            Et.SubElement(block1, 'TxnDescriptor').text = self._txn_descriptor

        # Auto substantiation
        if self._auto_substantiation is not None:
            block1.append(self._service.hydrate_auto_substantiation(self._auto_substantiation))

        if self._offline_auth_code is not None:
            Et.SubElement(block1, 'OfflineAuthCode').text = self._offline_auth_code

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)


class HpsCreditServiceRecurringBuilder(HpsBuilderAbstract):
    _schedule = None
    _amount = None
    _card = None
    _token = None
    _payment_method_key = None
    _one_time = False
    _card_holder = None
    _details = None
    _allow_duplicates = False

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('RecurringBilling')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        if self._card is not None:
            card_data = Et.SubElement(block1, 'CardData')
            card_data.append(self._service.hydrate_card_manual_entry(self._card))

        if self._token is not None:
            card_data = Et.SubElement(block1, 'CardData')
            token_data = Et.SubElement(card_data, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = self._token

        if self._payment_method_key is not None:
            Et.SubElement(block1, 'PaymentMethodKey').text = self._payment_method_key

        schedule_id = self._schedule
        if isinstance(self._schedule, HpsPayPlanSchedule):
            schedule_id = self._schedule.schedule_identifier

        recurring_data = Et.SubElement(block1, 'RecurringData')
        Et.SubElement(recurring_data, 'ScheduleID').text = str(schedule_id)
        Et.SubElement(recurring_data, 'OneTime').text = 'Y' if self._one_time else 'N'

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Recurring can only use one payment method')
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Recurring needs an amount')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._payment_method_key is not None:
            payment_methods += 1

        return payment_methods == 1

    def amount_not_none(self):
        return self._amount is not None


class HpsCreditServiceRefundBuilder(HpsBuilderAbstract):
    _amount = None
    _currency = None
    _card = None
    _token = None
    _transaction_id = None
    _card_holder = None
    _details = None
    _allow_duplicates = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)
        HpsInputValidation.check_currency(self._currency)

        # Build the transaction request
        transaction = Et.Element('CreditReturn')
        block1 = Et.SubElement(transaction, 'Block1')

        allow_dup = Et.SubElement(block1, 'AllowDup')
        allow_dup.text = "Y" if self._allow_duplicates is True else 'N'

        Et.SubElement(block1, 'Amt').text = str(self._amount)

        # Add Card Holder
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        # Card Data
        if self._card is not None:
            card_data_element = Et.SubElement(block1, 'CardData')
            card_data_element.append(self._service.hydrate_card_manual_entry(self._card))
        elif self._token is not None:
            card_data_element = Et.SubElement(block1, 'CardData')
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = self._token
        elif self._transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)

        # Additional Txn
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Refund can only use one payment method')
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Refund needs an amount')
        self.add_validation(self.currency_not_none, HpsArgumentException, 'Refund needs a currency')

    def only_one_payment_method(self):
        if self._card is not None and (self._token is not None or self._transaction_id is not None):
            return False
        elif self._token is not None and (self._card is not None or self._transaction_id is not None):
            return False
        elif self._transaction_id is not None and (self._card is not None or self._token is not None):
            return False
        elif self._card is None and self._token is None and self._transaction_id is None:
            return False

        return True

    def amount_not_none(self):
        return self._amount is not None

    def currency_not_none(self):
        return self._currency is not None


class HpsCreditServiceReverseBuilder(HpsBuilderAbstract):
    _amount = None
    _auth_amount = None
    _currency = None
    _card = None
    _token = None
    _transaction_id = None
    _details = None
    _allow_duplicates = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)
        HpsInputValidation.check_currency(self._currency)

        # Build the transaction request
        transaction = Et.Element('CreditReversal')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._auth_amount is not None:
            Et.SubElement(block1, 'AuthAmt').text = str(self._auth_amount)

        # Card Data
        if self._card is not None:
            card_data_element = Et.SubElement(block1, 'CardData')
            card_data_element.append(self._service.hydrate_card_manual_entry(self._card))
        elif self._token is not None:
            card_data_element = Et.SubElement(block1, 'CardData')
            token_data = Et.SubElement(card_data_element, 'TokenData')
            Et.SubElement(token_data, 'TokenValue').text = self._token
        elif self._transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)

        # Additional Txn
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Refund can only use one payment method')
        self.add_validation(self.amount_not_none, HpsArgumentException, 'Reverse needs an amount')
        self.add_validation(self.currency_not_none, HpsArgumentException, 'Reverse needs a currency')

    def only_one_payment_method(self):
        if self._card is not None and (self._token is not None or self._transaction_id is not None):
            return False
        elif self._token is not None and (self._card is not None or self._transaction_id is not None):
            return False
        elif self._transaction_id is not None and (self._card is not None or self._token is not None):
            return False
        elif self._card is None and self._token is None and self._transaction_id is None:
            return False

        return True

    def amount_not_none(self):
        return self._amount is not None

    def currency_not_none(self):
        return self._currency is not None


class HpsCreditServiceVerifyBuilder(HpsBuilderAbstract):
    _card = None
    _token = None
    _track_data = None
    _card_holder = None
    _request_multi_use_token = False
    _client_transaction_id = None
    _card_present = None
    _reader_present = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        # Build the transaction request.
        transaction = Et.Element('CreditAccountVerify')
        block1 = Et.SubElement(transaction, 'Block1')

        # Add Card Holder
        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        # Add Card Data
        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        elif self._token is not None:
            card_data_element.append(self._service.hydrate_token_data(
                self._token,
                self._card_present,
                self._reader_present
            ))
        elif self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))

        # Add Token Request
        token_request = Et.SubElement(card_data_element, 'TokenRequest')
        if self._request_multi_use_token:
            token_request.text = 'Y'
        else:
            token_request.text = 'N'

        return self._service.submit_transaction(transaction, self._client_transaction_id)

    def _setup_validations(self):
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Authorize can only use one payment method')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._card is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._track_data is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsCreditServiceVoidBuilder(HpsBuilderAbstract):
    _transaction_id = None
    _client_transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CreditVoid')
        Et.SubElement(transaction, 'GatewayTxnId').text = str(self._transaction_id)

        return self._service.submit_transaction(transaction, self._client_transaction_id)

    def _setup_validations(self):
        self.add_validation(self.transaction_id_is_not_none, HpsArgumentException, 'Void needs a transaction id.')

    def transaction_id_is_not_none(self):
        return self._transaction_id is not None


"""
    HpsDebitService
"""


class HpsFluentDebitService(HpsSoapGatewayService):
    def __init__(self, config=None):
        HpsSoapGatewayService.__init__(self, config)

    def with_config(self, config):
        self.services_config = config
        return self

    def sale(self, amount=None):
        return HpsDebitServiceSaleBuilder(self).with_amount(amount)

    def refund(self, amount=None):
        return HpsDebitServiceReturnBuilder(self).with_amount(amount)

    def reverse(self, amount=None):
        return HpsDebitServiceReversalBuilder(self).with_amount(amount)

    def submit_transaction(self, transaction, client_transaction_id=None):
        rsp = self.do_transaction(transaction, client_transaction_id)['Ver1.0']

        amount = None
        if transaction.tag == 'DebitSale':
            amount = transaction.iter('Amt').next().text

        self.process_charge_gateway_response(rsp, transaction.tag, amount, 'usd')
        self.process_charge_issuer_response(rsp, transaction.tag, amount, 'usd')

        return HpsDebitAuthorization.from_dict(rsp)

    def process_charge_issuer_response(self, response, expected_type, *args):
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
                        # self.reverse(int(transaction_id), *args)
                        self.reverse().with_transaction_id(int(transaction_id), *args)
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

    def process_charge_gateway_response(self, response, expected_type, *args):
        response_code = response['Header']['GatewayRspCode']
        if response_code == 0:
            return
        if response_code == 30:
            try:
                # self.reverse(response['Header']['GatewayTxnId'], *args)
                self.reverse().with_transaction_id(response['Header']['GatewayTxnId'], *args)
            except Exception, e:
                raise HpsGatewayException(
                    HpsExceptionCodes.gateway_timeout_reversal_error,
                    'Error occurred while reversing a charge due to HPS gateway time-out.',
                    e)
        HpsGatewayResponseValidation.check_response(response, expected_type)


class HpsDebitServiceReturnBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _amount = None
    _card_holder = None
    _details = None
    _pin_block = None
    _token = None
    _track_data = None
    _transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('DebitReturn')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'

        if self._track_data is not None:
            Et.SubElement(block1, 'TrackData').text = self._track_data.value
            if self._track_data.encryption_data is not None:
                block1.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)
        if self._token is not None:
            Et.SubElement(block1, 'TokenData').text = self._token

        if self._pin_block is not None:
            Et.SubElement(block1, 'PinBlock').text = self._pin_block

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Return needs one payment method.')
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Return needs an amount.')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._transaction_id is not None:
            payment_methods += 1

        return payment_methods == 1

    def amount_is_not_none(self):
        return self._amount is not None


class HpsDebitServiceReversalBuilder(HpsBuilderAbstract):
    _amount = None
    _authorized_amount = None
    _details = None
    _track_data = None
    _transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('DebitReversal')
        block1 = Et.SubElement(transaction, 'Block1')

        if self._amount is not None:
            Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._authorized_amount is not None:
            Et.SubElement(block1, 'AuthAmt').text = str(self._authorized_amount)

        if self._track_data is not None:
            Et.SubElement(block1, 'TrackData').text = self._track_data.value
            if self._track_data.encryption_data is not None:
                block1.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))

        if self._transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)

        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Reversal needs one payment method.')

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._transaction_id is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsDebitServiceSaleBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _allow_partial_auth = False
    _amount = None
    _card_holder = None
    _cash_back = None
    _pin_block = None
    _token = None
    _track_data = None
    _details = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)

        transaction = Et.Element('DebitSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'
        Et.SubElement(block1, 'AllowPartialAuth').text = 'Y' if self._allow_partial_auth else 'N'

        if self._track_data is not None:
            Et.SubElement(block1, 'TrackData').text = self._track_data.value
            if self._track_data.encryption_data is not None:
                block1.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(block1, 'TokenData').text = self._token

        if self._pin_block is not None:
            Et.SubElement(block1, 'PinBlock').text = self._pin_block

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        if self._cash_back is not None:
            Et.SubElement(block1, 'CashbackAmtInfo').text = str(self._cash_back)

        # Handle the AdditionalTxnFields
        if self._details is not None:
            block1.append(self._service.hydrate_additional_txn_fields(self._details))

        client_txn_id = self._service.get_client_txn_id(self._details)
        return self._service.submit_transaction(transaction, client_txn_id)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Debit Sale needs an amount.')
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Debit Sale needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1

        return payment_methods == 1


"""
    HpsFluentCheckService
"""


class HpsFluentCheckService(HpsSoapGatewayService):
    def __init__(self, config=None, enable_logging=False):
        HpsSoapGatewayService.__init__(self, config, enable_logging=enable_logging)

    def with_config(self, config):
        self.services_config = config
        return self

    def with_enable_logging(self, enable):
        self._logging = enable

    def override(self):
        return HpsCheckServiceOverrideBuilder(self)

    def recurring(self, amount=None):
        return HpsCheckServiceRecurringBuilder(self).with_amount(amount)

    def return_check(self):
        return HpsCheckServiceReturnBuilder(self)

    def sale(self, amount=None):
        return HpsCheckServiceSaleBuilder(self).with_amount(amount)

    def void(self):
        return HpsCheckServiceVoidBuilder(self)

    def build_transaction(self, action, check, amount, client_transaction_id=None, check_verify=None, ach_verify=None):
        if amount is not None:
            HpsInputValidation.check_amount(amount)

        if (check.sec_code == "CCD"
            and (check.check_holder is None
                 or check.check_holder.check_name is None)):
            raise HpsInvalidRequestException(
                HpsExceptionCodes.missing_check_name,
                'For sec code CCD the check name is required.', 'check_name')

        transaction = Et.Element('CheckSale')
        block1 = Et.SubElement(transaction, 'Block1')
        if amount is not None:
            Et.SubElement(block1, 'Amt').text = str(amount)
        block1.append(self.hydrate_check_data(check))
        Et.SubElement(block1, 'CheckAction').text = action
        Et.SubElement(block1, 'SECCode').text = str(check.sec_code)

        if check_verify is not None or ach_verify is not None:
            verify_element = Et.SubElement(block1, 'VerifyInfo')
            if check_verify is not None:
                Et.SubElement(verify_element, 'CheckVerify').text = 'Y' if check_verify else 'N'
            if ach_verify is not None:
                Et.SubElement(verify_element, 'ACHVerify').text = 'Y' if ach_verify else 'N'

        if check.check_type is not None:
            Et.SubElement(block1, 'CheckType').text = str(check.check_type)
        if check.data_entry_mode is not None:
            Et.SubElement(block1, 'DataEntryMode').text = str(check.data_entry_mode)
        if check.check_holder is not None:
            block1.append(self.hydrate_consumer_info(check))

        return self.submit_transaction(transaction, client_transaction_id)

    def submit_transaction(self, transaction, client_transaction_id=None):
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


class HpsCheckServiceOverrideBuilder(HpsBuilderAbstract):
    _check = None
    _amount = None
    _client_transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        return self._service.build_transaction(
            'OVERRIDE',
            self._check,
            self._amount,
            self._client_transaction_id
        )

    def _setup_validations(self):
        self.add_validation(self._amount_is_not_none, HpsArgumentException, 'Amount is required for override.')
        self.add_validation(self._check_is_not_none, HpsArgumentException, 'Check is required for override.')

    def _amount_is_not_none(self):
        return self._amount is not None

    def _check_is_not_none(self):
        return self._check is not None


class HpsCheckServiceRecurringBuilder(HpsBuilderAbstract):
    _amount = None
    _payment_method_key = None
    _schedule = None
    _one_time = False

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)

        transaction = Et.Element('CheckSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'CheckAction').text = 'SALE'
        Et.SubElement(block1, 'PaymentMethodKey').text = str(self._payment_method_key)

        recurring_data = Et.SubElement(block1, 'RecurringData')
        if self._schedule is not None:
            schedule_key = self._schedule
            if isinstance(self._schedule, HpsPayPlanSchedule):
                schedule_key = self._schedule.schedule_key
            Et.SubElement(recurring_data, 'ScheduleID').text = str(schedule_key)

        Et.SubElement(recurring_data, 'OneTime').text = 'Y' if self._one_time else 'N'

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._amount_is_not_none, HpsArgumentException, 'Amount is required for sale.')
        self.add_validation(
            self._payment_method_is_not_none,
            HpsArgumentException,
            'Payment method key is required for sale.'
        )

    def _amount_is_not_none(self):
        if not self._check_verify and not self._ach_verify:
            return self._amount is not None
        return True

    def _payment_method_is_not_none(self):
        return self._payment_method_key is not None


class HpsCheckServiceReturnBuilder(HpsBuilderAbstract):
    _check = None
    _amount = None
    _client_transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        return self._service.build_transaction(
            'RETURN',
            self._check,
            self._amount,
            self._client_transaction_id
        )

    def _setup_validations(self):
        self.add_validation(self._amount_is_not_none, HpsArgumentException, 'Amount is required for return.')
        self.add_validation(self._check_is_not_none, HpsArgumentException, 'Check is required for return.')

    def _amount_is_not_none(self):
        return self._amount is not None

    def _check_is_not_none(self):
        return self._check is not None


class HpsCheckServiceSaleBuilder(HpsBuilderAbstract):
    _ach_verify = None
    _amount = None
    _check = None
    _check_verify = None
    _client_transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        return self._service.build_transaction(
            'SALE',
            self._check,
            self._amount,
            self._client_transaction_id,
            self._check_verify,
            self._ach_verify
        )

    def _setup_validations(self):
        self.add_validation(self._amount_is_not_none, HpsArgumentException, 'Amount is required for sale.')
        self.add_validation(self._check_is_not_none, HpsArgumentException, 'Check is required for sale.')

    def _amount_is_not_none(self):
        if not self._check_verify and not self._ach_verify:
            return self._amount is not None
        return True

    def _check_is_not_none(self):
        return self._check is not None


class HpsCheckServiceVoidBuilder(HpsBuilderAbstract):
    _transaction_id = None
    _client_transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('CheckVoid')
        block1 = Et.SubElement(transaction, 'Block1')

        if self._transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)
        elif self._client_transaction_id is not None:
            txn_id = Et.SubElement(block1, 'ClientTxnId')
            txn_id.text = str(self._client_transaction_id)

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._only_one_transaction_id, HpsArgumentException, 'Void can only use one transaction id')

    def _only_one_transaction_id(self):
        if self._transaction_id is not None and self._client_transaction_id is not None:
            return False
        elif self._transaction_id is None and self._client_transaction_id is None:
            return False

        return True


"""
    HpsFluentGiftCardService
"""


class HpsFluentGiftCardService(HpsSoapGatewayService):
    def __init__(self, config=None):
        HpsSoapGatewayService.__init__(self, config)

    def with_config(self, config):
        self.services_config = config
        return self

    def activate(self, amount=None):
        return HpsGiftCardServiceActivateBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def add_value(self, amount=None):
        return HpsGiftCardServiceAddValueBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def alias(self):
        return HpsGiftCardServiceAliasBuilder(self)

    def balance(self):
        return HpsGiftCardServiceBalanceBuilder(self)

    def deactivate(self):
        return HpsGiftCardServiceDeactivateBuilder(self)

    def replace(self):
        return HpsGiftCardServiceReplaceBuilder(self)

    def reverse(self, amount=None):
        return HpsGiftCardServiceReverseBuilder(self)\
            .with_amount(amount)

    def reward(self, amount=None):
        return HpsGiftCardServiceRewardBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def sale(self, amount=None):
        return HpsGiftCardServiceSaleBuilder(self)\
            .with_amount(amount)\
            .with_currency('usd')

    def void(self, transaction_id=None):
        return HpsGiftCardServiceVoidBuilder(self).with_transaction_id(transaction_id)

    def submit_transaction(self, transaction):
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


class HpsGiftCardServiceActivateBuilder(HpsBuilderAbstract):
    _amount = None
    _card = None
    _currency = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)
        HpsInputValidation.check_currency(self._currency)

        transaction = Et.Element('GiftCardActivate')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'Amt').text = str(self._amount)
        block1.append(self._service.hydrate_gift_card_data(self._card))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._card_not_none, HpsArgumentException, 'Activate needs a payment method.')
        self.add_validation(self._amount_not_none, HpsArgumentException, 'Activate needs an amount.')
        self.add_validation(self._currency_not_none, HpsArgumentException, 'Activate needs a currency.')

    def _card_not_none(self):
        return self._card is not None

    def _amount_not_none(self):
        return self._amount is not None

    def _currency_not_none(self):
        return self._currency is not None


class HpsGiftCardServiceAddValueBuilder(HpsBuilderAbstract):
    _card = None
    _amount = None
    _currency = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)
        HpsInputValidation.check_currency(self._currency)

        transaction = Et.Element('GiftCardAddValue')
        block1 = Et.SubElement(transaction, 'Block1')

        Et.SubElement(block1, 'Amt').text = str(self._amount)
        block1.append(self._service.hydrate_gift_card_data(self._card))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(
            self._card_not_none,
            HpsArgumentException,
            'Activate can only use one payment method')
        self.add_validation(self._amount_not_none, HpsArgumentException, 'Activate needs an amount')
        self.add_validation(self._currency_not_none, HpsArgumentException, 'Activate needs a currency')

    def _card_not_none(self):
        return self._card is not None

    def _amount_not_none(self):
        return self._amount is not None

    def _currency_not_none(self):
        return self._currency is not None


class HpsGiftCardServiceAliasBuilder(HpsBuilderAbstract):
    _card = None
    _alias = None
    _action = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('GiftCardAlias')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Action').text = self._action
        Et.SubElement(block1, 'Alias').text = self._alias

        if self._card is not None:
            block1.append(self._service.hydrate_gift_card_data(self._card))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._alias_not_none, HpsArgumentException, 'Alias needs an alias.')
        self.add_validation(self._action_not_none, HpsArgumentException, 'Alias needs an action.')
        self.add_validation(self._card_not_none, HpsArgumentException, 'Alias needs a card.')

    def _card_not_none(self):
        if self._action is not 'CREATE':
            return self._card is not None
        else:
            return self._card is None

    def _alias_not_none(self):
        return self._alias is not None

    def _action_not_none(self):
        return self._action is not None


class HpsGiftCardServiceBalanceBuilder(HpsBuilderAbstract):
    _card = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('GiftCardBalance')
        block1 = Et.SubElement(transaction, 'Block1')
        block1.append(self._service.hydrate_gift_card_data(self._card))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._card_not_none, HpsArgumentException, 'Balance needs a card.')

    def _card_not_none(self):
        return self._card is not None


class HpsGiftCardServiceDeactivateBuilder(HpsBuilderAbstract):
    _card = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('GiftCardDeactivate')
        block1 = Et.SubElement(transaction, 'Block1')
        block1.append(self._service.hydrate_gift_card_data(self._card))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._card_not_none, HpsArgumentException, 'Balance needs a card.')

    def _card_not_none(self):
        return self._card is not None


class HpsGiftCardServiceReplaceBuilder(HpsBuilderAbstract):
    _old_card = None
    _new_card = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('GiftCardReplace')
        block1 = Et.SubElement(transaction, 'Block1')

        block1.append(self._service.hydrate_gift_card_data(self._old_card, 'OldCardData'))
        block1.append(self._service.hydrate_gift_card_data(self._new_card, 'NewCardData'))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._old_card_not_none, HpsArgumentException, 'Balance needs an old card.')
        self.add_validation(self._new_card_not_none, HpsArgumentException, 'Balance needs a new card.')

    def _old_card_not_none(self):
        return self._old_card is not None

    def _new_card_not_none(self):
        return self._new_card is not None


class HpsGiftCardServiceReverseBuilder(HpsBuilderAbstract):
    _card = None
    _amount = None
    _currency = None
    _transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        HpsInputValidation.check_amount(self._amount)

        transaction = Et.Element('GiftCardReversal')
        block1 = Et.SubElement(transaction, 'Block1')

        if self._amount is not None:
            Et.SubElement(block1, 'Amt').text = str(self._amount)

        if self._card is not None:
            block1.append(self._service.hydrate_gift_card_data(self._card))
        elif self._transaction_id is not None:
            Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self._amount_not_none, HpsArgumentException, 'Reverse needs an amount.')
        self.add_validation(self._only_one_payment_method, HpsArgumentException, 'Reverse needs a card or trans id.')

    def _amount_not_none(self):
        return self._amount is not None

    def _only_one_payment_method(self):
        if self._card is not None and self._transaction_id is not None:
            return False
        elif self._card is None and self._transaction_id is None:
            return False

        return True


class HpsGiftCardServiceRewardBuilder(HpsBuilderAbstract):
    _card = None
    _amount = None
    _currency = None
    _gratuity = None
    _tax = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        currency = self._currency.lower()
        HpsInputValidation.check_amount(self._amount)

        transaction = Et.Element('GiftCardReward')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        block1.append(self._service.hydrate_gift_card_data(self._card))

        if currency == 'usd' or currency == 'points':
            currency_element = Et.SubElement(block1, 'Currency')
            currency_element.text = 'USD' if currency == 'usd' else 'POINTS'

        if self._gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(self._gratuity)

        if self._tax is not None:
            Et.SubElement(block1, 'TaxAmtInfo').text = str(self._tax)

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(
            self._card_not_none,
            HpsArgumentException,
            'Reward can only use one payment method')
        self.add_validation(self._amount_not_none, HpsArgumentException, 'Reward needs an amount')
        self.add_validation(self._currency_not_none, HpsArgumentException, 'Reward needs a currency')

    def _card_not_none(self):
        return self._card is not None

    def _amount_not_none(self):
        return self._amount is not None

    def _currency_not_none(self):
        return self._currency is not None


class HpsGiftCardServiceSaleBuilder(HpsBuilderAbstract):
    _card = None
    _amount = None
    _currency = None
    _gratuity = None
    _tax = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        currency = self._currency.lower()
        HpsInputValidation.check_amount(self._amount)

        transaction = Et.Element('GiftCardSale')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        block1.append(self._service.hydrate_gift_card_data(self._card))

        if currency == 'usd' or currency == 'points':
            currency_element = Et.SubElement(block1, 'Currency')
            currency_element.text = 'USD' if currency == 'usd' else 'POINTS'

        if self._gratuity is not None:
            Et.SubElement(block1, 'GratuityAmtInfo').text = str(self._gratuity)

        if self._tax is not None:
            Et.SubElement(block1, 'TaxAmtInfo').text = str(self._tax)

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(
            self._card_not_none,
            HpsArgumentException,
            'Reward can only use one payment method')
        self.add_validation(self._amount_not_none, HpsArgumentException, 'Reward needs an amount')
        self.add_validation(self._currency_not_none, HpsArgumentException, 'Reward needs a currency')

    def _card_not_none(self):
        return self._card is not None

    def _amount_not_none(self):
        return self._amount is not None

    def _currency_not_none(self):
        return self._currency is not None


class HpsGiftCardServiceVoidBuilder(HpsBuilderAbstract):
    _transaction_id = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        trans = Et.Element('GiftCardVoid')
        block1 = Et.SubElement(trans, 'Block1')
        Et.SubElement(block1, 'GatewayTxnId').text = str(self._transaction_id)

        return self._service.submit_transaction(trans)

    def _setup_validations(self):
        self.add_validation(self._transaction_id_not_none, HpsArgumentException, 'Void needs a transaction id.')

    def _transaction_id_not_none(self):
        return self._transaction_id is not None

"""
    HpsFluentEbtFsService
"""


class HpsFluentEbtService(HpsSoapGatewayService):
    def __init__(self, config=None):
        HpsSoapGatewayService.__init__(self, config)

    def with_config(self, config):
        self.services_config = config
        return self

    def balance_inquiry(self):
        return HpsEbtBalanceInquiryBuilder(self).with_amount(0.00)

    def benefit_withdrawal(self, amount):
        return HpsEbtBenefitWithdrawalBuilder(self).with_amount(amount)

    def cash_back_purchase(self, amount):
        return HpsEbtCashBackPurchaseBuilder(self).with_amount(amount)

    def purchase(self, amount=None):
        return HpsEbtPurchaseBuilder(self).with_amount(amount)

    def refund(self, amount=None):
        return HpsEbtRefundBuilder(self).with_amount(amount)

    def voucher_purchase(self, amount=None):
        return HpsEbtVoucherPurchaseBuilder(self).with_amount(amount)

    def submit_transaction(self, transaction, client_transaction_id=None):
        rsp = self.do_transaction(transaction, client_transaction_id)['Ver1.0']
        HpsGatewayResponseValidation.check_response(rsp, transaction.tag)

        HpsIssuerResponseValidation.check_response(
            rsp['Header']['GatewayTxnId'],
            rsp['Transaction'][transaction.tag]['RspCode'],
            rsp['Transaction'][transaction.tag]['RspText'])

        return HpsEbtAuthorization().from_dict(rsp)


class HpsEbtBalanceInquiryBuilder(HpsBuilderAbstract):
    _amount = None
    _card = None
    _card_present = False
    _inquiry_type = None
    _pin_block = None
    _reader_present = None
    _request_multi_use_token = False
    _track_data = None
    _token = None
    _token_parameters = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('EBTBalanceInquiry')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)

        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        if self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(card_data_element, 'TokenData').text = self._token

        Et.SubElement(card_data_element, 'TokenRequest').text = 'Y' if self._request_multi_use_token else 'N'
        Et.SubElement(block1, 'BalanceInquiryType').text = self._inquiry_type
        Et.SubElement(block1, 'PinBlock').text = self._pin_block

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Balance Inquiry needs an amount.')
        self.add_validation(self.pin_block_is_not_none, HpsArgumentException, 'Balance Inquiry needs a pin block.')
        self.add_validation(
            self.inquiry_type_is_not_none,
            HpsArgumentException,
            'Balance Inquiry needs an inquiry type.')
        self.add_validation(
            self.only_one_payment_method,
            HpsArgumentException,
            'Balance Inquiry needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def inquiry_type_is_not_none(self):
        return self._inquiry_type is not None

    def pin_block_is_not_none(self):
        return self._pin_block is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._card is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsEbtBenefitWithdrawalBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _amount = None
    _card = None
    _card_holder = None
    _pin_block = None
    _request_multi_use_token = False
    _token = None
    _token_parameters = None
    _track_data = None

    # cash back purchase params
    _cash_back = 0.00

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('EBTCashBenefitWithdrawal')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'
        Et.SubElement(block1, 'CashBackAmount').text = str(self._cash_back)

        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(self._card))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        if self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(card_data_element, 'TokenData').text = self._token

        Et.SubElement(card_data_element, 'TokenRequest').text = 'Y' if self._request_multi_use_token else 'N'
        Et.SubElement(block1, 'PinBlock').text = self._pin_block

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Purchase needs an amount.')
        self.add_validation(self.pin_block_is_not_none, HpsArgumentException, 'Balance Inquiry needs a pin block.')
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Purchase needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def pin_block_is_not_none(self):
        return self._pin_block is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._card is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsEbtCashBackPurchaseBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _amount = None
    _card = None
    _card_holder = None
    _pin_block = None
    _request_multi_use_token = False
    _token = None
    _token_parameters = None
    _track_data = None

    # cash back purchase params
    _cash_back = 0.00

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('EBTCashBackPurchase')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'
        Et.SubElement(block1, 'CashBackAmount').text = str(self._cash_back)

        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(self._card))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        if self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(card_data_element, 'TokenData').text = self._token

        Et.SubElement(card_data_element, 'TokenRequest').text = 'Y' if self._request_multi_use_token else 'N'
        Et.SubElement(block1, 'PinBlock').text = self._pin_block

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Purchase needs an amount.')
        self.add_validation(self.pin_block_is_not_none, HpsArgumentException, 'Balance Inquiry needs a pin block.')
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Purchase needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def pin_block_is_not_none(self):
        return self._pin_block is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._card is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsEbtPurchaseBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _amount = None
    _card = None
    _card_holder = None
    _pin_block = None
    _request_multi_use_token = False
    _token = None
    _token_parameters = None
    _track_data = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('EBTFSPurchase')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'

        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(self._card))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        if self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(card_data_element, 'TokenData').text = self._token

        Et.SubElement(card_data_element, 'TokenRequest').text = 'Y' if self._request_multi_use_token else 'N'
        Et.SubElement(block1, 'PinBlock').text = self._pin_block

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Purchase needs an amount.')
        self.add_validation(self.pin_block_is_not_none, HpsArgumentException, 'Balance Inquiry needs a pin block.')
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Purchase needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def pin_block_is_not_none(self):
        return self._pin_block is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._card is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsEbtRefundBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _amount = None
    _card = None
    _card_holder = None
    _pin_block = None
    _request_multi_use_token = None
    _token = None
    _token_parameters = None
    _track_data = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('EBTFSReturn')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'PinBlock').text = self._pin_block
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'

        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(
                self._card,
                self._card_present,
                self._reader_present
            ))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        if self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(card_data_element, 'TokenData').text = self._token

        Et.SubElement(card_data_element, 'TokenRequest').text = 'Y' if self._request_multi_use_token else 'N'
        if self._token_parameters is not None:
            block1.append(self._service.hydrate_token_params(self._token_parameters))

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Purchase needs an amount.')
        self.add_validation(self.pin_block_is_not_none, HpsArgumentException, 'Balance Inquiry needs a pin block.')
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Purchase needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def pin_block_is_not_none(self):
        return self._pin_block is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._card is not None:
            payment_methods += 1

        return payment_methods == 1


class HpsEbtVoucherPurchaseBuilder(HpsBuilderAbstract):
    _allow_duplicates = False
    _amount = None
    _card = None
    _card_holder = None
    _pin_block = None
    _request_multi_use_token = False
    _token = None
    _token_parameters = None
    _track_data = None

    _approval_code = None
    _expiration_date = None
    _primary_account_number = None
    _serial_number = None

    def __init__(self, service):
        HpsBuilderAbstract.__init__(self, service)

    def execute(self):
        HpsBuilderAbstract.execute(self)

        transaction = Et.Element('EBTVoucherPurchase')
        block1 = Et.SubElement(transaction, 'Block1')
        Et.SubElement(block1, 'Amt').text = str(self._amount)
        Et.SubElement(block1, 'AllowDup').text = 'Y' if self._allow_duplicates else 'N'

        Et.SubElement(block1, 'ElectronicVoucherSerialNbr').text = str(self._serial_number)
        Et.SubElement(block1, 'VoucherApprovalCd').text = str(self._approval_code)
        Et.SubElement(block1, 'ExprDate').text = self._expiration_date
        Et.SubElement(block1, 'PrimaryAcctNbr').text = self._primary_account_number

        card_data_element = Et.SubElement(block1, 'CardData')
        if self._card is not None:
            card_data_element.append(self._service.hydrate_card_manual_entry(self._card))
            if self._card.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._card.encryption_data))
        if self._track_data is not None:
            card_data_element.append(self._service.hydrate_track_data(self._track_data))
            if self._track_data.encryption_data is not None:
                card_data_element.append(self._service.hydrate_encryption_data(self._track_data.encryption_data))
        if self._token is not None:
            Et.SubElement(card_data_element, 'TokenData').text = self._token

        Et.SubElement(card_data_element, 'TokenRequest').text = 'Y' if self._request_multi_use_token else 'N'
        Et.SubElement(block1, 'PinBlock').text = self._pin_block

        if self._card_holder is not None:
            block1.append(self._service.hydrate_card_holder_data(self._card_holder))

        return self._service.submit_transaction(transaction)

    def _setup_validations(self):
        self.add_validation(self.amount_is_not_none, HpsArgumentException, 'Purchase needs an amount.')
        self.add_validation(self.pin_block_is_not_none, HpsArgumentException, 'Balance Inquiry needs a pin block.')
        self.add_validation(self.only_one_payment_method, HpsArgumentException, 'Purchase needs one payment method.')

    def amount_is_not_none(self):
        return self._amount is not None

    def pin_block_is_not_none(self):
        return self._pin_block is not None

    def only_one_payment_method(self):
        payment_methods = 0
        if self._track_data is not None:
            payment_methods += 1
        if self._token is not None:
            payment_methods += 1
        if self._card is not None:
            payment_methods += 1

        return payment_methods == 1


"""
    HpsFluentGatewayService
"""


class HpsFluentGatewayService(object):
    credit = HpsFluentCreditService()
    debit = HpsFluentDebitService()
    gift = HpsFluentGiftCardService()
    check = HpsFluentCheckService()
    ebt = HpsFluentEbtService()

    def __init__(self, config=None):
        self.credit.with_config(config)
        self.debit.with_config(config)
        self.gift.with_config(config)
        self.check.with_config(config)
        self.ebt.with_config(config)