import unittest
import random

from securesubmit.infrastructure import HpsArgumentException
from securesubmit.services.fluent.gateway import HpsFluentCheckService
from securesubmit.tests.test_data import TestServicesConfig, TestCheck


class FluentCheckTests(unittest.TestCase):
    service = HpsFluentCheckService().with_config(TestServicesConfig.valid_services_config)

    # def test_override(self):
    #     check = TestCheck.certification
    #
    #     sale = self.service.sale(10)\
    #         .with_check(check)\
    #         .execute()
    #
    #     self.assertIsNotNone(sale)
    #     self.assertEqual('0', sale.response_code)
    #
    #     override = self.service.override()\
    #         .with_check(check)\
    #         .with_amount(10)\
    #         .execute()
    #     self.assertIsNotNone(override)
    #     self.assertEqual('0', override.response_code)
    #
    # def test_override_no_amount(self):
    #     builder = self.service.override().with_check(TestCheck.certification)
    #     self.assertRaises(HpsArgumentException, builder.execute)
    #
    # def test_override_no_check(self):
    #     builder = self.service.override().with_amount(10)
    #     self.assertRaises(HpsArgumentException, builder.execute)
    #
    # def test_return(self):
    #     check = TestCheck.certification
    #
    #     sale = self.service.sale(11)\
    #         .with_check(check)\
    #         .execute()
    #
    #     self.assertIsNotNone(sale)
    #     self.assertEqual('0', sale.response_code)
    #
    #     response = self.service.return_check()\
    #         .with_check(check)\
    #         .execute()
    #     self.assertIsNotNone(response)
    #     self.assertEqual('0', response.response_code)
    #
    # def test_return_no_amount(self):
    #     builder = self.service.return_check().with_check(TestCheck.certification)
    #     self.assertRaises(HpsArgumentException, builder.execute)
    #
    # def test_return_no_check(self):
    #     builder = self.service.return_check().with_amount(10)
    #     self.assertRaises(HpsArgumentException, builder.execute)

    def test_sale(self):
        sale = self.service.sale(22)\
            .with_check(TestCheck.certification)\
            .execute()

        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

    def test_sale_no_amount(self):
        builder = self.service.return_check().with_check(TestCheck.certification)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_sale_no_check(self):
        builder = self.service.return_check().with_amount(10)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_void_with_transaction_id(self):
        sale = self.service.sale(23)\
            .with_check(TestCheck.certification)\
            .execute()

        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

        void = self.service.void()\
            .with_transaction_id(sale.transaction_id)\
            .execute()
        self.assertIsNotNone(void)
        self.assertEqual('0', void.response_code)

    def test_void_with_client_transaction_id(self):
        client_transaction_id = random.randint(100000000, 999999999)

        sale = self.service.sale(24)\
            .with_check(TestCheck.certification)\
            .with_client_transaction_id(str(client_transaction_id))\
            .execute()

        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

        void = self.service.void()\
            .with_client_transaction_id(sale.client_transaction_id)\
            .execute()
        self.assertIsNotNone(void)
        self.assertEqual('0', void.response_code)

    def test_void_multiple_transaction_ids(self):
        builder = self.service.void()\
            .with_transaction_id('54896311524')\
            .with_client_transaction_id('54896311524')
        self.assertRaises(HpsArgumentException, builder.execute)