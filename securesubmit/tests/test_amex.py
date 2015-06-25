import unittest

from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsCreditException)
from securesubmit.services.token import HpsTokenService


class AmexTests(unittest.TestCase):
    charge_service = HpsCreditService(
        TestServicesConfig.valid_services_config)

    def test_amex_charge(self):
        response = self._charge_valid_amex(50)
        self.assertEqual(response.response_code, "00")

    # AVS Tests
    def test_amex_avs_response_a(self):
        response = self._charge_valid_amex(90.01)
        self.assertEqual(response.avs_result_code, "A")

    def test_amex_avs_response_n(self):
        response = self._charge_valid_amex(90.02)
        self.assertEqual(response.avs_result_code, "N")

    def test_amex_avs_response_r(self):
        response = self._charge_valid_amex(90.03)
        self.assertEqual(response.avs_result_code, "R")

    def test_amex_avs_response_s(self):
        response = self._charge_valid_amex(90.04)
        self.assertEqual(response.avs_result_code, "S")

    def test_amex_avs_response_u(self):
        response = self._charge_valid_amex(90.05)
        self.assertEqual(response.avs_result_code, "U")

    def test_amex_avs_response_w(self):
        response = self._charge_valid_amex(90.06)
        self.assertEqual(response.avs_result_code, "W")

    def test_amex_avs_response_x(self):
        response = self._charge_valid_amex(90.07)
        self.assertEqual(response.avs_result_code, "X")

    def test_amex_avs_response_y(self):
        response = self._charge_valid_amex(90.08)
        self.assertEqual(response.avs_result_code, "Y")

    def test_amex_avs_response_z(self):
        response = self._charge_valid_amex(90.09)
        self.assertEqual(response.avs_result_code, "Z")

    # CVV Tests
    def test_amex_cvv_response_m(self):
        response = self._charge_valid_amex(97.01)
        self.assertEqual(response.cvv_result_code, "M")

    def test_amex_cvv_response_n(self):
        response = self._charge_valid_amex(97.02)
        self.assertEqual(response.cvv_result_code, "N")

    def test_amex_cvv_response_p(self):
        response = self._charge_valid_amex(97.03)
        self.assertEqual(response.cvv_result_code, "P")

    def test_amex_token_cvv_response_m(self):
        response = self._charge_valid_amex_token(97.01)
        self.assertEqual(response.cvv_result_code, "M")

    def test_amex_token_cvv_response_n(self):
        response = self._charge_valid_amex_token(97.02)
        self.assertEqual(response.cvv_result_code, "N")

    def test_amex_token_cvv_response_p(self):
        response = self._charge_valid_amex_token(97.03)
        self.assertEqual(response.cvv_result_code, "P")

    # Amex to Visa 2nd
    def test_amex_response_denied(self):
        try:
            self._charge_valid_amex(10.08)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_card_expired(self):
        try:
            self._charge_valid_amex(10.32)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.expired_card, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_please_call(self):
        try:
            self._charge_valid_amex(10.34)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_invalid_merchant(self):
        try:
            self._charge_valid_amex(10.22)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_invalid_amount(self):
        try:
            self._charge_valid_amex(10.27)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.invalid_amount, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_no_action_taken(self):
        try:
            self._charge_valid_amex(10.14)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_invalid_cvv2(self):
        try:
            self._charge_valid_amex(10.23)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_cvc, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_message_format_error(self):
        try:
            self._charge_valid_amex(10.06)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_invalid_originator(self):
        try:
            self._charge_valid_amex(10.30)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_card_declined(self):
        try:
            self._charge_valid_amex(10.25)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_account_cancelled(self):
        try:
            self._charge_valid_amex(10.13)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_merchant_close(self):
        try:
            self._charge_valid_amex(10.12)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_amex_response_pickup_card(self):
        try:
            self._charge_valid_amex(10.04)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    # Verify, Authorize & Capture
    def test_amex_verify(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", response.response_code)

    def test_amex_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", response.response_code)

    def test_amex_token_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder, True)
        self.assertEqual('0', response.token_data.token_rsp_code)
        self.assertEqual("00", response.response_code)

    def test_amex_capture(self):
        # Authorize the card.
        auth_response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", auth_response.response_code)

        # Capture the authorization.
        capture_response = self.charge_service.capture(
            auth_response.transaction_id)
        self.assertEqual("00", capture_response.response_code)

    # Helper Method
    def _charge_valid_amex(self, amt):
        response = self.charge_service.charge(
            amt, "usd",
            TestCreditCard.valid_amex,
            TestCardHolder.valid_card_holder)
        if response is None:
            self.fail("Response is null.")

        return response

    def _charge_valid_amex_token(self, amt):
        token_service = HpsTokenService(TestServicesConfig.valid_services_config.credential_token)
        token_response = token_service.get_token(TestCreditCard.valid_amex)

        response = self.charge_service.charge(
            amt, 'usd',
            token_response.token_value,
            TestCardHolder.valid_card_holder)
        if response is None:
            self.fail('Response is null.')

        return response
