import unittest

from securesubmit.entities import HpsAddress, HpsDirectMarketData
from securesubmit.entities.credit import HpsCardHolder, HpsCPCData, HpsTrackData, HpsCreditCard
from securesubmit.entities.gift import HpsGiftCard
from securesubmit.infrastructure import HpsException
from securesubmit.infrastructure.enums import HpsTaxType
from securesubmit.services import HpsServicesConfig
from securesubmit.services.fluent.gateway import HpsFluentCreditService, HpsFluentGiftCardService
from securesubmit.services.gateway import HpsBatchService


class MotoTests(unittest.TestCase):
    config = HpsServicesConfig()
    config.secret_api_key = 'skapi_cert_MRCQAQBC_VQACBE0rFaZlbDDPieMGP06JDAtjyS7NQ'
    config.developer_id = '012345'
    config.version_number = '0001'

    batch_service = HpsBatchService(config)
    service = HpsFluentCreditService().with_config(config)

    use_tokens = True
    use_prepaid = True

    visa_token = None
    mastercard_token = None
    discover_token = None
    amex_token = None

    test_10_transaction_id = None
    test_20_transaction_id = None
    test_39_transaction_id = None
    test_52_transaction_id = None
    test_53_transaction_id = None

    """ CARD VERIFY """

    def test_000_close_batch(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")
            print 'batch id: {0}'.format(response.id)
            print 'sequence number: {0}'.format(response.sequence_number)
        except HpsException, e:
            if e.message != 'Transaction was rejected because it requires a batch to be open.':
                self.fail(e.message)

    """ Account Verification """

    def test_001_verify_visa(self):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025

        response = self.service.verify()\
            .with_card(card)\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('85', response.response_code)

    def test_002_verify_master_card(self):
        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025

        response = self.service.verify()\
            .with_card(card)\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('85', response.response_code)

    def test_003_verify_discover(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.verify()\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('85', response.response_code)

    """ Address Verification """

    def test_004_verify_amex(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025

        response = self.service.verify()\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(self.use_tokens)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ Balance Inquiry (for Prepaid Card) """

    def test_005_balance_inquiry_visa(self):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025

        response = self.service.prepaid_balance_inquiry()\
            .with_card(card)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ CREDIT SALE (For Multi-Use Token Only) """

    def test_006_charge_visa_token(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025

        response = self.service.charge(13.01)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertIsNotNone(response.token_data)
        self.assertIsNotNone(response.token_data.token_value)
        self.__class__.visa_token = response.token_data.token_value

    def test_007_charge_master_card_token(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(13.02)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertIsNotNone(response.token_data)
        self.assertIsNotNone(response.token_data.token_value)
        self.__class__.mastercard_token = response.token_data.token_value

    def test_008_charge_discover_token(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '750241234'

        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(13.03)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertIsNotNone(response.token_data)
        self.assertIsNotNone(response.token_data.token_value)
        self.__class__.discover_token = response.token_data.token_value

    def test_009_charge_amex_token(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 1234

        response = self.service.charge(13.04)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertIsNotNone(response.token_data)
        self.assertIsNotNone(response.token_data.token_value)
        self.__class__.amex_token = response.token_data.token_value

    """ CREDIT SALE """

    def test_010_charge_visa(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        builder = self.service.charge(17.01)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)

        if self.use_tokens:
            builder.with_token(self.__class__.visa_token)
        else:
            builder.with_card(card)

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.__class__.test_10_transaction_id = response.transaction_id

    def test_011_charge_master_card(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        builder = self.service.charge(17.02)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)

        if self.use_tokens:
            builder.with_token(self.__class__.mastercard_token)
        else:
            builder.with_card(card)

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_012_charge_discover(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '750241234'

        direct_market_data = HpsDirectMarketData('123456')

        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        builder = self.service.charge(17.03)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)

        if self.use_tokens:
            builder.with_token(self.__class__.discover_token)
        else:
            builder.with_card(card)

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_013_charge_amex(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 1234

        direct_market_data = HpsDirectMarketData('123456')

        builder = self.service.charge(17.04)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)

        if self.use_tokens:
            builder.with_token(self.__class__.amex_token)
        else:
            builder.with_card(card)

        response = builder.execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_014_charge_jcb(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '750241234'

        card = HpsCreditCard()
        card.number = '3566007770007321'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.charge(17.05)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ AUTHORIZATION """

    def test_015_authorization_visa(self):
        # Test 015a Authorization
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.authorize(17.06)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # test 015b Capture/AddToBatch
        capture = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture)
        self.assertEqual('00', capture.response_code)

    def test_016_authorization_master_card(self):
        # Test 016a Authorization
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '750241234'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.authorize(17.07)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # test 016b Capture/AddToBatch
        capture = self.service.capture(response.transaction_id).execute()
        self.assertIsNotNone(capture)
        self.assertEqual('00', capture.response_code)

    def test_017_authorization_discover(self):
        # Test 017a Authorization
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        direct_market_data = HpsDirectMarketData('123456')

        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.authorize(17.08)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

        # test 017b Capture/AddToBatch
        # do not capture

    """ PARTIALLY - APPROVED SALE """

    def test_018_partial_approval_visa(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.charge(130)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .with_allow_partial_auth(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertIsNotNone(response.authorized_amount)
        self.assertEqual(u'110.00', response.authorized_amount)

    def test_019_partial_approval_discover(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        direct_market_data = HpsDirectMarketData('123456')

        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(145)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .with_allow_partial_auth(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertIsNotNone(response.authorized_amount)
        self.assertEqual(u'65.00', response.authorized_amount)

    def test_020_partial_approval_master_card(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        direct_market_data = HpsDirectMarketData('123456')

        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(155)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_direct_market_data(direct_market_data)\
            .with_allow_partial_auth(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('10', response.response_code)
        self.assertIsNotNone(response.authorized_amount)
        self.assertEqual(u'100.00', response.authorized_amount)
        self.__class__.test_20_transaction_id = response.transaction_id

    """ LEVEL II CORPORATE PURCHASE CARD """

    def test_021_level_ii_response_b(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860 Dallas Pkwy'
        card_holder.address.zip = '750241234'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(112.34)\
            .with_card(card)\
            .with_card_holder(card_holder)\
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

    def test_022_level_ii_response_b(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '750241234'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(112.34)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_allow_duplicates(True)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('B', response.cpc_indicator)

        cpc_data = HpsCPCData('', HpsTaxType.sales_tax, 1.0)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_023_level_ii_response_r(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(123.45)\
            .with_card(card)\
            .with_card_holder(card_holder)\
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

    def test_024_level_ii_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(134.56)\
            .with_card(card)\
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

    def test_025_level_ii_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(111.06)\
            .with_card(card)\
            .with_card_holder(card_holder)\
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

    def test_026_level_ii_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(111.07)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('S', response.cpc_indicator)

        cpc_data = HpsCPCData('', HpsTaxType.sales_tax, 1.00)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_027_level_ii_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(111.08)\
            .with_card(card)\
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

    def test_028_level_ii_response_s(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(111.09)\
            .with_card(card)\
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

    def test_029_level_ii_no_response(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 1234

        response = self.service.charge(111.10)\
            .with_card(card)\
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

    def test_030_level_ii_no_response(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '750241234'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 1234

        response = self.service.charge(111.11)\
            .with_card(card)\
            .with_card_holder(card_holder)\
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

    def test_031_level_ii_no_response(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 1234

        response = self.service.charge(111.12)\
            .with_card(card)\
            .with_card_holder(card_holder)\
            .with_cpc_req(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        self.assertEqual('0', response.cpc_indicator)

        cpc_data = HpsCPCData('9876543210', HpsTaxType.sales_tax, 1.00)
        cpc_response = self.service.cpc_edit(response.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_response)
        self.assertEqual('00', cpc_response.response_code)

    def test_032_level_ii_no_response(self):
        card_holder = HpsCardHolder()
        card_holder.address = HpsAddress()
        card_holder.address.address = '6860'
        card_holder.address.zip = '75024'

        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 1234

        response = self.service.charge(111.13)\
            .with_card(card)\
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

    """ PRIOR / VOICE AUTHORIZATION """

    def test_033_offline_sale(self):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.offline_charge(17.10)\
            .with_card(card)\
            .with_offline_auth_code('654321')\
            .with_direct_market_data(direct_market_data)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_033_offline_authorization(self):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.offline_auth(17.10)\
            .with_card(card)\
            .with_offline_auth_code('654321')\
            .with_direct_market_data(direct_market_data)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ RETURN """

    def test_034_offline_credit_return(self):
        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        direct_market_data = HpsDirectMarketData('123456')

        response = self.service.refund(15.15)\
            .with_card(card)\
            .with_direct_market_data(direct_market_data)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    """ ONLINE VOID / REVERSAL """

    def test_035_void_test_10(self):
        void_response = self.service.void(self.__class__.test_10_transaction_id).execute()
        self.assertIsNotNone(void_response)
        self.assertEqual('00', void_response.response_code)

    def test_036_void_test_20(self):
        void_response = self.service.void(self.__class__.test_20_transaction_id).execute()
        self.assertIsNotNone(void_response)
        self.assertEqual('00', void_response.response_code)

    """ ADVANCED FRAUD SCREENING """

    def test_037_fraud_prevention_sale(self):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.charge(15000).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)
        # self.assertEqual('FR', response.issuser_response_code)

    def test_038_fraud_prevention_return(self):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2025
        card.cvv = 123

        response = self.service.refund(15000).with_card(card).execute()
        self.assertIsNotNone(response)
        if response.response_code != '00':
            self.assertEqual('41', response.response_code)
            # self.assertEqual('FR', response.issuser_response_code)

    """ HMS GIFT - REWARDS """

    """ GIFT """

    gift_service = HpsFluentGiftCardService(config)

    # def gift_card_1(self):
    #     card = HpsGiftCard()
    #     card.card_number = '5022440000000000098'
    #
    #     return card
    #
    # def gift_card_2(self):
    #     card = HpsGiftCard()
    #     card.card_number = '5022440000000000007'
    #
    #     return card

    """ ACTIVATE """

    def test_044_activate_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.activate(6.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_045_activate_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.activate(7.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ LOAD / ADD VALUE """

    def test_046_add_value_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.add_value(8.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_047_add_value_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.add_value(9.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ BALANCE INQUIRY """

    def test_048_balance_inquiry_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.balance().with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'10.00', response.balance_amount)

    def test_049_balance_inquiry_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.balance().with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'10.00', response.balance_amount)

    """ REPLACE / TRANSFER """

    def test_050_replace_gift_1(self):
        old_card = HpsGiftCard()
        old_card.card_number = '5022440000000000098'

        new_card = HpsGiftCard()
        new_card.card_number = '5022440000000000007'

        response = self.gift_service.replace()\
            .with_old_card(old_card)\
            .with_new_card(new_card)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_051_replace_gift_2(self):
        new_card = HpsGiftCard()
        new_card.card_number = '5022440000000000098'

        old_card = HpsGiftCard()
        old_card.card_number = '5022440000000000007'

        response = self.gift_service.replace()\
            .with_old_card(old_card)\
            .with_new_card(new_card)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ SALE / REDEEM """

    def test_052_sale_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.sale(1.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_053_sale_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.sale(2.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_054_sale_gift_1_void(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.sale(3.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.__class__.test_52_transaction_id = response.transaction_id

    def test_055_sale_gift_2_reversal(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.sale(4.00).with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.__class__.test_53_transaction_id = response.transaction_id

    """ VOID """

    def test_056_void_gift(self):
        void_response = self.gift_service.void(self.__class__.test_52_transaction_id).execute()
        self.assertIsNotNone(void_response)
        self.assertEqual('0', void_response.response_code)

    """ REVERSAL """

    def test_057_reversal_gift(self):
        reversal_response = self.gift_service.reverse(4.00)\
            .with_transaction_id(self.__class__.test_53_transaction_id)\
            .execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('0', reversal_response.response_code)

    def test_058_reversal_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        reversal_response = self.gift_service.reverse(2.00).with_card(card).execute()
        self.assertIsNotNone(reversal_response)
        self.assertEqual('0', reversal_response.response_code)

    """ DEACTIVATE """

    def test_059_deactivate_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.deactivate().with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ RECEIPTS MESSAGING """

    def test_060_receipts_messaging(self):
        pass  # print and scan receipt for test 51

    """ REWARD """

    """ BALANCE INQUIRY """

    def test_061_balance_inquiry_rewards_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.balance().with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'0', response.points_balance_amount)

    def test_062_balance_inquiry_rewards_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.balance().with_card(card).execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual(u'0', response.points_balance_amount)

    """ ALIAS """

    def test_063_create_alias_gift_1(self):
        response = self.gift_service.alias()\
            .with_alias('9725550100')\
            .with_action('CREATE')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_064_create_alias_gift_2(self):
        response = self.gift_service.alias()\
            .with_alias('9725550100')\
            .with_action('CREATE')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_065_add_alias_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.alias()\
            .with_card(card)\
            .with_alias('2145550199')\
            .with_action('ADD')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_066_add_alias_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.alias()\
            .with_card(card)\
            .with_alias('2145550199')\
            .with_action('ADD')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_067_delete_alias_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.alias()\
            .with_card(card)\
            .with_alias('2145550199')\
            .with_action('DELETE')\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ SALE / REDEEM """

    def test_068_redeem_points_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.sale(100)\
            .with_currency('points')\
            .with_card(card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_069_redeem_points_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.sale(200)\
            .with_currency('points')\
            .with_card(card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_070_redeem_points_gift_2(self):
        gift = HpsGiftCard()
        gift.alias = '9725550100'

        response = self.gift_service.sale(300)\
            .with_currency('points')\
            .with_card(gift)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ REWARDS """

    def test_071_rewards_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.reward(10)\
            .with_card(card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_072_rewards_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.reward(11)\
            .with_card(card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ REPLACE / TRANSFER """

    def test_073_replace_gift_1(self):
        old_card = HpsGiftCard()
        old_card.card_number = '5022440000000000098'

        new_card = HpsGiftCard()
        new_card.card_number = '5022440000000000007'

        response = self.gift_service.replace()\
            .with_old_card(old_card)\
            .with_new_card(new_card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_074_replace_gift_2(self):
        new_card = HpsGiftCard()
        new_card.card_number = '5022440000000000098'

        old_card = HpsGiftCard()
        old_card.card_number = '5022440000000000007'

        response = self.gift_service.replace()\
            .with_old_card(old_card)\
            .with_new_card(new_card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ DEACTIVATE """

    def test_075_deactivate_gift_1(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        response = self.gift_service.deactivate()\
            .with_card(card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_076_deactivate_gift_2(self):
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        response = self.gift_service.deactivate()\
            .with_card(card)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ RECEIPTS MESSAGING """

    def test_077_receipts_messaging(self):
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
