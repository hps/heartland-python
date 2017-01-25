import unittest

from securesubmit.entities import HpsTokenData
from securesubmit.infrastructure.enums import HpsPayPlanScheduleStatus
from securesubmit.services.gateway import HpsCreditService, HpsPayPlanService
from securesubmit.services.token import HpsTokenService
from securesubmit.tests.test_data import TestServicesConfig, TestCreditCard, TestCardHolder


class PayPlanRecurringTests(unittest.TestCase):
    credit_service = HpsCreditService(TestServicesConfig.valid_services_config, True)
    pp_service = HpsPayPlanService(TestServicesConfig.valid_pay_plan_config, True)
    schedules = pp_service.page(1, 0).find_all_schedules({
        'scheduleStatus': 'Active',
        'scheduleIdentifier': 'SecureSubmit'
    })
    schedule = None
    if len(schedules.results) > 0:
        schedule = schedules.results[0]

    def test_001_one_time_with_card(self):
        response = self.credit_service.recurring(
            TestCreditCard.valid_visa,
            10,
            self.schedule,
            TestCardHolder.valid_card_holder,
            True)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_002_one_time_with_token(self):
        token = self._get_token(TestCreditCard.valid_visa)
        response = self.credit_service.recurring(token, 10, self.schedule, None, True)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_003_one_time_with_payment_method_key(self):
        payment_method_key = self._get_payment_method_key()
        response = self.credit_service.recurring(payment_method_key, 10, self.schedule, None, True)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_004_with_card(self):
        response = self.credit_service.recurring(
            TestCreditCard.valid_visa,
            10,
            self.schedule,
            TestCardHolder.valid_card_holder)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_005_with_token(self):
        token = self._get_token(TestCreditCard.valid_visa)
        response = self.credit_service.recurring(token, 10, self.schedule)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_006_with_payment_method_key(self):
        payment_method_key = self._get_payment_method_key()
        response = self.credit_service.recurring(payment_method_key, 10, self.schedule)
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def _get_token(self, card, key=None):
        if key is not None and key != '':
            self.public_key = key
        else:
            self.public_key = TestServicesConfig.valid_services_config.credential_token

        self.token_service = HpsTokenService(self.public_key)
        token_response = self.token_service.get_token(card)
        if token_response.token_value is not None:
            token = HpsTokenData()
            token.token_value = token_response.token_value
            return token
        else:
            return token_response

    def _get_payment_method_key(self):
        return self.schedule.payment_method_key