import unittest

from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsCreditException,
            HpsTransactionDetails)


class MasterCardTests(unittest.TestCase):

    charge_service = HpsCreditService(TestServicesConfig.valid_services_config)

    def test_mastercard_charge(self):
        response = self._charge_valid_mastercard(50)
        self.assertEqual(response.response_code, "00")

    def test_visa_with_details(self):
        details = HpsTransactionDetails()
        details.memo = 'memo'
        details.invoice_number = '1234'
        details.customer_id = 'customerID'

        charge = self.charge_service.charge(
            50, 'usd',
            TestCreditCard.valid_mastercard,
            TestCardHolder.valid_card_holder,
            False, 'descriptor', False,
            details)

        self.assertIsNotNone(charge)

        transaction = self.charge_service.get(charge.transaction_id)
        self.assertIsNotNone(transaction)
        self.assertEquals(transaction.memo, 'memo')
        self.assertEquals(transaction.invoice_number, '1234')
        self.assertEquals(transaction.customer_id, 'customerID')

    # AVS Tests
    def test_mastercard_avs_response_A(self):
        response = self._charge_valid_mastercard(90.01)
        self.assertEqual(response.avs_result_code, "A")

    def test_mastercard_avs_response_N(self):
        response = self._charge_valid_mastercard(90.02)
        self.assertEqual(response.avs_result_code, "N")

    def test_mastercard_avs_response_R(self):
        response = self._charge_valid_mastercard(90.03)
        self.assertEqual(response.avs_result_code, "R")

    def test_mastercard_avs_response_S(self):
        response = self._charge_valid_mastercard(90.04)
        self.assertEqual(response.avs_result_code, "S")

    def test_mastercard_avs_response_U(self):
        response = self._charge_valid_mastercard(90.05)
        self.assertEqual(response.avs_result_code, "U")

    def test_mastercard_avs_response_W(self):
        response = self._charge_valid_mastercard(90.06)
        self.assertEqual(response.avs_result_code, "W")

    def test_mastercard_avs_response_X(self):
        response = self._charge_valid_mastercard(90.07)
        self.assertEqual(response.avs_result_code, "X")

    def test_mastercard_avs_response_Y(self):
        response = self._charge_valid_mastercard(90.08)
        self.assertEqual(response.avs_result_code, "Y")

    def test_mastercard_avs_response_Z(self):
        response = self._charge_valid_mastercard(90.09)
        self.assertEqual(response.avs_result_code, "Z")

    # CVV Tests
    def test_mastercard_cvv_response_M(self):
        response = self._charge_valid_mastercard(95.01)
        self.assertEqual(response.cvv_result_code, "M")

    def test_mastercard_cvv_response_N(self):
        response = self._charge_valid_mastercard(95.02)
        self.assertEqual(response.cvv_result_code, "N")

    def test_mastercard_cvv_response_P(self):
        response = self._charge_valid_mastercard(95.03)
        self.assertEqual(response.cvv_result_code, "P")

    def test_mastercard_cvv_response_U(self):
        response = self._charge_valid_mastercard(95.04)
        self.assertEqual(response.cvv_result_code, "U")

    # mastercard responses
    def test_mastercard_response_refer_card_issuer(self):
        try:
            response = self._charge_valid_mastercard(10.34)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_term_id_error(self):
        try:
            response = self._charge_valid_mastercard(10.22)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_invalid_merchant(self):
        try:
            response = self._charge_valid_mastercard(10.01)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_do_not_honor(self):
        try:
            response = self._charge_valid_mastercard(10.25)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_invalid_transaction(self):
        try:
            response = self._charge_valid_mastercard(10.26)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_invalid_amount(self):
        try:
            response = self._charge_valid_mastercard(10.27)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.invalid_amount, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_invalid_card(self):
        try:
            response = self._charge_valid_mastercard(10.28)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_invalid_issuer(self):
        try:
            response = self._charge_valid_mastercard(10.18)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_lost_card(self):
        try:
            response = self._charge_valid_mastercard(10.31)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_hold_call(self):
        try:
            response = self._charge_valid_mastercard(10.03)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_decline(self):
        try:
            response = self._charge_valid_mastercard(10.08)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_expired_card(self):
        try:
            response = self._charge_valid_mastercard(10.32)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.expired_card, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_exceeds_limit(self):
        try:
            response = self._charge_valid_mastercard(10.09)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_restricted_card(self):
        try:
            response = self._charge_valid_mastercard(10.10)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_security_violation(self):
        try:
            response = self._charge_valid_mastercard(10.19)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_exceeds_freq_limit(self):
        try:
            response = self._charge_valid_mastercard(10.11)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_card_no_error(self):
        try:
            response = self._charge_valid_mastercard(10.14)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_invalid_account(self):
        try:
            response = self._charge_valid_mastercard(10.06)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_mastercard_response_system_error(self):
        try:
            response = self._charge_valid_mastercard(10.21)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    # Verify, Authorize, Refund & Capture
    def test_mastercard_verify(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_mastercard,
            TestCardHolder.valid_card_holder)
        self.assertEqual("85", response.response_code)

    def test_mastercard_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", response.response_code)

    def test_mastercard_token_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.valid_card_holder, True)
        self.assertEqual('0', response.token_data.token_rsp_code)
        self.assertEqual("00", response.response_code)

    def test_mastercard_refund(self):
        chargeResponse = self.charge_service.charge(
            25, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip_no_street)
        refundResponse = self.charge_service.refund(
            25, "usd",
            chargeResponse.transaction_id)
        self.assertEqual(refundResponse.response_code, '00')

    def test_mastercard_capture(self):
        # Authorize the card.
        authResponse = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", authResponse.response_code)
        # Capture the authorization.
        captureResponse = self.charge_service.capture(
            authResponse.transaction_id)
        self.assertEqual("00", captureResponse.response_code)

    def _charge_valid_mastercard(self, amt):
        response = self.charge_service.charge(
            amt, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.valid_card_holder)
        if response is None:
            self.fail("Response is null.")
        return response
