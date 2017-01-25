import unittest

from securesubmit.services.fluent.gateway import HpsFluentCreditService
from securesubmit.tests.test_data import TestServicesConfig, TestData, TestCardHolder


class Certification(unittest.TestCase):
    credit_service = HpsFluentCreditService().with_config(TestServicesConfig.valid_services_config)

    def test_visa_3ds_decrypted_should_charge_ok(self):
        payment_data = TestData.visa_payment_data()
        response = self.credit_service.charge(payment_data.transaction_amount)\
            .with_payment_data(payment_data)\
            .with_payment_data_source('ApplePay')\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_request_multi_use_token(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

    def test_visa_3ds_decrypted_should_auth_ok(self):
        payment_data = TestData.visa_payment_data()
        response = self.credit_service.authorize(payment_data.transaction_amount)\
            .with_payment_data(payment_data)\
            .with_payment_data_source('ApplePay')\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_request_multi_use_token(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

        capture_response = self.credit_service.capture()\
            .with_transaction_id(response.transaction_id)\
            .execute()
        self.assertIsNotNone(capture_response)

    def test_amex_3ds_decrypted_should_charge_ok(self):
        payment_data = TestData.amex_payment_data()
        response = self.credit_service.charge(payment_data.transaction_amount)\
            .with_payment_data(payment_data)\
            .with_payment_data_source('ApplePay')\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_request_multi_use_token(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

    def test_amex_3ds_decrypted_should_auth_ok(self):
        payment_data = TestData.amex_payment_data()
        response = self.credit_service.authorize(payment_data.transaction_amount)\
            .with_payment_data(payment_data)\
            .with_payment_data_source('ApplePay')\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_request_multi_use_token(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

        capture_response = self.credit_service.capture()\
            .with_transaction_id(response.transaction_id)\
            .execute()
        self.assertIsNotNone(capture_response)