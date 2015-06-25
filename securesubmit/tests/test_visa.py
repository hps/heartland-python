import unittest

from securesubmit.entities.credit import HpsCPCData
from securesubmit.infrastructure.enums import HpsTaxType
from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsCreditException,
            HpsTransactionDetails)


class VisaTests(unittest.TestCase):
    charge_service = HpsCreditService(
        TestServicesConfig.valid_services_config)

    def test_visa_should_charge(self):
        response = self._charge_valid_visa(50)
        self.assertEqual("00", response.response_code)

    def test_visa_with_details(self):
        details = HpsTransactionDetails()
        details.memo = 'memo'
        details.invoice_number = '1234'
        details.customer_id = 'customerID'

        charge = self.charge_service.charge(
            50, 'usd',
            TestCreditCard.valid_visa,
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
    def test_visa_avs_response_b(self):
        response = self._charge_valid_visa(91.01)
        self.assertEqual("B", response.avs_result_code)

    def test_visa_avs_response_c(self):
        response = self._charge_valid_visa(91.02)
        self.assertEqual("C", response.avs_result_code)

    def test_visa_avs_response_d(self):
        response = self._charge_valid_visa(91.03)
        self.assertEqual("D", response.avs_result_code)

    def test_visa_avs_response_i(self):
        response = self._charge_valid_visa(91.05)
        self.assertEqual("I", response.avs_result_code)

    def test_visa_avs_response_m(self):
        response = self._charge_valid_visa(91.06)
        self.assertEqual("M", response.avs_result_code)

    def test_visa_avs_response_p(self):
        response = self._charge_valid_visa(91.07)
        self.assertEqual("P", response.avs_result_code)

    # CVV Tests
    def test_visa_cvv_response_m(self):
        response = self._charge_valid_visa(96.01)
        self.assertEqual("M", response.cvv_result_code)

    def test_visa_cvv_response_n(self):
        response = self._charge_valid_visa(96.02)
        self.assertEqual("N", response.cvv_result_code)

    def test_visa_cvv_response_p(self):
        response = self._charge_valid_visa(96.03)
        self.assertEqual("P", response.cvv_result_code)

    def test_visa_cvv_response_s(self):
        response = self._charge_valid_visa(96.04)
        self.assertEqual("S", response.cvv_result_code)

    def test_visa_cvv_response_u(self):
        response = self._charge_valid_visa(96.05)
        self.assertEqual("U", response.cvv_result_code)

    # Visa to Visa 2nd
    # def test_visa_response_1033(self):
    #     try:
    #         self._charge_valid_visa(10.33)
    #     except HpsCreditException, e:
    #         self.assertEqual(HpsExceptionCodes.card_declined, e.code)
    #         return
    #
    #     self.fail("No exception was thrown.")

    def test_visa_response_refer_card_issuer(self):
        try:
            self._charge_valid_visa(10.34)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_merchant(self):
        try:
            self._charge_valid_visa(10.22)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_pickup_card(self):
        try:
            self._charge_valid_visa(10.04)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_do_not_honor(self):
        try:
            self._charge_valid_visa(10.25)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_transaction(self):
        try:
            self._charge_valid_visa(10.26)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_amount(self):
        try:
            self._charge_valid_visa(10.27)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.invalid_amount, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_card(self):
        try:
            self._charge_valid_visa(10.28)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_number, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_issuer(self):
        try:
            self._charge_valid_visa(10.18)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_system_error_reenter(self):
        try:
            self._charge_valid_visa(10.29)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_lost_card(self):
        try:
            self._charge_valid_visa(10.31)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_hot_card_pickup(self):
        try:
            self._charge_valid_visa(10.03)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_insufficient_funds(self):
        try:
            self._charge_valid_visa(10.08)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_no_check_amount(self):
        try:
            self._charge_valid_visa(10.16)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_no_savings_account(self):
        try:
            self._charge_valid_visa(10.17)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_expired_card(self):
        try:
            self._charge_valid_visa(10.32)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.expired_card, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_txn_not_permitted(self):
        try:
            self._charge_valid_visa(10.30)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_invalid_aquirer(self):
        try:
            self._charge_valid_visa(10.30)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_exceeds_limit(self):
        try:
            self._charge_valid_visa(10.09)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_restricted_card(self):
        try:
            self._charge_valid_visa(10.10)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_security_violation(self):
        try:
            self._charge_valid_visa(10.11)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.card_declined, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_check_digit_err(self):
        try:
            self._charge_valid_visa(10.05)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_cvc, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_system_error(self):
        try:
            self._charge_valid_visa(10.21)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.processing_error, e.code)
            return

        self.fail("No exception was thrown.")

    def test_visa_response_cvv2_mismatch(self):
        try:
            self._charge_valid_visa(10.23)
        except HpsCreditException, e:
            self.assertEqual(HpsExceptionCodes.incorrect_cvc, e.code)
            return

        self.fail("No exception was thrown.")

    # Verify, Authorize & Capture
    def test_visa_verify(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual("85", response.response_code)

    def test_visa_edit(self):
        auth_response = self.charge_service.authorize(
            50, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual('00', auth_response.response_code)

        edit_response = self.charge_service.edit(
            auth_response.transaction_id, 55, 5)
        self.assertEqual('00', edit_response.response_code)

    def test_visa_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", response.response_code)

    def test_visa_token_authorize(self):
        response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder, True)
        self.assertEqual('0', response.token_data.token_rsp_code)
        self.assertEqual("00", response.response_code)

    def test_visa_capture(self):
        # Authorize the card.
        auth_response = self.charge_service.authorize(
            50, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        self.assertEqual("00", auth_response.response_code)

        # Capture the authorization.
        capture_response = self.charge_service.capture(
            auth_response.transaction_id)
        self.assertEqual("00", capture_response.response_code)

    # test CPC stuff
    def test_visa_charge_cpc_req_should_return_business(self):
        """
        Visa charge and CPC Req should return cpcIndicator 'B'.
        """
        charge_response = self.charge_service.charge(
            112.34, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            cpc_req=True
        )
        self.assertEquals('00', charge_response.response_code)
        self.assertEquals('B', charge_response.cpc_indicator)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '123456789'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = '15'

        edit_response = self.charge_service.cpc_edit(charge_response.transaction_id, cpc_data)
        self.assertEquals('00', edit_response.response_code)

    def test_visa_charge_cpc_req_should_return_corporate(self):
        """
        Visa charge and CPC Req should return cpcIndicator 'R'.
        """
        charge_response = self.charge_service.charge(
            123.45, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            cpc_req=True
        )
        self.assertEquals('00', charge_response.response_code)
        self.assertEquals('R', charge_response.cpc_indicator)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '123456789'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = '15'

        edit_response = self.charge_service.cpc_edit(charge_response.transaction_id, cpc_data)
        self.assertEquals('00', edit_response.response_code)

    def test_visa_charge_cpc_req_should_return_purchasing(self):
        """
        Visa charge and CPC Req should return cpcIndicator 'S'.
        """
        charge_response = self.charge_service.charge(
            134.56, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            cpc_req=True
        )
        self.assertEquals('00', charge_response.response_code)
        self.assertEquals('S', charge_response.cpc_indicator)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '123456789'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = '15'

        edit_response = self.charge_service.cpc_edit(charge_response.transaction_id, cpc_data)
        self.assertEquals('00', edit_response.response_code)

    def test_visa_auth_cpc_req_should_return_business(self):
        """
        Visa auth and CPC Req should return cpcIndicator 'B'.
        """
        charge_response = self.charge_service.authorize(
            112.34, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            cpc_req=True
        )
        self.assertEquals('00', charge_response.response_code)
        self.assertEquals('B', charge_response.cpc_indicator)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '123456789'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = '15'

        edit_response = self.charge_service.cpc_edit(charge_response.transaction_id, cpc_data)
        self.assertEquals('00', edit_response.response_code)

    def test_visa_auth_cpc_req_should_return_corporate(self):
        """
        Visa auth and CPC Req should return cpcIndicator 'R'.
        """
        charge_response = self.charge_service.authorize(
            123.45, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            cpc_req=True
        )
        self.assertEquals('00', charge_response.response_code)
        self.assertEquals('R', charge_response.cpc_indicator)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '123456789'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = '15'

        edit_response = self.charge_service.cpc_edit(charge_response.transaction_id, cpc_data)
        self.assertEquals('00', edit_response.response_code)

    def test_visa_auth_cpc_req_should_return_purchasing(self):
        """
        Visa auth and CPC Req should return cpcIndicator 'S'.
        """
        charge_response = self.charge_service.authorize(
            134.56, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder,
            cpc_req=True
        )
        self.assertEquals('00', charge_response.response_code)
        self.assertEquals('S', charge_response.cpc_indicator)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '123456789'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = '15'

        edit_response = self.charge_service.cpc_edit(charge_response.transaction_id, cpc_data)
        self.assertEquals('00', edit_response.response_code)

    # Helper Methods
    def _charge_valid_visa(self, amount):
        response = self.charge_service.charge(
            amount, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.valid_card_holder)
        if response is None:
            self.fail("Response is None")

        return response