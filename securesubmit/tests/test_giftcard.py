import unittest

from securesubmit.tests.test_data \
    import (TestGiftCard, TestServicesConfig)
from securesubmit.services.gateway import HpsGiftCardService


class GiftCardTests(unittest.TestCase):
    gift_service = HpsGiftCardService(TestServicesConfig.valid_services_config, True)

    def test_gift_card_activate(self):
        response = self.gift_service.activate(
            100.00, 'usd',
            TestGiftCard.valid_gift_card_manual)
        if response is None:
            self.fail('Response is null.')

        self.assertEqual(response.response_code, '0')

    def test_gift_card_add_value(self):
        response = self.gift_service.add_value(
            10.00, 'usd',
            TestGiftCard.valid_gift_card_manual)
        if response is None:
            self.fail('Response is null.')

        self.assertEqual(response.response_code, '0')

    # def test_gift_card_alias(self):
    #    response = self.gift_service.alias(HpsGiftCardAliasAction.add,
    #                                       TestGiftCard.valid_gift_card_manual,
    #                                       '12345674890')
    #    if response is None:
    #        self.fail('Response is null.')

    #    self.assertEqual(response.response_code, '0')

    def test_gift_card_balance(self):
        response = self.gift_service.balance(
            TestGiftCard.valid_gift_card_manual)
        if response is None:
            self.fail('Response is null.')

        self.assertEqual(response.response_code, '0')

    def test_gift_card_deactivate(self):
        response = self.gift_service.deactivate(
            TestGiftCard.valid_gift_card_manual)
        if response is None:
            self.fail('Response is null.')

        self.assertEqual(response.response_code, '0')

    def test_gift_card_replace(self):
        response = self.gift_service.replace(
            TestGiftCard.valid_gift_card_manual,
            TestGiftCard.valid_gift_card_manual_2)

        if response is None:
            self.fail('Response is null.')

        self.assertEqual(response.response_code, '0')

    def test_gift_card_reward(self):
        response = self.gift_service.reward(
            TestGiftCard.valid_gift_card_manual, 10.00)
        if response is None:
            self.fail('Response is null.')

        self.assertEqual(response.response_code, '0')

    def test_gift_card_sale(self):
        response = self.gift_service.sale(
            TestGiftCard.valid_gift_card_manual, 10.00)
        if response is None:
            self.fail('Response is None')
        self.assertEqual(response.response_code, '0')

    def test_gift_card_void(self):
        sale_response = self.gift_service.sale(
            TestGiftCard.valid_gift_card_manual, 10.00)
        self.assertEqual(sale_response.response_code, '0')
        void_response = self.gift_service.void(
            sale_response.transaction_id)
        self.assertEqual(void_response.response_code, '0')

    def test_gift_card_reverse_by_txn(self):
        sale_response = self.gift_service.sale(
            TestGiftCard.valid_gift_card_manual, 10.00)
        self.assertEqual(sale_response.response_code, '0')
        reverse_response = self.gift_service.reverse(
            sale_response.transaction_id, 10.00)
        self.assertEqual(reverse_response.response_code, '0')

    def test_gift_card_reverse_by_card(self):
        sale_response = self.gift_service.sale(
            TestGiftCard.valid_gift_card_manual, 10.00)
        self.assertEqual(sale_response.response_code, '0')
        reverse_response = self.gift_service.reverse(
            TestGiftCard.valid_gift_card_manual, 10.00)
        self.assertEqual(reverse_response.response_code, '0')
