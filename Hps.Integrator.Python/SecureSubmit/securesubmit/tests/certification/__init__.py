from securesubmit.entities.credit import HpsCreditCard, HpsTrackData, HpsEncryptionData
from securesubmit.entities.gift import HpsGiftCard
from securesubmit.services.token import HpsTokenService


class TestData(object):
    public_api_key = None
    token_service = None
    tokens = dict()

    def __init__(self, public_api_key):
        self.public_api_key = public_api_key
        self.token_service = HpsTokenService(self.public_api_key)

    def tokenize_card(self, card):
        if card.number in self.tokens:
            return self.tokens[card.number]

        token = self.token_service.get_token(card)
        self.tokens[card.number] = token

        return token

    """ CREDIT CARDS """

    def visa_card(self, cvv=True, token=False):
        card = HpsCreditCard()
        card.number = '4012002000060016'
        card.exp_month = 12
        card.exp_year = 2015
        if cvv:
            card.cvv = 123

        if token:
            return self.tokenize_card(card).token_value
        return card

    def master_card(self, cvv=True, token=False):
        card = HpsCreditCard()
        card.number = '5473500000000014'
        card.exp_month = 12
        card.exp_year = 2015
        if cvv:
            card.cvv = 123

        if token:
            return self.tokenize_card(card).token_value
        return card

    def discover_card(self, cvv=True, token=False):
        card = HpsCreditCard()
        card.number = '6011000990156527'
        card.exp_month = 12
        card.exp_year = 2015
        if cvv:
            card.cvv = 123

        if token:
            return self.tokenize_card(card).token_value
        return card

    def amex_card(self, cvv=True, token=False):
        card = HpsCreditCard()
        card.number = '372700699251018'
        card.exp_month = 12
        card.exp_year = 2015
        if cvv:
            card.cvv = 1234

        if token:
            return self.tokenize_card(card).token_value
        return card

    def jcb_card(self, cvv=True, token=False):
        card = HpsCreditCard()
        card.number = '3566007770007321'
        card.exp_month = 12
        card.exp_year = 2015
        if cvv:
            card.cvv = 123

        if token:
            return self.tokenize_card(card).token_value
        return card

    """ CARD MULTI_USE TOKENS """

    # @staticmethod
    # def visa_multi_use_token(industry='ecommerce'):
    #     if industry == 'ecommerce':
    #         return u'Wf4LD1084WQUbf1S6Kcd0016'
    #     elif industry == 'retail':
    #         return u'Wf4LD1084WQUbf1S6Kcd0016'
    #
    # @staticmethod
    # def master_card_multi_use_token(industry='ecommerce'):
    #     if industry == 'ecommerce':
    #         return u'e51Af108vAsB6Tx0PfmG0014'
    #     elif industry == 'retail':
    #         return u'e51Af108vAsB6Tx0PfmG0014'
    #
    # @staticmethod
    # def discover_multi_use_token(industry='ecommerce'):
    #     if industry == 'ecommerce':
    #         return u'ubeZ3f08W1aaEV643ZJa6527'
    #     elif industry == 'retail':
    #         return u'ubeZ3f08W1aaEV643ZJa6527'
    #
    # @staticmethod
    # def amex_multi_use_token(industry='ecommerce'):
    #     if industry == 'ecommerce':
    #         return u'94oIbE08e30G0fVcH12d1018'
    #     elif industry == 'retail':
    #         return u'94oIbE08e30G0fVcH12d1018'

    @staticmethod
    def gsb_card_ecommerce():
        card = HpsCreditCard()
        card.number = '6277220572999800'
        card.exp_month = 12
        card.exp_year = 2049

        return card

    """ CARD SWIPE DATA """

    def visa_swipe(self, token=False, method='swipe'):
        card = HpsTrackData()
        card.value = '%B4012002000060016^VI TEST CREDIT^251210118039000000000396?;4012002000060016=25121011803939600000?'
        card.method = method

        if token:
            return self.tokenize_card(card)
        return card

    def master_card_swipe(self, token=False, method='swipe'):
        card = HpsTrackData()
        card.value = '%B5473500000000014^MC TEST CARD^251210199998888777766665555444433332?;5473500000000014=25121019999888877776?'
        card.method = method

        if token:
            return self.tokenize_card(card)
        return card

    def amex_swipe(self, token=False, method='swipe'):
        card = HpsTrackData()
        card.value = '%B3727 006992 51018^AMEX TEST CARD^2512990502700?;372700699251018=2512990502700?'
        card.method = method

        if token:
            return self.tokenize_card(card)
        return card

    def discover_swipe(self, token=False, method='swipe'):
        card = HpsTrackData()
        card.value = '%B6011000990156527^DIS TEST CARD^25121011000062111401?;6011000990156527=25121011000062111401?'
        card.method = method

        if token:
            return self.tokenize_card(card)
        return card

    def jcb_swipe(self, token=False, method='swipe'):
        card = HpsTrackData()
        card.value = '%B3566007770007321^JCB TEST CARD^2512101100000000000000000064300000?;3566007770007321=25121011000000076435?'
        card.method = method

        if token:
            return self.tokenize_card(card)
        return card

    def gsb_swipe(self, token=False):
        card = HpsTrackData()
        card.value = '%B6277220020010671^   /                         ^49121010228710000209000000?;6277220020010671=49121010228710000209?'
        card.method = 'swipe'

        if token:
            return self.tokenize_card(card)
        return card

    @staticmethod
    def visa_debit_swipe():
        card = HpsTrackData()
        card.value = '&lt;E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|LO04K0WFOmdkDz0um+GwUkILL8ZZOP6Zc4rCpZ9+kg2T3JBT4AEOilWTI|+++++++Dbbn04ekG|11;4012001000000016=25120000000000000000?|1u2F/aEhbdoPixyAPGyIDv3gBfF|+++++++Dbbn04ekG|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|&gt;'
        card.method = 'swipe'
        card.encryption_data = HpsEncryptionData()
        card.encryption_data.version = '01'

        return card

    @staticmethod
    def visa_debit_pin_block():
        return '32539F50C245A6A93D123412324000AA'

    @staticmethod
    def mastercard_debit_swipe():
        card = HpsTrackData()
        card.value = '&lt;E1052711%B5473501000000014^MC TEST CARD^251200000000000000000000000000000000?|GVEY/MKaKXuqqjKRRueIdCHPPoj1gMccgNOtHC41ymz7bIvyJJVdD3LW8BbwvwoenI+|+++++++C4cI2zjMp|11;5473501000000014=25120000000000000000?|8XqYkQGMdGeiIsgM0pzdCbEGUDP|+++++++C4cI2zjMp|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|&gt;'
        card.method = 'swipe'
        card.encryption_data = HpsEncryptionData()
        card.encryption_data.version = '01'

        return card

    @staticmethod
    def mastercard_debit_pin_block():
        return 'F505AD81659AA42A3D123412324000AB'

    """ GIFT CARDS """

    @staticmethod
    def gift_card_1():
        card = HpsGiftCard()
        card.card_number = '5022440000000000098'

        return card

    @staticmethod
    def gift_card_2():
        card = HpsGiftCard()
        card.card_number = '5022440000000000007'

        return card

    @staticmethod
    def gift_swipe_1():
        card = HpsGiftCard()
        card.track_data = '%B5022440000000000098^^391200081613?;5022440000000000098=391200081613?'

        return card