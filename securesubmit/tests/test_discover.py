import unittest

from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsCreditException)


class DiscoverTests(unittest.TestCase):
    charge_service = HpsCreditService(TestServicesConfig.valid_services_config)

    def test_discover_charge(self):
        response = self._charge_valid_discover(50)
        self.assertEqual(response.response_code, '00')

    def test_discover_avs_response_A(self):
        response = self._charge_valid_discover(91.01)
        self.assertEqual(response.avs_result_code, 'A')

    def test_discover_avs_response_N(self):
        response = self._charge_valid_discover(91.02)
        self.assertEqual(response.avs_result_code, 'N')

    def test_discover_avs_response_R(self):
        response = self._charge_valid_discover(91.03)
        self.assertEqual(response.avs_result_code, 'R')

    def test_discover_avs_response_U(self):
        response = self._charge_valid_discover(91.05)
        self.assertEqual(response.avs_result_code, 'U')

    def test_discover_avs_response_Y(self):
        response = self._charge_valid_discover(91.06)
        self.assertEqual(response.avs_result_code, 'Y')

    def test_discover_avs_response_Z(self):
        response = self._charge_valid_discover(91.07)
        self.assertEqual(response.avs_result_code, 'Z')

    def test_discover_response_refer_card_issuer(self):
        try:
            response = self._charge_valid_discover(10.34)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return
        self.fail('No exception was thrown.')

    def test_discover_response_invalid_merchant(self):
        try:
            response = self._charge_valid_discover(10.22)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_pickup_card(self):
        try:
            response = self._charge_valid_discover(10.04)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_do_not_honor(self):
        try:
            response = self._charge_valid_discover(10.25)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_invalid_transaction(self):
        try:
            response = self._charge_valid_discover(10.26)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_invalid_amount(self):
        try:
            response = self._charge_valid_discover(10.27)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.invalid_amount, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_invalid_card(self):
        try:
            response = self._charge_valid_discover(10.28)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_invalid_issuer(self):
        try:
            response = self._charge_valid_discover(10.18)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_system_error_reenter(self):
        try:
            response = self._charge_valid_discover(10.29)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_message_format_error(self):
        try:
            response = self._charge_valid_discover(10.06)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_lost_card(self):
        try:
            response = self._charge_valid_discover(10.31)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_insufficient_funds(self):
        try:
            response = self._charge_valid_discover(10.08)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_no_savings_account(self):
        try:
            response = self._charge_valid_discover(10.17)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_expired_card(self):
        try:
            response = self._charge_valid_discover(10.32)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.expired_card, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_no_card_record(self):
        try:
            response = self._charge_valid_discover(10.24)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_txn_not_permitted(self):
        try:
            response = self._charge_valid_discover(10.20)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_invalid_aquirer(self):
        try:
            response = self._charge_valid_discover(10.30)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_exceeds_limit(self):
        try:
            response = self._charge_valid_discover(10.09)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_restricted_card(self):
        try:
            response = self._charge_valid_discover(10.10)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_security_violation(self):
        try:
            response = self._charge_valid_discover(10.19)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_exceeds_freq_limits(self):
        try:
            response = self._charge_valid_discover(10.11)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_no_to_account(self):
        try:
            response = self._charge_valid_discover(10.13)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_invalid_account(self):
        try:
            response = self._charge_valid_discover(10.14)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail('No exception was thrown.')

    def test_discover_response_system_error(self):
        try:
            response = self._charge_valid_discover(10.21)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail('No exception was thrown.')

    # Verify, Authorize & Capture
    def test_discover_verify(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_discover,
            TestCardHolder.valid_card_holder)
        self.assertEqual('85', response.response_code)

    def test_discover_authorize(self):
        response = self.charge_service.authorize(
            50, 'usd',
            TestCreditCard.valid_discover,
            TestCardHolder.valid_card_holder)
        self.assertEqual('00', response.response_code)

    def test_discover_token_authorization(self):
        response = self.charge_service.authorize(
            50, 'usd',
            TestCreditCard.valid_discover,
            TestCardHolder.valid_card_holder, True)
        self.assertEqual('0', response.token_data.token_rsp_code)
        self.assertEqual('00', response.response_code)

    def test_discover_capture(self):
        # Authorize the card.
        authResponse = self.charge_service.authorize(
            50, 'usd',
            TestCreditCard.valid_discover,
            TestCardHolder.valid_card_holder)
        self.assertEqual('00', authResponse.response_code)

        # Capture the authorization.
        captureResponse = self.charge_service.capture(
            authResponse.transaction_id)
        self.assertEqual('00', captureResponse.response_code)

    def _charge_valid_discover(self, amt):
        response = self.charge_service.charge(
            amt, 'usd',
            TestCreditCard.valid_discover,
            TestCardHolder.valid_card_holder)
        if response is None:
            self.fail('Response is null.')
        return response
