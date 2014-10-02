import unittest
from securesubmit.services.gateway \
    import (HpsCheckService,
            HpsCheckException)
from securesubmit.infrastructure.enums import CheckActionType
from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCheck)


class CheckTests(unittest.TestCase):
    check_service = HpsCheckService(
        TestServicesConfig.valid_services_config)

    def test_check_should_sale(self):
        response = self.check_service.sale(
            CheckActionType.SALE,
            TestCheck.approve, 5.00)
        self.assertIsNotNone(response, 'response is none')
        self.assertEqual(response.response_code, '0')

    def test_check_should_decline(self):
        try:
            self.check_service.sale(
                CheckActionType.SALE,
                TestCheck.decline, 5.00)
            self.fail(
                'The transaction should have thrown an HpsCheckException.')
        except HpsCheckException, e:
            self.assertEqual(e.code, '1')

    def test_check_should_void(self):
        sale_response = self.check_service.sale(
            CheckActionType.SALE,
            TestCheck.approve, 5.00)
        void_response = self.check_service.void(sale_response.transaction_id)
        self.assertIsNotNone(void_response, 'response is none')
        self.assertEqual(void_response.response_code, '0')
