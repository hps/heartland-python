import unittest
import copy

from securesubmit.tests.test_data import (
    TestServicesConfig,
    TestCreditCard,
    TestCardHolder
)
from securesubmit.services.gateway import (
    HpsCreditService,
    HpsCreditCard,
    HpsArgumentException
)
from securesubmit.services.token import HpsTokenService


class TokenServiceTests(unittest.TestCase):
    token_service = HpsTokenService(TestServicesConfig.valid_services_config.credential_token)

    def test_null_public_key(self):
        with self.assertRaises(HpsArgumentException):
            HpsTokenService(None)

    def test_empty_public_key(self):
        with self.assertRaises(HpsArgumentException):
            HpsTokenService('')

    def test_malformed_public_key(self):
        with self.assertRaises(HpsArgumentException):
            HpsTokenService('pkapi_bad')

    def test_bad_public_key(self):
        token = HpsTokenService('pkapi_foo_foo').get_token(TestCreditCard.valid_visa)
        self.assertIsNotNone(token)

    def test_validation_invalid_card_number(self):
        card = HpsCreditCard()
        card.number = '1'

        response = self.token_service.get_token(card)
        error = response.error

        self.assertIsNotNone(error)
        self.assertEqual('2', error.code)
        self.assertEqual('card.number', error.param)
        self.assertEqual('Card number is invalid.', error.message)

    def test_validation_long_card_number(self):
        card = HpsCreditCard()
        card.number = '11111111111111111111111111111111111'

        response = self.token_service.get_token(card)
        error = response.error

        self.assertIsNotNone(error)
        self.assertEqual('2', error.code)
        self.assertEqual('card.number', error.param)
        self.assertEqual('Card number is invalid.', error.message)

    def test_validation_high_exp_month(self):
        card = copy.deepcopy(TestCreditCard.valid_visa)
        card.exp_month = 13

        response = self.token_service.get_token(card)
        error = response.error

        self.assertIsNotNone(error)
        self.assertEqual('2', error.code)
        self.assertEqual('card.exp_month', error.param)
        self.assertEqual('Card expiration month is invalid.', error.message)

    def test_validation_low_exp_year(self):
        card = copy.deepcopy(TestCreditCard.valid_visa)
        card.exp_year = 12

        response = self.token_service.get_token(card)
        error = response.error

        self.assertIsNotNone(error)
        self.assertEqual('2', error.code)
        self.assertEqual('card.exp_year', error.param)
        self.assertEqual('Card expiration year is invalid.', error.message)

    def test_validation_year_under_2000(self):
        card = copy.deepcopy(TestCreditCard.valid_visa)
        card.exp_year = 1999

        response = self.token_service.get_token(card)
        error = response.error

        self.assertIsNotNone(error)
        self.assertEqual('2', error.code)
        self.assertEqual('card.exp_year', error.param)
        self.assertEqual('Card expiration year is invalid.', error.message)

    def test_token_result(self):
        response = self.token_service.get_token(TestCreditCard.valid_visa)
        self.assertIsNone(response.error)

    def test_token_data_result(self):
        response = self.token_service.get_token(TestCreditCard.valid_visa)
        self.assertIsNotNone(response.token_value)
        self.assertIsNotNone(response.token_type)
        self.assertIsNotNone(response.token_expire)

    def test_token_charge(self):
        token = self.token_service.get_token(TestCreditCard.valid_visa)
        charge_service = HpsCreditService(TestServicesConfig.valid_services_config)
        charge = charge_service.charge(4, 'USD', token.token_value, TestCardHolder.valid_card_holder)

        self.assertIsNotNone(charge)
        self.assertEqual('00', charge.response_code)

    def test_swipe_token(self):
        swipe_data = '.11%B4012001000000016^VI TEST CREDIT^251210100000000000000000?|mc7vPHGGYh79DuD2Ys0ELhubZcP7dIsNaxQlRF243dIX5kfXEnQKaciND|+++++++JnvkN4mBa11;4012001000000016=25121010000000000000?|kON4LjKZ+tcDZcIef/W2H7oRDw|+++++++JnvkN4mBa00||/wECAQECAoFGAgEH3wEeShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0TBtEt4SQvyC03zgmcS/4rnZdMpF+4mJT6EYuyDKC+WJAMG4+cSiWOGHtqwaK6edyzqosTPLavpdRat7z2dVX/SM3//TXLGGrSIayLW6Zmatbw4MT0KtBuyYaKX74E4v2L2PhItHv7m6rm2xGu2yTPmCvm9yFTouljvhF3Klx8rUAn0o0zCVAE9sl/iix+qqnTLEvgd/XXpaiYwyQoKSkkZGVX7QP'
        token = self.token_service.get_swipe_token(swipe_data)
        self.assertIsNotNone(token)

        charge_service = HpsCreditService(TestServicesConfig.valid_services_config)
        charge = charge_service.charge(3, 'USD', token.token_value, TestCardHolder.valid_card_holder)

        self.assertIsNotNone(charge)
        self.assertEqual('00', charge.response_code)

    def test_encrypted_card_token(self):
        track = '4012007060016=2512101hX3JZdqcwEOaoUry'
        ktb = '/wECAQEEAoFGAgEH3ggDTDT6jRZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0MCtomwyCdnN+qr1I/SvhXbgOurdPKxkAyrmBQkzS/0UB6HWpdN1nc4IXcgB7tuVAs4fRjIlYOTIWNjf10bwciwD3m1JNoDMtvoXggaN7dLI7uuA+jYzt0gAmzgB3QqUFY0k7awOm923RJhnVaWUBJv9jL3+gvFNzZ+CiYbJH3BoArnCvWJbn/ohfnlJ6bA+GPC2fJlQkizQXbrRoF+pbcezCaY9W'
        token = self.token_service.get_track_token(track, '02', ktb)
        self.assertIsNotNone(token)

        charge_service = HpsCreditService(TestServicesConfig.valid_services_config)
        charge = charge_service.charge(2, 'USD', token.token_value, TestCardHolder.valid_card_holder)

        self.assertIsNotNone(charge)
        self.assertEqual('00', charge.response_code)