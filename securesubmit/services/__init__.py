"""
    core.py

    The HPS services config.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""
import base64
from requests.auth import AuthBase
from securesubmit.infrastructure import HpsException


class _HpsConfigInterface(object):
    UAT_URL = None
    CERT_URL = None
    PROD_URL = None

    def validate(self):
        pass

    def service_uri(self):
        pass


class BasicAuth(AuthBase):
    def __init__(self, secret_api_key):
        self.secret_api_key = secret_api_key

    def __call__(self, r):
        r.headers['Authorization'] = 'Basic ' + base64.b64encode(self.secret_api_key)
        return r


class _HpsRestServiceConfig(_HpsConfigInterface):
    secret_api_key = None
    username = None
    password = None

    @staticmethod
    def get_headers(additional_headers=None):
        headers = {'content-type': 'application/json; charset=utf-8'}
        if additional_headers is not None:
            headers.update(additional_headers)
        return headers

    def basic_authorization(self):
        if self.secret_api_key is not None:
            return BasicAuth(self.secret_api_key)
        elif self.username is not None and self.password is not None:
            return self.username, self.password
        return None


class HpsActivationServiceConfig(_HpsRestServiceConfig):
    _is_test = False

    def __init__(self, is_test=False):
        self._is_test = is_test
        self.UAT_URL = 'https://huds.test.e-hps.com/config-server/v1/'
        self.CERT_URL = 'https://huds.test.e-hps.com/config-server/v1/'
        self.PROD_URL = 'https://huds.prod.e-hps.com/config-server/v1/'

    def service_uri(self):
        return self.CERT_URL if self._is_test else self.PROD_URL

    def validate(self):
        pass


class HpsPayPlanServiceConfig(_HpsRestServiceConfig):
    def __init__(self):
        self.PROD_URL = 'https://api2.heartlandportico.com/payplan.v2/'
        self.CERT_URL = 'https://cert.api2.heartlandportico.com/Portico.PayPlan.v2/'
        self.UAT_URL = 'https://api-uat.heartlandportico.com/payplan.v2/'

    def service_uri(self):
        if '_uat_' in self.secret_api_key:
            return self.UAT_URL
        elif '_cert_' in self.secret_api_key:
            return self.CERT_URL
        else:
            return self.PROD_URL

    def validate(self):
        if self.secret_api_key is None:
            raise HpsException('Invalid Configuration: Secret API Key cannot be None')


class HpsServicesConfig(_HpsConfigInterface):
    credential_token = None
    secret_api_key = None
    license_id = None
    site_id = None
    device_id = None
    version_number = None
    username = None
    password = None
    developer_id = None
    site_trace = None

    def __init__(self):
        self.UAT_URL = 'https://api-uat.heartlandportico.com/paymentserver.v1/PosGatewayService.asmx?wsdl'
        self.CERT_URL = 'https://cert.api2.heartlandportico.com/Hps.Exchange.PosGateway/PosGatewayService.asmx?wsdl'
        self.PROD_URL = 'https://api2.heartlandportico.com/Hps.Exchange.PosGateway/PosGatewayService.asmx?wsdl'

    def service_uri(self):
        if '_uat_' in self.secret_api_key:
            return self.UAT_URL
        elif '_cert_' in self.secret_api_key:
            return self.CERT_URL
        else:
            return self.PROD_URL
