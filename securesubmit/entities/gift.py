"""
    gift.py

    This module defines the gift entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from securesubmit.entities import HpsTransaction


class HpsEncryptionData(object):
    version = None

    """This is required in certain encryption versions when
       supplying track data and indicates which track has been supplied."""
    encrypted_track_number = None

    """This is required in certain encryption versions;
       the <u>K</u>ey <u>T</u>ransmission <u>B</u>lock
       (KTB) used at the point of sale."""
    ktb = None

    """This is required in certain encryption versions;
       the <u>K</u>ey <u>S</u>erial <u>N</u>umber (KSN)
       used at the point of sale."""
    ksn = None


class HpsGiftCard(object):
    number = None
    exp_month = None
    exp_year = None
    is_track_data = None
    encryption_data = None

    def __init__(self, number=None):
        is_track_data = False
        self.number = number


class HpsGiftCardActivate(HpsTransaction):
    authorization_code = None
    balance_amount = None
    points_balance = None

    """The rewards (dollars or points) added to the account as a
       result of a transaction."""
    rewards = None

    """Notes contain reward messages to be displayed on a receipt,
       mobile app, or web page to inform an account holder about
       special rewards or promotions available on the account."""
    notes = None

    @classmethod
    def from_dict(cls, rsp):
        activation_rsp = rsp['Transaction'].itervalues().next()

        activation = cls()
        activation.transaction_id = rsp['Header']['GatewayTxnId']
        activation.authorization_code = None
        if 'AuthCode' in activation_rsp:
            activation.authorization_code = activation_rsp['AuthCode']
        activation.balance_amount = None
        if 'BalanceAmt' in activation_rsp:
            activation.balance_amount = activation_rsp['BalanceAmt']
        activation.points_balance_amount = None
        if 'PointsBalanceAmt' in activation_rsp:
            activation.points_balance_amount = \
                activation_rsp['PointsBalanceAmt']
        activation.rewards = None
        if 'Rewards' in activation_rsp:
            activation.rewards = activation_rsp['Rewards']
        activation.notes = None
        if 'Notes' in activation_rsp:
            activation.notes = activation_rsp['Notes']
        activation.response_code = None
        if 'RspCode' in activation_rsp:
            activation.response_code = str(activation_rsp['RspCode'])
        activation.response_text = None
        if 'RspText' in activation_rsp:
            activation.response_text = activation_rsp['RspText']

        return activation


class HpsGiftCardAddValue(HpsGiftCardActivate):
    pass


class HpsGiftCardAlias(HpsTransaction):
    gift_card = None

    @classmethod
    def from_dict(cls, rsp):
        item = rsp['Transaction'].itervalues().next()

        alias = cls()
        alias.transaction_id = rsp['Header']['GatewayTxnId']
        alias.gift_card = HpsGiftCard(item['CardData'])
        alias.rsp_code = None
        if 'RspCode' in item:
            alias.rsp_code = str(item['RspCode'])
        alias.rsp_text = None
        if 'RspText' in item:
            alias.rsp_text = item['RspText']

        return alias


class HpsGiftCardBalance(HpsGiftCardActivate):
    pass


class HpsGiftCardDeactivate(HpsGiftCardActivate):
    pass


class HpsGiftCardReplace(HpsGiftCardActivate):
    pass


class HpsGiftCardReversal(HpsGiftCardActivate):
    pass


class HpsGiftCardReward(HpsGiftCardActivate):
    pass


class HpsGiftCardSale(HpsGiftCardActivate):
    split_tender_card_amount = None
    split_tender_balance_due = None

    @classmethod
    def from_dict(cls, rsp):
        item = rsp['Transaction'].itervalues().next()

        sale = super(HpsGiftCardSale, cls).from_dict(rsp)
        sale.split_tender_card_amount = None
        if 'SplitTenderCardAmt' in item:
            sale.split_tender_card_amount = item['SplitTenderCardAmt']
        sale.split_tender_balance_due = None
        if 'SplitTenderBalanceDueAmt' in item:
            sale.split_tender_balance_due = item['SplitTenderBalanceDueAmt']

        return sale


class HpsGiftCardVoid(HpsGiftCardActivate):
    pass
