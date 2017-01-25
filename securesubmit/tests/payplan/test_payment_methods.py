import unittest

from securesubmit.entities.payplan import HpsPayPlanPaymentMethod
from securesubmit.infrastructure.enums import HpsPayPlanPaymentMethodStatus, HpsPayPlanPaymentMethodType
from securesubmit.services.gateway import HpsPayPlanService
from securesubmit.tests.test_data import TestServicesConfig


class PayPlanPaymentMethodTests(unittest.TestCase):
    service = HpsPayPlanService(TestServicesConfig.valid_pay_plan_config, True)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    customer = service.page(1, 0).find_all_customers().results[0]

    def test_001_add(self):
        payment_method = HpsPayPlanPaymentMethod()
        payment_method.customer_key = self.customer.customer_key
        payment_method.payment_method_type = HpsPayPlanPaymentMethodType.CREDIT_CARD
        payment_method.name_on_account = 'Bill Johnson'
        payment_method.account_number = 4111111111111111
        payment_method.expiration_date = '0120'
        payment_method.country = 'USA'

        response = self.service.add_payment_method(payment_method)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.payment_method_key)

    def test_002_edit(self):
        results = self.service.page(1, 0).find_all_payment_methods({'customerIdentifier': 'SecureSubmit'})
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) >= 1)

        payment_method = results.results[0]
        payment_status = HpsPayPlanPaymentMethodStatus.ACTIVE
        if payment_method.payment_status == HpsPayPlanPaymentMethodStatus.ACTIVE:
            payment_status = HpsPayPlanPaymentMethodStatus.INACTIVE
        payment_method.payment_status = payment_status

        response = self.service.edit_payment_method(payment_method)
        self.assertIsNotNone(response)
        self.assertEqual(payment_method.payment_method_key, response.payment_method_key)
        self.assertEqual(payment_status, payment_method.payment_status)

        response = self.service.get_payment_method(payment_method.payment_method_key)
        self.assertIsNotNone(response)
        self.assertEqual(payment_method.payment_method_key, response.payment_method_key)
        self.assertEqual(payment_status, payment_method.payment_status)

    def test_003_find_all(self):
        results = self.service.find_all_payment_methods()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) > 0)

    def test_004_find_all_with_paging(self):
        results = self.service.page(1, 0).find_all_payment_methods()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

    def test_005_find_all_with_filters(self):
        results = self.service.find_all_payment_methods({'customerIdentifier': 'SecureSubmit'})
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) >= 1)

    def test_006_get_by_payment_method(self):
        results = self.service.page(1, 0).find_all_payment_methods()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        payment_method = self.service.get_payment_method(results.results[0])
        self.assertIsNotNone(payment_method)
        self.assertEqual(results.results[0].payment_method_key, payment_method.payment_method_key)

    def test_007_get_by_key(self):
        results = self.service.page(1, 0).find_all_payment_methods()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        payment_method = self.service.get_payment_method(results.results[0].payment_method_key)
        self.assertIsNotNone(payment_method)
        self.assertEqual(results.results[0].payment_method_key, payment_method.payment_method_key)

    def test_008_delete_by_payment_method(self):
        self.test_001_add()

        results = self.service.page(1, 0).find_all_payment_methods()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        payment_method = self.service.delete_payment_method(results.results[0])
        self.assertIsNone(payment_method)

    def test_009_delete_by_key(self):
        self.test_001_add()

        results = self.service.page(1, 0).find_all_payment_methods()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        payment_method = self.service.delete_payment_method(results.results[0].payment_method_key)
        self.assertIsNone(payment_method)
