import unittest
from securesubmit.entities import HpsAddress
from securesubmit.entities.credit import HpsCardHolder, HpsCPCData
from securesubmit.entities.gift import HpsGiftCard
from securesubmit.infrastructure import HpsException
from securesubmit.infrastructure.enums import HpsTaxType
from securesubmit.services import HpsServicesConfig
from securesubmit.services.fluent.gateway import *
from securesubmit.services.gateway import HpsBatchService
from securesubmit.tests.certification import TestData


class RestauantTests(unittest.TestCase):
    config = HpsServicesConfig()
    config.secret_api_key = 'skapi_cert_MbKPAQCG-1QA2wtK44AP7Jhi4osTUmCXcNGyUWAYyw'
    config.developer_id = '012345'
    config.version_number = '0001'

    batch_service = HpsBatchService(config)
    service = HpsFluentCreditService().with_config(config)

    test_data = TestData('pkapi_cert_k2Abpf0NUzIpMjbH6G')

    use_tokens = True
    use_prepaid = True

    """ CLOSE BATCH """

    def test_000_close_batch(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")
            print 'batch id: {0}'.format(response.id)
            print 'sequence number: {0}'.format(response.sequence_number)
        except HpsException, e:
            self.fail(e.message)

    """ CREDIT CARD FUNCTIONS """

    """ CARD VERIFY """

    """ Account Verification """

    def test_001_card_verify_visa_swipe(self):
        response = self.service.verify()\
            .with_track_data(self.test_data.visa_swipe())\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('85', response.response_code)

    def test_002_card_verify_mastercard_swipe(self):
        response = self.service.verify()\
            .with_track_data(self.test_data.master_card_swipe())\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('85', response.response_code)

    def test_003_card_verify_discover_swipe(self):
        response = self.service.verify()\
            .with_track_data(self.test_data.discover_swipe())\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('85', response.response_code)

        """ Address Verification """

    def test_004_verify_amex(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.verify()\
            .with_card(self.test_data.amex_card(cvv=False))\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Balance Inquiry (for Prepaid Card) """

    def test_005_balance_inquiry_visa_swipe(self):
        response = self.service.prepaid_balance_inquiry()\
            .with_track_data(self.test_data.visa_swipe())\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ CREDIT SALE (For Multi-Use Token Only) """

    def test_006_charge_visa_swipe_token(self):
        response = self.service.charge(15.01)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_007_charge_mastercard_swipe_token(self):
        response = self.service.charge(15.02)\
            .with_track_data(self.test_data.master_card_swipe())\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_008_charge_discover_swipe_token(self):
        response = self.service.charge(15.03)\
            .with_track_data(self.test_data.discover_swipe())\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_009_charge_amex_swipe_token(self):
        response = self.service.charge(15.04)\
            .with_track_data(self.test_data.amex_swipe())\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ CREDIT SALE """

    """ Swiped """

    def test_010_charge_visa_swipe(self):
        response = self.service.charge(15.01)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(15.01).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    def test_011_charge_mastercard_swipe(self):
        response = self.service.charge(15.02)\
            .with_track_data(self.test_data.master_card_swipe())\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_012_charge_discover_swipe(self):
        response = self.service.charge(15.03)\
            .with_track_data(self.test_data.discover_swipe())\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_013_charge_amex_swipe(self):
        response = self.service.charge(15.04)\
            .with_track_data(self.test_data.amex_swipe())\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_014_charge_jcb_swipe(self):
        response = self.service.charge(15.05).with_track_data(self.test_data.jcb_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # TEST CASE 058
        return_response = self.service.refund(15.05).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(return_response)
        self.assertEqual('00', return_response.response_code)

    def test_015_charge_visa_swipe(self):
        response = self.service.charge(15.06).with_track_data(self.test_data.visa_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(15.06)\
            .with_auth_amount(5.06)\
            .with_transaction_id(response.transaction_id)\
            .execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    """ Manually Entered - Card Present """

    def test_016_charge_visa_manual_card_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '750241324'

        response = self.service.charge(16.01)\
            .with_card(self.test_data.visa_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_017_charge_mastercard_manual_card_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        response = self.service.charge(16.02)\
            .with_card(self.test_data.master_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(16.02).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    def test_018_charge_discover_manual_card_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '750241324'

        response = self.service.charge(16.03)\
            .with_card(self.test_data.discover_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_019_charge_visa_manual_card_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        response = self.service.charge(16.04)\
            .with_card(self.test_data.amex_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_020_charge_visa_manual_card_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(16.05)\
            .with_card(self.test_data.jcb_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_021_charge_discover_manual_card_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '750241324'

        response = self.service.charge(16.07)\
            .with_card(self.test_data.discover_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(16.07)\
            .with_auth_amount(6.07)\
            .with_transaction_id(response.transaction_id)\
            .execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    """ Manually Entered - Card Not Present """

    def test_022_charge_visa_manual_card_not_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '750241234'

        builder = self.service.charge(17.01)\
            .with_card_holder(card_holder)\

        if self.use_tokens:
            builder.with_token(self.test_data.visa_multi_use_token('retail'))
        else:
            builder.with_card(self.test_data.visa_card())

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_023_charge_mastercard_manual_card_not_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        builder = self.service.charge(17.02)\
            .with_card_holder(card_holder)\

        if self.use_tokens:
            builder.with_token(self.test_data.master_card_multi_use_token('retail'))
        else:
            builder.with_card(self.test_data.master_card())

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(17.02).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    def test_024_charge_discover_manual_card_not_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        builder = self.service.charge(17.03)\
            .with_card_holder(card_holder)\

        if self.use_tokens:
            builder.with_token(self.test_data.discover_multi_use_token('retail'))
        else:
            builder.with_card(self.test_data.discover_card())

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_025_charge_amex_manual_card_not_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '750241234'

        builder = self.service.charge(17.04)\
            .with_card_holder(card_holder)\

        if self.use_tokens:
            builder.with_token(self.test_data.amex_multi_use_token('retail'))
        else:
            builder.with_card(self.test_data.amex_card())

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_026_charge_jcb_manual_card_not_present(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        response = self.service.charge(17.05)\
            .with_card_holder(card_holder)\
            .with_card(self.test_data.visa_card())\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Contactless """

    def test_027_charge_visa_contactless(self):
        response = self.service.charge(18.01).with_track_data(self.test_data.visa_swipe(method='proximity')).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_028_charge_mastercard_contactless(self):
        response = self.service.charge(18.01)\
            .with_track_data(self.test_data.master_card_swipe(method='proximity'))\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_029_charge_discover_contactless(self):
        response = self.service.charge(18.01)\
            .with_track_data(self.test_data.discover_swipe(method='proximity'))\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_030_charge_amex_contactless(self):
        response = self.service.charge(18.01).with_track_data(self.test_data.amex_swipe(method='proximity')).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ AUTHORIZATION """

    def test_031_authorize_visa_swipe(self):
        # 031a Authorize
        response = self.service.authorize(15.08).with_track_data(self.test_data.visa_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 031c Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    def test_032_authorize_visa_swipe_additional_auth(self):
        # 032a Authorize
        response = self.service.authorize(15.09).with_track_data(self.test_data.visa_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 032b Additional Auth (Restaurant Only)
        additional_auth_response = self.service.additional_auth(16.34)\
            .with_transaction_id(response.transaction_id)\
            .execute()
        self.assertIsNotNone(additional_auth_response)
        self.assertEqual('00', additional_auth_response.response_code)

        # 032c Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    def test_033_authorize_visa_swipe(self):
        # 033a Authorize
        response = self.service.authorize(15.10).with_track_data(self.test_data.master_card_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 033c Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    """ AUTHORIZE - Manually Entered, Card Present """

    def test_034_authorize_visa_manual_card_present(self):
        # 034a Authorize
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        response = self.service.authorize(16.08)\
            .with_card(self.test_data.visa_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 034c Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    def test_035_authorize_visa_manual_card_present_additional_auth(self):
        # 035a Authorize
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        response = self.service.authorize(16.09)\
            .with_card(self.test_data.visa_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 035b Additional Auth (Restaurant Only)

        # 035c Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    def test_036_authorize_mastercard_manual_card_present(self):
        # 036a Authorize
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        response = self.service.authorize(16.10)\
            .with_card(self.test_data.master_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 034c Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    """ AUTHORIZE - Manually Entered, Card Not Present """

    def test_037_authorize_visa_manual(self):
        # 034a Authorize
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '750241234'

        response = self.service.authorize(17.08)\
            .with_card(self.test_data.visa_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 034b Add To Batch
        capture_response = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture_response)
        self.assertEqual('00', capture_response.response_code)

    def test_038_authorize_mastercard_manual(self):
        # 038a Authorize
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        response = self.service.authorize(17.09)\
            .with_card(self.test_data.master_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # 038b Add To Batch (Do not complete)

    """ PARTIALLY APPROVED SALE (Required) """

    def test_039_charge_discover_swipe_partial_approval(self):
        response = self.service.charge(40.00)\
            .with_track_data(self.test_data.discover_swipe())\
            .with_allow_partial_auth(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertEqual(u'40.00', response.authorized_amount)

    def test_040_charge_visa_swipe_partial_approval(self):
        response = self.service.charge(130.00)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_allow_partial_auth(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertEqual(u'110.00', response.authorized_amount)

    def test_041_charge_mastercard_manual_partial_approval(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(145.00)\
            .with_card(self.test_data.master_card())\
            .with_allow_partial_auth(True)\
            .with_card_holder(card_holder)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertEqual(u'65.00', response.authorized_amount)

    def test_042_charge_discover_swipe_partial_approval(self):
        response = self.service.charge(155.00)\
            .with_track_data(self.test_data.discover_swipe())\
            .with_allow_partial_auth(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertEqual(u'100.00', response.authorized_amount)

        reversal_response = self.service.reverse(100.00).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    """ SALE with GRATUITY """

    """ Tip Edit (Tip at Settlement) """

    def test_043_charge_visa_swipe_edit_gratuity(self):
        response = self.service.charge(15.11).with_track_data(self.test_data.visa_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        edit_response = self.service.edit(response.transaction_id).with_amount(18.11).with_gratuity(3.00).execute()
        self.assertIsNotNone(edit_response)
        self.assertEqual('00', edit_response.response_code)

    def test_044_charge_mastercard_manual_edit_gratuity(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(15.12)\
            .with_card(self.test_data.master_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        edit_response = self.service.edit(response.transaction_id).with_amount(18.12).with_gratuity(3.00).execute()
        self.assertIsNotNone(edit_response)
        self.assertEqual('00', edit_response.response_code)

    """ Tip On Purchase """

    def test_045_charge_visa_manaual_gratuity(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(18.63)\
            .with_card(self.test_data.visa_card())\
            .with_card_holder(card_holder)\
            .with_card_present(True)\
            .with_gratuity(3.50)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_046_charge_mastercard_swipe_gratuity(self):
        response = self.service.charge(18.64)\
            .with_track_data(self.test_data.master_card_swipe())\
            .with_gratuity(3.50)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ LEVEL II CORPORATE PURCHASE CARD """

    def test_047_level_ii_visa_swipe_response_b(self):
        response = self.service.charge(112.34)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('B', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.not_used)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_048_level_ii_visa_swipe_response_r(self):
        response = self.service.charge(123.45)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('R', response.cpc_indicator)

        cpc_data = HpsCPCData('', HpsTaxType.tax_exempt)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_049_level_ii_visa_manual_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(134.56)\
            .with_card(self.test_data.visa_card())\
            .with_card_present(True)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('S', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.sales_tax, 1.0)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_050_level_ii_mastercard_swipe_response_s(self):
        response = self.service.charge(111.06)\
            .with_track_data(self.test_data.master_card_swipe())\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('S', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.not_used)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_051_level_ii_mastercard_manual_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(111.07)\
            .with_card(self.test_data.master_card())\
            .with_card_present(True)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('S', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.sales_tax, 1.00)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_052_level_ii_mastercard_manual_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(111.09)\
            .with_card(self.test_data.master_card())\
            .with_card_present(True)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('S', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.tax_exempt)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_053_level_ii_amex_swipe_no_response(self):
        response = self.service.charge(111.10)\
            .with_track_data(self.test_data.amex_swipe())\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('0', response.cpc_indicator)

        cpc_data = HpsCPCData('', HpsTaxType.sales_tax, 1.00)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_054_level_ii_amex_manual_no_response(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(111.11)\
            .with_card(self.test_data.amex_card())\
            .with_card_present(True)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('0', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.not_used)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_055_level_ii_amex_manual_no_response(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        response = self.service.charge(111.12)\
            .with_card(self.test_data.amex_card())\
            .with_card_present(True)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('0', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.tax_exempt)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    """ OFFLINE SALE / AUTHORIZATION """

    def test_056_offline_charge_visa_manual(self):
        response = self.service.offline_charge(15.11)\
            .with_card(self.test_data.visa_card(cvv=False))\
            .with_offline_auth_code('654321')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_056_offline_auth_visa_manual(self):
        response = self.service.offline_auth(15.11)\
            .with_card(self.test_data.visa_card(cvv=False))\
            .with_offline_auth_code('654321')\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ RETURN """

    def test_057_return_mastercard(self):
        response = self.service.refund(15.11)\
            .with_card(self.test_data.master_card(cvv=False))\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_058_return_jcb_transaction_id(self):
        pass  # See test 014

    """ ONLINE VOID / REVERSAL (Required) """
    def test_059_reversal_visa(self):
        pass  # See test 010

    def test_060_reversal_mastercard(self):
        pass  # See test 017

    def test_061_reversal_mastercard(self):
        pass  # See test 023

    def test_062_reversal_discover(self):
        pass  # See test 040

    def test_063_reversal_visa_partial(self):
        pass  # See test 015

    def test_064_reversal_discover_partial(self):
        pass  # See test 021

    """ PIN DEBIT CARD FUNCTIONS """

    debit_service = HpsFluentDebitService(config)

    """ SALE - PIN Based Debit """

    def test_065_debit_sale_visa_swipe(self):
        response = self.debit_service.sale(14.01)\
            .with_track_data(self.test_data.visa_debit_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_066_debit_sale_mastercard_swipe(self):
        response = self.debit_service.sale(14.02)\
            .with_track_data(self.test_data.mastercard_debit_swipe())\
            .with_pin_block(self.test_data.mastercard_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.debit_service.reverse(14.02).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    def test_067_debit_sale_visa_swipe_cashback(self):
        response = self.debit_service.sale(14.03)\
            .with_track_data(self.test_data.visa_debit_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_cash_back(5.00)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ PARTIALLY APPROVED PURCHASE """

    def test_068_debit_sale_mastercard_partial_approval(self):
        response = self.debit_service.sale(33.00)\
            .with_track_data(self.test_data.mastercard_debit_swipe())\
            .with_pin_block(self.test_data.mastercard_debit_pin_block())\
            .with_allow_partial_auth(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertEqual(u'22.00', response.authorized_amount)

    def test_069_debit_sale_visa_partial_approval(self):
        response = self.debit_service.sale(44.00)\
            .with_track_data(self.test_data.mastercard_debit_swipe())\
            .with_pin_block(self.test_data.mastercard_debit_pin_block())\
            .with_allow_partial_auth(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertEqual(u'33.00', response.authorized_amount)

        reversal_response = self.debit_service.reverse(33.00).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    """ RETURN """

    def test_070_debit_return_visa_swipe(self):
        response = self.debit_service.refund(14.07)\
            .with_track_data(self.test_data.visa_debit_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ REVERSAL """

    def test_071_debit_reversal_mastercard(self):
        pass  # See test 066

    def test_072_debit_reversal_visa(self):
        pass  # See test 69

    """ ONE Card - GSB CARD FUNCTIONS """

    """ Balance Inquiry """

    def test_073_balance_inquiry_gsb_swipe(self):
        response = self.service.prepaid_balance_inquiry().with_track_data(self.test_data.gsb_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_074_balance_inquiry_gsb_manual(self):
        response = self.service.prepaid_balance_inquiry()\
            .with_card(self.test_data.gsb_card_ecommerce())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Add Value (LOAD) """

    def test_075_add_value_gsb_swipe(self):
        response = self.service.prepaid_add_value(5.00).with_track_data(self.test_data.gsb_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_076_add_value_gsb_manual(self):
        response = self.service.prepaid_add_value(5.00)\
            .with_card(self.test_data.gsb_card_ecommerce())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Sale """

    def test_077_charge_gsb_swipe_reversal(self):
        response = self.service.charge(2.05).with_track_data(self.test_data.gsb_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(2.05).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    def test_078_charge_gsb_swipe(self):
        response = self.service.charge(2.10).with_track_data(self.test_data.gsb_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_079_charge_gsb_swipe_partial_reversal(self):
        response = self.service.charge(2.15).with_track_data(self.test_data.gsb_swipe()).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        reversal_response = self.service.reverse(2.15)\
            .with_auth_amount(1.15)\
            .with_transaction_id(response.transaction_id)\
            .execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('00', reversal_response.response_code)

    """ EBT FUNCTIONS """

    ebt_service = HpsFluentEbtService(config)

    """ Food Stamp Purchase """

    def test_080_ebtfs_purchase_visa_swipe(self):
        response = self.ebt_service.purchase(101.01)\
            .with_track_data(self.test_data.visa_debit_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_081_ebtfs_purchase_visa_manual(self):
        response = self.ebt_service.purchase(102.01)\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Food Stamp Electronic Voucher (Manual Entry Only) """

    def test_082_ebt_voucher_purchase_visa(self):
        response = self.ebt_service.voucher_purchase(103.01)\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_serial_number(123456789012345)\
            .with_approval_code(123456)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Food Stamp Return """

    def test_083_ebtfs_return_visa_swipe(self):
        response = self.ebt_service.refund(104.01)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_084_ebtfs_return_visa_manual(self):
        response = self.ebt_service.refund(105.01)\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Food Stamp Balance Inquiry """

    def test_085_ebt_balance_inquiry_visa_swipe(self):
        response = self.ebt_service.balance_inquiry()\
            .with_track_data(self.test_data.visa_debit_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_inquiry_type('FOODSTAMP')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_086_ebt_balance_inquiry_visa_manual(self):
        response = self.ebt_service.balance_inquiry()\
            .with_card(self.test_data.visa_card())\
            .with_pin_block('32539F50C245A6A93D123412324000AA')\
            .with_card_present(True)\
            .with_reader_present(True)\
            .with_inquiry_type('FOODSTAMP')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ EBT CASH BENEFITS """

    """ Cash Back Purchase """

    def test_087_ebt_cash_back_purchase_visa_swipe(self):
        response = self.ebt_service.cash_back_purchase(106.01)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_cash_back(5.00)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_088_ebt_cash_back_purchase_visa_manual(self):
        response = self.ebt_service.cash_back_purchase(107.01)\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_card_present(True)\
            .with_cash_back(5.00)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ No Cash Back Purchase """

    def test_089_ebt_cash_back_purchase_visa_swipe_no_cash_back(self):
        response = self.ebt_service.cash_back_purchase(108.01)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_090_ebt_cash_back_purchase_visa_manual_no_cash_back(self):
        response = self.ebt_service.cash_back_purchase(109.01)\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Cash Back Balance Inquiry """

    def test_091_ebt_balance_inquiry_visa_swipe_cash(self):
        response = self.ebt_service.balance_inquiry()\
            .with_track_data(self.test_data.visa_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_inquiry_type('CASH')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_092_ebt_balance_inquiry_visa_manual_cash(self):
        response = self.ebt_service.balance_inquiry()\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_card_present(True)\
            .with_reader_present(True)\
            .with_inquiry_type('CASH')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Cash Benefits Withdrawal """

    def test_093_ebt_benefit_withdrawal_visa_swipe(self):
        response = self.ebt_service.benefit_withdrawal(110.01)\
            .with_track_data(self.test_data.visa_swipe())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_094_ebt_benefit_withdrawal_visa_manual(self):
        response = self.ebt_service.benefit_withdrawal(111.01)\
            .with_card(self.test_data.visa_card())\
            .with_pin_block(self.test_data.visa_debit_pin_block())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ HMS GIFT - REWARDS """

    """ GIFT """

    gift_service = HpsFluentGiftCardService(config)

    """ ACTIVATE """

    def test_095_activate_gift_1_swipe(self):
        response = self.gift_service.activate(6.00)\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_096_activate_gift_2_manual(self):
        response = self.gift_service.activate(7.00)\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ LOAD / ADD VALUE """

    def test_097_add_value_gift_1_swipe(self):
        response = self.gift_service.add_value(8.00)\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_098_add_value_gift_2_manual(self):
        response = self.gift_service.add_value(9.00)\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ BALANCE INQUIRY """

    def test_099_balance_inquiry_gift_1_swipe(self):
        response = self.gift_service.balance()\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'10.00', response.balance_amount)

    def test_100_balance_inquiry_gift_2_manual(self):
        response = self.gift_service.balance()\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'10.00', response.balance_amount)

    """ REPLACE / TRANSFER """

    def test_101_replace_gift_1_swipe(self):
        response = self.gift_service.replace()\
            .with_old_card(self.test_data.gift_swipe_1())\
            .with_new_card(self.test_data.gift_card_2())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_102_replace_gift_2_manual(self):
        response = self.gift_service.replace()\
            .with_old_card(self.test_data.gift_card_2())\
            .with_new_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ SALE / REDEEM """

    def test_103_sale_gift_1_swipe(self):
        response = self.gift_service.sale(1.00)\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_104_sale_gift_2_manual(self):
        response = self.gift_service.sale(2.00)\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_105_sale_gift_1_void_swipe(self):
        response = self.gift_service.sale(3.00)\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

        # VOID TRANSACTION
        void_response = self.gift_service.void(response.transaction_id).execute()
        self.assertIsNotNone(void_response)
        self.assertEqual('0', void_response.response_code)

    def test_106_sale_gift_2_reversal_manual(self):
        response = self.gift_service.sale(4.00)\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

        # REVERSE TRANSACTION
        reversal_response = self.gift_service.reverse(4.00).with_transaction_id(response.transaction_id).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('0', reversal_response.response_code)

    """ VOID """

    def test_107_void_gift(self):
        pass  # SEE TEST 104

    """ REVERSAL """

    def test_108_reversal_gift(self):
        pass  # SEE TEST 105

    """ DEACTIVATE """

    def test_109_deactivate_gift_1(self):
        response = self.gift_service.deactivate()\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ RECEIPTS MESSAGING """

    def test_110_receipts_messaging(self):
        pass  # print and scan receipt for test 51

    """ REWARD """

    """ BALANCE INQUIRY """

    def test_111_balance_inquiry_rewards_1(self):
        response = self.gift_service.balance()\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'0', response.points_balance_amount)

    def test_112_balance_inquiry_rewards_2(self):
        response = self.gift_service.balance()\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'0', response.points_balance_amount)

    """ ALIAS """

    def test_113_create_alias_gift_1(self):
        response = self.gift_service.alias()\
            .with_alias('9725550100')\
            .with_action('CREATE')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_114_create_alias_gift_2(self):
        response = self.gift_service.alias()\
            .with_alias('9725550100')\
            .with_action('CREATE')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_115_add_alias_gift_1(self):
        response = self.gift_service.alias()\
            .with_card(self.test_data.gift_swipe_1())\
            .with_alias('2145550199')\
            .with_action('ADD')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_116_add_alias_gift_2(self):
        response = self.gift_service.alias()\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .with_alias('2145550199')\
            .with_action('ADD')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_117_delete_alias_gift_1(self):
        response = self.gift_service.alias()\
            .with_card(self.test_data.gift_swipe_1())\
            .with_alias('2145550199')\
            .with_action('DELETE')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ SALE / REDEEM """

    def test_118_redeem_points_gift_1(self):
        response = self.gift_service.sale(100)\
            .with_currency('points')\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_119_redeem_points_gift_2(self):
        response = self.gift_service.sale(200)\
            .with_currency('points')\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_120_redeem_points_gift_2(self):
        gift = HpsGiftCard()
        gift.alias = '9725550100'

        response = self.gift_service.sale(300)\
            .with_currency('points')\
            .with_card(gift)\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ REWARDS """

    def test_121_rewards_gift_1(self):
        response = self.gift_service.reward(10)\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_122_rewards_gift_2(self):
        response = self.gift_service.reward(11)\
            .with_card(self.test_data.gift_card_2())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ REPLACE / TRANSFER """

    def test_123_replace_gift_1_swipe(self):
        response = self.gift_service.replace()\
            .with_old_card(self.test_data.gift_swipe_1())\
            .with_new_card(self.test_data.gift_card_2())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_124_replace_gift_2_manual(self):
        response = self.gift_service.replace()\
            .with_old_card(self.test_data.gift_card_2())\
            .with_new_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ DEACTIVATE """

    def test_125_deactivate_gift_1(self):
        response = self.gift_service.deactivate()\
            .with_card(self.test_data.gift_swipe_1())\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_126_deactivate_gift_2(self):
        response = self.gift_service.deactivate()\
            .with_card(self.test_data.gift_card_2())\
            .with_card_present(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ RECEIPTS MESSAGING """

    def test_127_receipts_messaging(self):
        pass  # print and scan receipt for test 51

    """ CLOSE BATCH """

    def test_999_close_batch(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")
            print 'batch id: {0}'.format(response.id)
            print 'sequence number: {0}'.format(response.sequence_number)
        except HpsException, e:
            self.fail(e.message)