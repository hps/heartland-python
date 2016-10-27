"""
    token.py

    The Public API for which you are requesting a token.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

import urllib3.contrib.pyopenssl
import certifi
import jsonpickle
import base64

from securesubmit.infrastructure import HpsException, HpsArgumentException
from securesubmit.serialization import HpsToken, HpsCardToken, HpsSwipeToken, HpsTrackDataToken

urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

class HpsTokenService(object):
    """The Public API for which you are requesting a token."""

    _public_api_key = None
    _url = None

    def __init__(self, public_api_key):
        self._public_api_key = public_api_key

        if public_api_key is None or public_api_key == "":
            raise HpsArgumentException("publicAPIKey is None or Empty.")

        components = public_api_key.split("_")
        if len(components) != 3:
            raise HpsArgumentException(
                "Public API Key must contain three underscores.",
                "publicAPIKey")

        env = components[1].lower()
        if env == "prod":
            self._url = (
                "https://api2.heartlandportico.com/SecureSubmit.v1/api/token")
        else:
            self._url = (
                "https://cert.api2.heartlandportico.com/Hps.Exchange.PosGateway.Hpf.v1/api/token")

    def _request_token(self, input_token):
        """Get a token for a given credit card."""
        try:
            data = jsonpickle.encode(input_token, False, False, True)
            data = data.replace("[", "").replace("]", "")

            headers = {'content-type': 'application/json',
                       'authorization': 'Basic ' + base64.b64encode(self._public_api_key)}

            # response = requests.post(self._url,
            #                          data=data,
            #                          headers=headers,
            #                          auth=(self._public_api_key, None))

            response = http.request('post', self._url, headers=headers, body=data)

            token = HpsToken()
            if len(response.data) > 0:
                token = HpsToken.from_dict(jsonpickle.decode(response.data))

            return token
        except Exception, e:
            raise HpsException(e.message)

    def get_token(self, card):
        return self._request_token(HpsCardToken(card))

    def get_swipe_token(self, swipe):
        return self._request_token(HpsSwipeToken(swipe))

    def get_track_token(self, track, ktb, pin_block=None):
        return self._request_token(HpsTrackDataToken(track, ktb, pin_block))
