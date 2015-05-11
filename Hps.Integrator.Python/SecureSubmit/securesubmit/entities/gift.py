"""
    gift.py

    This module defines the gift entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from securesubmit.entities import HpsTransaction


class HpsGiftCard(object):
    track_data = None
    card_number = None
    alias = None
    token_value = None
    encryption_data = None
    pin = None

    @classmethod
    def from_dict(cls, rsp):
        card = cls()
        card.track_data = None if 'TrackData' not in rsp else rsp['TrackData']
        card.card_number = None if 'CardNbr' not in rsp else rsp['CardNbr']
        card.alias = None if 'Alias' not in rsp else rsp['Alias']
        card.token_value = None if 'TokenValue' not in rsp else rsp['TokenValue']
        card.encryption_data = None if 'EncryptionData' not in rsp else rsp['EncryptionData']
        card.pin = None if 'PIN' not in rsp else rsp['PIN']

        return card


class HpsGiftCardActivate(HpsTransaction):
    authorization_code = None
    balance_amount = None
    points_balance_amount = None

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
        alias.gift_card = HpsGiftCard.from_dict(item['CardData'])
        alias.response_code = None if 'RspCode' not in item else item['RspCode']
        alias.response_text = None if 'RspText' not in item else item['RspText']

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
