import unittest
import base64

class RamblerTests(unittest.TestCase):
    def test_decode(self):
        hex_encoded_track = 'DEF9B18FDEBF65D82164390C4A5D290C52EF8E9AAB02E598FC49CBB5D8D97ADA454F1279977A0003AB07EE90791C580990E1A68D35C9473F1ADE3E971112378E5ABB15B9261EAF3F11728E652DC0233DC65BD6774BE9886626F507C15E4FCB75ED8918A6F21C98170DC15C65F031B7D2C027374150B4A883A9F596C83BE63930'
        hex_encoded_ksn = 'FFFFC120119009C0000B'

        submission_track = base64.b64encode(hex_encoded_track.decode('hex'))
        submission_ksn = base64.b64encode(hex_encoded_ksn.decode('hex'))

        self.assertEqual('3vmxj96/ZdghZDkMSl0pDFLvjpqrAuWY/EnLtdjZetpFTxJ5l3oAA6sH7pB5HFgJkOGmjTXJRz8a3j6XERI3jlq7FbkmHq8/EXKOZS3AIz3GW9Z3S+mIZib1B8FeT8t17YkYpvIcmBcNwVxl8DG30sAnN0FQtKiDqfWWyDvmOTA=', submission_track)
        self.assertEqual('///BIBGQCcAACw==', submission_ksn)

