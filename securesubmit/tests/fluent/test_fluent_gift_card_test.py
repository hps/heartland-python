import unittest

from securesubmit.infrastructure import HpsArgumentException
from securesubmit.services.fluent.gateway import HpsFluentGiftCardService
from securesubmit.tests.test_data import TestServicesConfig, TestGiftCard


class FluentGiftCardTests(unittest.TestCase):
    service = HpsFluentGiftCardService().with_config(TestServicesConfig.valid_services_config)

    def test_activate(self):
        response = self.service.activate(100)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_activate_no_card(self):
        builder = self.service.activate(100)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_activate_no_amount(self):
        builder = self.service.activate().with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_activate_no_currency(self):
        builder = self.service.activate(100)\
            .with_currency(None)\
            .with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_add_value(self):
        response = self.service.add_value(100)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_add_value_no_card(self):
        builder = self.service.add_value(100)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_add_value_no_amount(self):
        builder = self.service.add_value().with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_add_value_no_currency(self):
        builder = self.service.add_value(100)\
            .with_currency(None)\
            .with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_balance(self):
        response = self.service.balance()\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_balance_no_card(self):
        builder = self.service.balance()
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_deactivate(self):
        response = self.service.deactivate()\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_deactivate_no_card(self):
        builder = self.service.deactivate()
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_replace(self):
        response = self.service.replace()\
            .with_old_card(TestGiftCard.valid_gift_card_manual)\
            .with_new_card(TestGiftCard.valid_gift_card_manual_2)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_replace_no_old_card(self):
        builder = self.service.replace().with_new_card(TestGiftCard.valid_gift_card_manual_2)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_replace_no_new_card(self):
        builder = self.service.replace().with_old_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_by_card(self):
        sale = self.service.sale(10)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

        response = self.service.reverse()\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .with_amount(10)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_reverse_by_transaction_id(self):
        sale = self.service.sale(10)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

        response = self.service.reverse(10)\
            .with_transaction_id(sale.transaction_id)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_reverse_no_amount(self):
        builder = self.service.reverse().with_transaction_id('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_multiple_payment_options(self):
        builder = self.service.reverse(10)\
            .with_transaction_id('123456')\
            .with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_no_payment_option(self):
        builder = self.service.reverse(10)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reward(self):
        response = self.service.reward(12)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_reward_no_card(self):
        builder = self.service.reward(100)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reward_no_amount(self):
        builder = self.service.reward().with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reward_no_currency(self):
        builder = self.service.reward(100)\
            .with_currency(None)\
            .with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_sale(self):
        sale = self.service.sale(10)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

    def test_sale_no_card(self):
        builder = self.service.sale(100)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_sale_no_amount(self):
        builder = self.service.sale().with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_sale_no_currency(self):
        builder = self.service.sale(100)\
            .with_currency(None)\
            .with_card(TestGiftCard.valid_gift_card_manual)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_void(self):
        sale = self.service.sale(10)\
            .with_card(TestGiftCard.valid_gift_card_manual)\
            .execute()
        self.assertIsNotNone(sale)
        self.assertEqual('0', sale.response_code)

        response = self.service.void()\
            .with_transaction_id(sale.transaction_id)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_void_no_transaction_id(self):
        builder = self.service.void()
        self.assertRaises(HpsArgumentException, builder.execute)