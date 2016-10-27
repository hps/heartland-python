import unittest
import datetime
from securesubmit.entities.credit import HpsCreditCard
from securesubmit.services import HpsServicesConfig

from securesubmit.services.gateway import (
    HpsCreditService,
    HpsTransactionType,
    HpsExceptionCodes,
    HpsInvalidRequestException,
    HpsAuthenticationException,
    HpsCreditException,
    HpsGatewayException,
    HpsTransactionDetails,
    HpsCardHolder,
    HpsAddress,
    HpsDirectMarketData)
from securesubmit.tests.test_data import (
    TestCreditCard,
    TestCardHolder,
    TestServicesConfig)


class GeneralTests(unittest.TestCase):
    charge_service = HpsCreditService(enable_logging=True)

    def test_charge_ampersand_in_customer_id(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        details = HpsTransactionDetails()
        details.customer_id = '&something'

        try:
            response = self.charge_service.charge(
                '5', 'usd', TestCreditCard.valid_visa,
                None, False, None, False, details)
            self.assertIsNotNone(response)
            self.assertEqual('00', response.response_code)
        except HpsGatewayException, e:
            self.fail('Gateway threw an error')

    def test_charge_ampersand_in_invoice_number(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        details = HpsTransactionDetails()
        details.invoice_number = '&something'

        try:
            response = self.charge_service.charge(
                '5', 'usd', TestCreditCard.valid_visa,
                None, False, None, False, details)
            self.assertIsNotNone(response)
            self.assertEqual('00', response.response_code)
        except HpsGatewayException, e:
            self.fail('Gateway threw an error')

    def test_charge_ampersand_in_memo(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        details = HpsTransactionDetails()
        details.memo = '&something'

        try:
            response = self.charge_service.charge(
                '5', 'usd', TestCreditCard.valid_visa,
                None, False, None, False, details)
            self.assertIsNotNone(response)
            self.assertEqual('00', response.response_code)
        except HpsGatewayException, e:
            self.fail('Gateway threw an error')

    def test_charge_ampersand_in_descriptor(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        try:
            response = self.charge_service.charge(
                '5', 'usd', TestCreditCard.valid_visa, descriptor='&something')
            self.assertIsNotNone(response)
            self.assertEqual('00', response.response_code)
        except HpsGatewayException, e:
            self.fail('Gateway threw an error')

    def test_charge_ampersand_in_address(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        card_holder = HpsCardHolder()
        # card_holder.first_name = '&firstname' OK
        # card_holder.last_name = '&lastname' OK
        card_holder.address = HpsAddress()
        # card_holder.address.address = '&address' OK
        # card_holder.address.city = '&city' OK
        # card_holder.address.country = '&country' OK
        # card_holder.address.state = '&state' OK
        card_holder.address.zip = '40205'
        # card_holder.email = '&email'
        card_holder.phone = '2563235076'

        try:
            response = self.charge_service.charge(
                '5', 'usd', TestCreditCard.valid_visa, card_holder)
            self.assertIsNotNone(response)
            self.assertEqual('00', response.response_code)
        except HpsGatewayException, e:
            self.fail(e.message)

    def test_charge_secretkey_trimming(self):
        config = HpsServicesConfig()
        config.secret_api_key = '   skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A     '
        self.charge_service._config = config
        charge_amount = 5

        try:
            response = self.charge_service.charge(
                charge_amount, "usd",
                TestCreditCard.valid_visa,
                TestCardHolder.valid_card_holder)
            self.assertIsNotNone(response)
            self.assertEqual('00', response.response_code)
        except HpsGatewayException, e:
            self.fail(e.message)


    def test_charge_invalid_amount(self):
        charge_amount = -5
        self.charge_service._config = None

        try:
            self.charge_service.charge(
                charge_amount, "usd",
                TestCreditCard.valid_visa,
                TestCardHolder.valid_card_holder)
        except HpsInvalidRequestException, e:
            self.assertEquals(e.code, HpsExceptionCodes.invalid_amount)
            self.assertEquals(e.param_name, 'amount')
            return

        self.fail("No exception was raised")

    def test_charge_empty_currency(self):
        charge_amount = 50
        currency = ""
        self.charge_service._config = None

        try:
            self.charge_service.charge(
                charge_amount, currency,
                TestCreditCard.valid_visa,
                TestCardHolder.valid_card_holder)
        except HpsInvalidRequestException, e:
            self.assertEquals(e.code, HpsExceptionCodes.missing_currency)
            self.assertEquals(e.param_name, "currency")
            return

        self.fail("No exception was raised")

    def test_charge_no_currency(self):
        charge_amount = 50
        currency = "EUR"
        self.charge_service._config = None

        try:
            self.charge_service.charge(
                charge_amount, currency,
                TestCreditCard.valid_visa,
                TestCardHolder.valid_card_holder)
        except HpsInvalidRequestException, e:
            self.assertEquals(e.code, HpsExceptionCodes.invalid_currency)
            self.assertEquals(e.param_name, 'currency')
            return

        self.fail("No exception was thrown.")

    def test_charge_invalid_config(self):
        charge_amount = 50
        currency = "usd"
        self.charge_service.services_config = None

        try:
            self.charge_service.charge(
                charge_amount, currency,
                TestCreditCard.valid_visa,
                TestCardHolder.valid_card_holder)
        except HpsAuthenticationException, e:
            self.assertIn(
                e.message,
                ('The HPS SDK has not been properly configured. '
                 'Please make sure to initialize the config either '
                 'in a service constructor or in your App.config '
                 'or Web.config file.'))
            return

        self.fail("No exception was thrown.")

    def test_charge_invalid_card_number(self):
        charge_amount = 50
        currency = "usd"
        self.charge_service._config = TestServicesConfig.valid_services_config

        try:
            self.charge_service.charge(
                charge_amount, currency,
                TestCreditCard.invalid_card,
                TestCardHolder.valid_card_holder)
        except (HpsCreditException, HpsGatewayException) as e:
            self.assertEqual(e.code, HpsExceptionCodes.invalid_number)
            return

        self.fail("No exception was thrown.")

    def test_list_should_list(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        items = self.charge_service.list(
            datetime.datetime.utcnow() + datetime.timedelta(-10),
            datetime.datetime.utcnow())
        self.assertIsNotNone(items)

    def test_list_should_list_filter(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        items = self.charge_service.list(
            datetime.datetime.utcnow() + datetime.timedelta(-10),
            datetime.datetime.utcnow(), HpsTransactionType.Capture)
        self.assertIsNotNone(items)

    def test_get_first_charge(self):
        self.charge_service._config = TestServicesConfig.valid_services_config
        items = self.charge_service.list(
            datetime.datetime.utcnow() + datetime.timedelta(-10),
            datetime.datetime.utcnow())

        if len(items) > 0:
            charge = self.charge_service.get(items[0].transaction_id)
            self.assertIsNotNone(charge)

    def test_charge_with_market_data(self):
        direct_market_data = HpsDirectMarketData('123456', 10, 8)
        self.charge_service._config = TestServicesConfig.valid_services_config

        response = self.charge_service.charge(
            50, 'usd',
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder,
            direct_market_data=direct_market_data)

        self.assertEqual('00', response.response_code)

    def test_capture_with_market_data(self):
        self.charge_service._config = TestServicesConfig.valid_services_config
        auth_response = self.charge_service.authorize(
            50, 'usd', TestCreditCard.valid_amex, TestCardHolder.valid_card_holder)
        self.assertEquals('00', auth_response.response_code)

        direct_market_data = HpsDirectMarketData('123456', 10, 8)
        response = self.charge_service.capture(auth_response.transaction_id, direct_market_data=direct_market_data)
        self.assertEquals('00', response.response_code)

    def test_charge_with_default_market_data(self):
        direct_market_data = HpsDirectMarketData()
        self.charge_service._config = TestServicesConfig.valid_services_config

        response = self.charge_service.charge(
            50, 'usd',
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder,
            direct_market_data=direct_market_data)

        self.assertEqual('00', response.response_code)

    def test_capture_with_default_market_data(self):
        self.charge_service._config = TestServicesConfig.valid_services_config
        auth_response = self.charge_service.authorize(
            50, 'usd', TestCreditCard.valid_amex, TestCardHolder.valid_card_holder)
        self.assertEquals('00', auth_response.response_code)

        direct_market_data = HpsDirectMarketData()
        response = self.charge_service.capture(auth_response.transaction_id, direct_market_data=direct_market_data)
        self.assertEquals('00', response.response_code)

    def test_cvv_with_leading_zero(self):
        self.charge_service._config = TestServicesConfig.valid_services_config

        card = HpsCreditCard()
        card.number = "4111111111111111"
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = "012"

        response = self.charge_service.authorize(15.15, 'usd', card)
        self.assertIsNotNone(response)
        self.assertEquals('00', response.response_code)

    def test_update_token_expiry(self):
        config = HpsServicesConfig()
        config.secret_api_key = 'skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A'

        self.charge_service._config = config

        card = HpsCreditCard()
        card.number = "4111111111111111"
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = "012"

        response = self.charge_service.authorize(12.09, 'usd', card, request_multi_use_token=True)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertIsNotNone(response.token_data)

        update_token_response = self.charge_service.update_token_expiry(response.token_data.token_value, 12, 2035)
        self.assertIsNotNone(response)
        self.assertEqual('0', update_token_response.response_code)
