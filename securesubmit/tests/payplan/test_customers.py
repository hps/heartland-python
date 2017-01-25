import random
import unittest
import datetime
import time

from securesubmit.entities.payplan import *
from securesubmit.infrastructure.enums import HpsPayPlanCustomerStatus
from securesubmit.services.gateway import HpsPayPlanService
from securesubmit.tests.test_data import TestServicesConfig


class PayPlanCustomerTests(unittest.TestCase):
    service = HpsPayPlanService(TestServicesConfig.valid_pay_plan_config, enable_logging=True)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def get_customer_identifier(self):
        return datetime.date.today().strftime('%Y%m%d') + '-SecureSubmit-' + ''.join(random.sample(self.alphabet, 10))

    def test_add_customer(self):
        new_customer = HpsPayPlanCustomer()
        new_customer.customer_identifier = self.get_customer_identifier()
        new_customer.first_name = 'Bill'
        new_customer.last_name = 'Johnson'
        new_customer.company = 'Heartland Payment Systems'
        new_customer.country = 'USA'
        new_customer.customer_status = HpsPayPlanCustomerStatus.ACTIVE

        response = self.service.add_customer(new_customer)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.customer_key)

    def test_edit_customer(self):
        results = self.service.page(1, 0).find_all_customers({'customerIdentifier': 'SecureSubmit'})
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) >= 1)

        # make the edit
        phone_day = '555' + ''.join(random.sample('0123456789', 7))
        customer = results.results[0]
        customer.phone_day = phone_day

        result = self.service.edit_customer(customer)
        self.assertIsNotNone(result)
        self.assertEqual(customer.customer_key, result.customer_key)
        self.assertEqual(phone_day, result.phone_day)

        # verify the edit
        result = self.service.get_customer(customer.customer_key)
        self.assertEqual(customer.customer_key, result.customer_key)
        self.assertEqual(phone_day, result.phone_day)

    def test_find_all_customers(self):
        results = self.service.find_all_customers()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) > 0)

    def test_find_all_customers_with_paging(self):
        results = self.service.page(1, 0).find_all_customers()
        self.assertIsNotNone(results)
        self.assertEqual(1, len(results.results))

    def test_find_all_customers_with_filters(self):
        results = self.service.find_all_customers({'customerIdentifier': 'SecureSubmit'})
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) >= 1)

    def test_get_customer_by_customer(self):
        results = self.service.page(1, 0).find_all_customers()
        self.assertIsNotNone(results)
        self.assertEqual(1, len(results.results))

        customer = self.service.get_customer(results.results[0])
        self.assertIsNotNone(customer)
        self.assertEqual(results.results[0].customer_key, customer.customer_key)

    def test_get_customer_by_key(self):
        results = self.service.page(1, 0).find_all_customers()
        self.assertIsNotNone(results)
        self.assertEqual(1, len(results.results))

        customer = self.service.get_customer(results.results[0].customer_key)
        self.assertIsNotNone(customer)
        self.assertEqual(results.results[0].customer_key, customer.customer_key)

    def test_delete_customer_by_customer(self):
        self.test_add_customer()

        results = self.service.page(1, 0).find_all_customers()
        self.assertIsNotNone(results)
        self.assertEqual(1, len(results.results))

        customer = self.service.delete_customer(results.results[0])
        self.assertIsNone(customer)

    def test_delete_customer_by_key(self):
        self.test_add_customer()

        results = self.service.page(1, 0).find_all_customers()
        self.assertIsNotNone(results)
        self.assertEqual(1, len(results.results))

        customer = self.service.delete_customer(results.results[0].customer_key)
        self.assertIsNone(customer)