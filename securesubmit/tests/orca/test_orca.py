import unittest
from securesubmit.entities.orca import DeviceActivationRequest
from securesubmit.services import HpsOrcaServiceConfig
from securesubmit.services.gateway import HpsOrcaService


class OrcaServiceTests(unittest.TestCase):
    config = HpsOrcaServiceConfig()
    config.username = 'admin'
    config.password = 'password'
    config.hardware_type_name = 'Heartland Mobuyle'
    config.application_id = 'Mobuyle Retail'
    config.is_test = True

    service = HpsOrcaService(config, enable_logging=True)

    def test_full_cycle(self):
        activation_response = self.device_activation()
        key_activation_response = self.device_activation_key(activation_response)
        self.device_parameters(key_activation_response)

    def test_device_api_key(self):
        response = self.service.device_api_key(101436, 5315938, 101433, '777700857994', '$Test1234')
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.secret_api_key)
        self.assertEqual(response.site_id, 101436)
        self.assertEqual(response.device_id, 5315938)

    def device_activation(self):
        request = DeviceActivationRequest()
        request.merchant_id = '777700857994'
        request.device_id = '5315938'
        request.email = 'russell.everett@e-hps.com'

        response = self.service.device_activation(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.activation_code)
        self.assertEqual(response.merchant_id, request.merchant_id)
        self.assertEqual(response.device_id, request.device_id)
        self.assertEqual(response.email, request.email)
        self.assertEqual(response.application_id, self.config.application_id)
        self.assertEqual(response.hardware_type_name, self.config.hardware_type_name)

        return response

    def device_activation_key(self, activation_response):
        response = self.service.device_activation_key(
            activation_response.merchant_id,
            activation_response.activation_code
        )
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.secret_api_key)
        self.assertEqual(response.merchant_id, activation_response.merchant_id)
        self.assertEqual(response.application_id, activation_response.application_id)
        self.assertEqual(response.activation_code, activation_response.activation_code)

        return response

    def device_parameters(self, key_activation_response):
        if self.config.has_emv_data():
            response = self.service.device_parameters(
                key_activation_response.secret_api_key,
                key_activation_response.device_id
            )
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.parameters)
            self.assertEqual(key_activation_response.device_id, response.device_id)
            self.assertEqual(key_activation_response.application_id, response.application_id)
            self.assertEqual(key_activation_response.hardware_type_name, response.hardware_type_name)