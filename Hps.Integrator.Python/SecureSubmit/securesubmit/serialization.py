"""
    serialization.py

    defines the serialization mediums used.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from securesubmit.entities.credit import HpsCreditCard


class HpsError(object):
    type = None
    message = None
    code = None
    param = None

    @classmethod
    def from_dict(cls, data):
        error = cls()
        for key in data:
            setattr(error, key, data[key])
        return error


class HpsToken:
    object = None
    token_type = None
    token_value = None
    token_expire = None
    error = None

    def __init__(self):
        self.object = 'token'
        self.token_type = 'supt'

    @classmethod
    def from_dict(cls, data):
        token = cls()
        for key in data:
            if key == 'error':
                token.error = HpsError.from_dict(data[key])
            else:
                setattr(token, key, data[key])
        return token


class HpsCardToken(HpsToken):
    card = None

    def __init__(self, card_data=None, cvc=None, exp_month=None, exp_year=None):
        HpsToken.__init__(self)

        if card_data is not None:
            if isinstance(card_data, HpsCreditCard):
                self.card = Card(card_data.number,
                                 card_data.cvv,
                                 card_data.exp_month,
                                 card_data.exp_year)
            else:
                self.card = Card(card_data, cvc, exp_month, exp_year)


class HpsSwipeToken(HpsToken):
    card = None

    def __init__(self, swipe_data=None):
        HpsToken.__init__(self)

        if swipe_data is not None:
            self.card = CardSwipe(swipe_data)


class HpsTrackDataToken(HpsToken):
    encryptedcard = None

    def __init__(self, track_data=None, track_number=None, ktb=None, pin_block=None):
        HpsToken.__init__(self)

        if track_data is not None:
            if isinstance(track_data, EncryptedCard):
                self.encryptedcard = EncryptedCard()
            else:
                self.encryptedcard = EncryptedCard(track_data, track_number, ktb, pin_block)


class Card(object):
    number = None
    cvc = None
    exp_month = None
    exp_year = None

    def __init__(self, number, cvc, exp_month, exp_year):
        self.number = number
        self.cvc = cvc
        self.exp_month = exp_month
        self.exp_year = exp_year


class CardSwipe(object):
    track_method = None
    track = None

    def __init__(self, swipe_data):
        self.track_method = 'swipe'
        self.track = swipe_data


class EncryptedCard:
    track = None
    track_method = None
    track_number = None
    pin_block = None
    ktb = None

    def __init__(self, track=None, track_number=None, ktb=None, pin_block=None):
        self.track = track
        self.track_number = track_number
        self.ktb = ktb
        self.pin_block = pin_block
        self.track_method = 'swipe'
