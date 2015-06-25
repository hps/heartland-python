import unittest

from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService,
            HpsExceptionCodes,
            HpsException,
            HpsBatchService,
            HpsDirectMarketData,
            HpsCPCData)
from securesubmit.infrastructure.enums import HpsTaxType


class BatchCertTests(unittest.TestCase):
    batch_service = HpsBatchService(TestServicesConfig.valid_services_config)
    charge_service = HpsCreditService(TestServicesConfig.valid_services_config)
    direct_marketing = HpsDirectMarketData('123456')

    def test_inline_certification(self):
        self.batch_should_close_ok()

        self.visa_should_verify_ok()
        self.mastercard_should_verify_ok()
        self.discover_should_verify_ok()
        self.amex_avs_should_verify_ok()

        # self.visa_balance_inquiry()

        self.visa_should_charge_ok()
        self.mastercard_should_charge_ok()
        self.discover_should_charge_ok()
        self.amex_should_charge_ok()
        self.jcb_should_charge_ok()

        self.visa_should_auth_ok()
        self.mastercard_should_auth_ok()
        self.discover_should_auth_ok()
        self.visa_should_capture_ok()
        self.mastercard_should_capture_ok()

        self.visa_partial_approval()
        self.discover_partial_approval()
        self.mastercard_partial_approval()

        self.visa_level_ii_no_tax_should_response_b()
        self.visa_level_ii_tax_should_response_b()
        self.visa_level_ii_exempt_should_response_r()
        self.visa_level_ii_should_response_s()
        self.mastercard_level_ii_no_tax_should_response_s()
        self.mastercard_level_ii_tax_no_po_should_response_s()
        self.mastercard_level_ii_tax_with_po_should_response_s()
        self.mastercard_level_ii_exempt_should_response_s()
        self.amex_level_ii_no_tax()
        self.amex_level_ii_tax_no_po()
        self.amex_level_ii_tax_with_po()
        self.amex_level_ii_exempt()

        self.mastercard_should_return_ok()
        self.visa_should_reverse_ok()
        self.mastercard_should_reverse_ok()

        self.batch_should_close_ok()

    def batch_should_close_ok(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")
            print 'batch id: {0}'.format(response.id)
            print 'sequence number: {0}'.format(response.sequence_number)
        except HpsException, e:
            if e.code != HpsExceptionCodes.no_open_batch:
                self.fail("Something failed other than 'no open batch'.")

    """ card verify """

    def visa_should_verify_ok(self):
        response = self.charge_service.verify(TestCreditCard.valid_visa)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def mastercard_should_verify_ok(self):
        response = self.charge_service.verify(TestCreditCard.valid_mastercard)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def discover_should_verify_ok(self):
        response = self.charge_service.verify(TestCreditCard.valid_discover)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "85")

    def amex_avs_should_verify_ok(self):
        response = self.charge_service.verify(
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, '00')

    # def visa_balance_inquiry(self):
    #     response = self.charge_service.balance_inquiry(TestCreditCard.valid_visa)
    #     if response is None:
    #         self.fail("Response is None")
    #
    #     self.assertEqual(response.response_code, '00')

    """ sale (for multi use token) """

    def visa_should_charge_ok(self):
        response = self.charge_service.charge(
            17.01, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_short_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def mastercard_should_charge_ok(self):
        response = self.charge_service.charge(
            17.02, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def discover_should_charge_ok(self):
        response = self.charge_service.charge(
            17.03, "usd",
            TestCreditCard.valid_discover,
            TestCardHolder.cert_holder_long_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def amex_should_charge_ok(self):
        response = self.charge_service.charge(
            17.04, "usd",
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def jcb_should_charge_ok(self):
        response = self.charge_service.charge(
            17.05, "usd",
            TestCreditCard.valid_jcb,
            TestCardHolder.cert_holder_long_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    """ authorization (delayed capture) """

    _visa_auth_txn_id = None
    _mc_auth_txn_id = None
    _discover_auth_txn_id = None

    def visa_should_auth_ok(self):
        response = self.charge_service.authorize(
            17.06, "usd",
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_short_zip)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")
        self._visa_auth_txn_id = response.transaction_id

    def mastercard_should_auth_ok(self):
        response = self.charge_service.authorize(
            17.07, "usd",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")
        self._mc_auth_txn_id = response.transaction_id

    def discover_should_auth_ok(self):
        response = self.charge_service.authorize(
            17.08, "usd",
            TestCreditCard.valid_discover,
            TestCardHolder.cert_holder_long_zip_no_street)
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")
        self._discover_auth_txn_id = response.transaction_id

    def visa_should_capture_ok(self):
        response = self.charge_service.capture(
            self._visa_auth_txn_id,
            '17.06')
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

    def mastercard_should_capture_ok(self):
        response = self.charge_service.capture(
            self._mc_auth_txn_id,
            '17.07')
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

    """ partially - approved sale """

    def visa_partial_approval(self):
        response = self.charge_service.charge(
            130.00, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_short_zip_no_street,
            allow_partial_auth=True,
            direct_market_data=self.direct_marketing
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '10')
        self.assertEqual(response.authorized_amount, '110.00')

    def discover_partial_approval(self):
        response = self.charge_service.charge(
            145.00, 'usd',
            TestCreditCard.valid_discover,
            TestCardHolder.cert_holder_short_zip_no_street,
            allow_partial_auth=True,
            direct_market_data=self.direct_marketing
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '10')

    partial_auth_transaction_id = None
    def mastercard_partial_approval(self):
        response = self.charge_service.charge(
            155.00, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_short_zip_no_street,
            allow_partial_auth=True,
            direct_market_data=self.direct_marketing
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '10')
        self.assertEqual(response.authorized_amount, '100.00')
        self.partial_auth_transaction_id = response.transaction_id

    """ level II corporate purchase card """

    def visa_level_ii_no_tax_should_response_b(self):
        response = self.charge_service.charge(
            112.34, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.not_used)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def visa_level_ii_tax_should_response_b(self):
        response = self.charge_service.charge(
            111.34, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('', HpsTaxType.sales_tax, 1.0)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def visa_level_ii_exempt_should_response_r(self):
        response = self.charge_service.charge(
            123.45, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('', HpsTaxType.tax_exempt)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def visa_level_ii_should_response_s(self):
        response = self.charge_service.charge(
            133.56, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.sales_tax, 1.0)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def mastercard_level_ii_no_tax_should_response_s(self):
        response = self.charge_service.charge(
            111.06, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.not_used)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def mastercard_level_ii_tax_no_po_should_response_s(self):
        response = self.charge_service.charge(
            110.07, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('', HpsTaxType.sales_tax, 1.0)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def mastercard_level_ii_tax_with_po_should_response_s(self):
        response = self.charge_service.charge(
            110.08, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.sales_tax, 1.0)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def mastercard_level_ii_exempt_should_response_s(self):
        response = self.charge_service.charge(
            111.09, 'usd',
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip,
            cpc_req=True
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.tax_exempt)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def amex_level_ii_no_tax(self):
        response = self.charge_service.charge(
            111.10, 'usd',
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street,
            cpc_req=True
        )
        if response is None:
            self.fail('response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.not_used)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def amex_level_ii_tax_no_po(self):
        response = self.charge_service.charge(
            110.11, 'usd',
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street,
            cpc_req=True
        )
        if response is None:
            self.fail('response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('', HpsTaxType.sales_tax, 1.0)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def amex_level_ii_tax_with_po(self):
        response = self.charge_service.charge(
            110.12, 'usd',
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street,
            cpc_req=True
        )
        if response is None:
            self.fail('response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.sales_tax, 1.0)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    def amex_level_ii_exempt(self):
        response = self.charge_service.charge(
            111.13, 'usd',
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street,
            cpc_req=True
        )
        if response is None:
            self.fail('response is None')

        self.assertEqual(response.response_code, '00')

        edit_response = self.charge_service.cpc_edit(
            response.transaction_id,
            HpsCPCData('9876543210', HpsTaxType.tax_exempt)
        )
        if edit_response is None:
            self.fail('Edit response is None')

    """ returns """

    def mastercard_should_return_ok(self):
        response = self.charge_service.refund(
            '15.15',
            'usd',
            TestCreditCard.valid_mastercard)
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')

    """ online void / reversal """

    def visa_should_reverse_ok(self):
        response = self.charge_service.reverse(
            TestCreditCard.valid_visa,
            17.01, "usd")
        if response is None:
            self.fail("Response is None")

        self.assertEqual(response.response_code, "00")

    def mastercard_should_reverse_ok(self):
        response = self.charge_service.reverse(
            self.partial_auth_transaction_id,
            100.00, 'usd'
        )
        if response is None:
            self.fail('Response is None')

        self.assertEqual(response.response_code, '00')
