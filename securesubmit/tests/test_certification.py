import unittest

from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCreditCard,
            TestCardHolder)
from securesubmit.services.gateway \
    import (HpsCreditService)


class Certification(unittest.TestCase):
    client = HpsCreditService(TestServicesConfig.valid_services_config)

    # CREDIT SALE
    def test_credit_sale_visa(self):
        self.client.charge(
            10.00, "USD",
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip)

    def test_credit_sale_mastercard(self):
        self.client.charge(
            11.00, "USD",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip)

    def test_credit_sale_discover(self):
        self.client.charge(
            12.00, "USD",
            TestCreditCard.valid_discover,
            TestCardHolder.cert_holder_long_zip_no_street)

    def test_credit_sale_amex(self):
        self.client.charge(
            13.00, "USD",
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street)

    # CREDIT AUTH & CAPTURE
    def test_credit_auth_visa(self):
        response = self.client.authorize(
            15.00, "USD",
            TestCreditCard.valid_visa,
            TestCardHolder.cert_holder_long_zip)
        self.client.capture(response.transaction_id)

    def test_credit_auth_mastercard(self):
        response = self.client.authorize(
            16.00, "USD",
            TestCreditCard.valid_mastercard,
            TestCardHolder.cert_holder_short_zip)
        self.client.capture(response.transaction_id)

    def test_credit_auth_discover(self):
        response = self.client.authorize(
            17.00, "USD",
            TestCreditCard.valid_discover,
            TestCardHolder.cert_holder_long_zip_no_street)
        self.client.capture(response.transaction_id)

    def test_credit_auth_amex(self):
        response = self.client.authorize(
            18.00, "USD",
            TestCreditCard.valid_amex,
            TestCardHolder.cert_holder_short_zip_no_street)
        self.client.capture(response.transaction_id)

    # CREDIT ACCOUNT VERIFY
    def test_credit_account_verify_visa(self):
        self.client.verify(TestCreditCard.valid_visa_no_cvv)

    def test_credit_account_verify_mastercard(self):
        self.client.verify(TestCreditCard.valid_mastercard_no_cvv)

    def test_credit_account_verify_discover(self):
        self.client.verify(TestCreditCard.valid_discover_no_cvv)

    # CREDIT REVERSAL
    def test_credit_reversal_visa(self):
        response = self.client.authorize(
            60.00, "USD",
            TestCreditCard.valid_visa_no_cvv)
        self.client.capture(response.transaction_id)
        self.client.reverse(response.transaction_id, 60, "USD")

    def test_credit_reversal_mastercard(self):
        response = self.client.authorize(
            61.00, "USD",
            TestCreditCard.valid_mastercard_no_cvv)
        self.client.capture(response.transaction_id)
        self.client.reverse(response.transaction_id, 61, "USD")

    def test_credit_reversal_discover(self):
        response = self.client.authorize(
            62.00, "USD",
            TestCreditCard.valid_discover_no_cvv)
        self.client.capture(response.transaction_id)
        self.client.reverse(response.transaction_id, 62, "USD")

    def test_credit_reversal_amex(self):
        response = self.client.authorize(
            63.00, "USD",
            TestCreditCard.valid_amex_no_cvv)
        self.client.capture(response.transaction_id)
        self.client.reverse(response.transaction_id, 63, "USD")

    # CREDIT RETURN
    def test_credit_return_visa(self):
        response = self.client.charge(
            50.00, "USD",
            TestCreditCard.valid_visa_no_cvv)
        self.client.refund(50, "USD", response.transaction_id)

    def test_credit_return_mastercard(self):
        response = self.client.charge(
            51.00, "USD",
            TestCreditCard.valid_mastercard_no_cvv)
        self.client.refund(51, "USD", response.transaction_id)

    def test_credit_return_discover(self):
        response = self.client.charge(
            52.00, "USD",
            TestCreditCard.valid_discover_no_cvv)
        self.client.refund(52, "USD", response.transaction_id)

    def test_credit_return_amex(self):
        response = self.client.charge(
            53.00, "USD",
            TestCreditCard.valid_amex_no_cvv)
        self.client.refund(53, "USD", response.transaction_id)
