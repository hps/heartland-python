import unittest
from securesubmit.services import HpsActivationServiceConfig
from securesubmit.services.gateway import HpsActivationService


class ActivationServiceTests(unittest.TestCase):
    config = HpsActivationServiceConfig(is_test=True)

    service = HpsActivationService(config, enable_logging=True)

    def test_device_activation_key(self):
        """
            test values for merchant_id and activation_code may be obtained from integration@e-hps.com
        """

        response = self.service.device_activation_key('777700857994', '378326')
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.secret_api_key)

        return response
