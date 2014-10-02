"""
    core.py

    The HPS services config.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""


class HpsServicesConfig(object):
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
    soap_service_uri = None
    pay_plan_base_uri = None

    @property
    def service_uri(self):
        return self.soap_service_uri

    @service_uri.setter
    def service_uri(self, value):
        self.soap_service_uri = value
