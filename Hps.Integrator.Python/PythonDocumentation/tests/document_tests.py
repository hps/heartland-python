import unittest
import requests
from securesubmit.tests.test_data import (TestServicesConfig,
                                          TestCardHolder,
                                          TestCreditCard)
from securesubmit.services.gateway import HpsCreditService


class AutoDocTests(unittest.TestCase):
    _base_url = 'http://localhost:58533/api/autodoc/'
    # _base_url = 'https://developer.heartlandpaymentsystems.com/api/autodoc/'
    _headers = {'content-type': 'application/json; charset=utf-8'}
    _language = 'Python'
    _username = 'EntApp_DevPortal@e-hps.com'
    _password = 'S3cureDocument!'

    # def test_create_doc(self):
    #    params = {
    #        'title': 'Test Document3',
    #        'description': 'Some random code to do something...',
    #        'parameters':{'param1', 'param2'},
    #        'returns': 'Nothing'}
    #    response = requests.post(
    #        self._base_url + "createdoc",
    #        params=params,
    #        headers=self._headers)
    #    self.assertEqual(response.status_code, 200, response.content)

    def _add_document(self, title, content):
        data = {'title': title,
                'language': self._language,
                'content': content}
        response = requests.post(self._base_url + 'adddocumentation',
                                 params=data,
                                 headers=self._headers,
                                 auth=(self._username, self._password))
        self.assertEqual(response.status_code, 200, response.content)

    def test_authentication_method(self):
        config = None
        credit_service = None

        code = 'config = HpsServicesConfig()\r\n'
        code += ('config.secret_api_key = '
                 '\'skapi_cert_MdtSAABGSBcAgAZlM8rWSH-fC8SyZBM0Kt7hbSIh8w\''
                 '\r\n\r\n')
        code += 'credit_service = HpsCreditService(config)'

        exec code
        self.assertIsNotNone(config)
        self.assertEqual(
            'skapi_cert_MdtSAABGSBcAgAZlM8rWSH-fC8SyZBM0Kt7hbSIh8w',
            config.secret_api_key)
        self.assertIsNotNone(credit_service)

        self._add_document(
            'Authentication Methods',
            code.replace(
                'skapi_cert_MdtSAABGSBcAgAZlM8rWSH-fC8SyZBM0Kt7hbSIh8w',
                '{{SECRETAPIKEY}}'))

    def test_handling_errors(self):
        code = 'try:\r\n'
        code += ('    credit_service.charge(-5, \'usd\', '
                 'credit_card, card_holder)\r\n')
        code += 'except InvalidRequestException, e:\r\n'
        code += '    # handle error for amount less than zero dollars\r\n'
        code += 'except AuthenticationException, e:\r\n'
        code += '    # handle errors related to your HpsServiceConfig\r\n'
        code += 'except HpsCreditException, e:\r\n'
        code += ('    # handle card-related exceptions: card declined, '
                 'processing error, etc')

        self._add_document('Handling Errors', code)

    def test_create_card_holder(self):
        card_holder = None

        code = 'card_holder = HpsCardHolder()\r\n'
        code += 'card_holder.address.zip = \'75024\''

        exec code
        self.assertIsNotNone(card_holder)
        self.assertEqual('75024', card_holder.address.zip)

        self._add_document('Create a Card Holder', code)

    def test_create_credit_card(self):
        credit_card = None

        code = 'credit_card = HpsCreditCard()\r\n'
        code += 'credit_card.cvv = 123\r\n'
        code += 'credit_card.exp_month = 12\r\n'
        code += 'credit_card.exp_year = 2015\r\n'
        code += 'credit_card.number = \'4012002000060016\'\r\n'

        exec code
        self.assertIsNotNone(credit_card)
        self.assertEqual(123, credit_card.cvv)
        self.assertEqual(12, credit_card.exp_month)
        self.assertEqual(2015, credit_card.exp_year)
        self.assertEqual('4012002000060016', credit_card.number)

        self._add_document('Create a Credit Card', code)

    def test_verify_card(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('response = credit_service.verify('
                 'credit_card, card_holder)\r\n')

        exec code
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '85')

        self._add_document('Verify a Card', code)

    def test_charge_card(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('response = credit_service.charge('
                 '10, \'usd\', credit_card, card_holder)\r\n')

        exec code
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

        self._add_document('Charge a Card', code)

    def test_authorize_card(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('response = credit_service.authorize('
                 '10, \'usd\', credit_card, card_holder)\r\n')

        exec code
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

        self._add_document('Authorize a Charge', code)

    def test_capture_auth(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        auth_response = None
        capture_response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('auth_response = credit_service.authorize('
                 '10, \'usd\', credit_card, card_holder)\r\n')
        code += ('capture_response = credit_service.capture('
                 'auth_response.transaction_id)')

        exec code
        self.assertIsNotNone(auth_response)
        self.assertIsNotNone(capture_response)
        self.assertEqual(auth_response.response_code, '00')
        self.assertEqual(capture_response.response_code, '00')

        self._add_document('Capture an Authorization', code)

    def test_refund_transaction(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        charge_response = None
        refund_response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('charge_response = credit_service.charge('
                 '10, \'usd\', credit_card, card_holder)\r\n')
        code += ('refund_response = credit_service.refund('
                 '10, \'usd\', charge_response.transaction_id)')

        exec code
        self.assertIsNotNone(charge_response)
        self.assertEqual(charge_response.response_code, '00')
        self.assertIsNotNone(refund_response)
        self.assertEqual(refund_response.response_code, '00')

        self._add_document('Refund a Transaction', code)

    def test_reverse_transaction(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        auth_response = None
        reverse_response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('auth_response = credit_service.authorize('
                 '10, \'usd\', credit_card, card_holder)\r\n')
        code += ('reverse_response = credit_service.reverse('
                 'auth_response.transaction_id, 10, \'usd\')')

        exec code
        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.response_code, '00')
        self.assertIsNotNone(reverse_response)
        self.assertEqual(reverse_response.response_code, '00')

        self._add_document('Reverse a Transaction', code)

    def test_void_transaction(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        auth_response = None
        void_response = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += ('auth_response = credit_service.authorize('
                 '10, \'usd\', credit_card, card_holder)\r\n')
        code += ('void_response = credit_service.void('
                 'auth_response.transaction_id)')

        exec code
        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.response_code, '00')
        self.assertIsNotNone(void_response)
        self.assertEqual(void_response.response_code, '00')

        self._add_document('Void a Transaction', code)

    def test_list_transactions(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        items = None

        code = ('items = credit_service.list('
                'datetime.datetime.utcnow() + datetime.timedelta(-10), '
                'datetime.datetime.utcnow())\r\n')

        exec code
        self.assertIsNotNone(items)

        self._add_document('List Transactions', code)

    def test_get_transaction(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        items = None
        charge = None

        code = ('items = credit_service.list('
                'datetime.datetime.utcnow() + datetime.timedelta(-10), '
                'datetime.datetime.utcnow())\r\n')
        code += 'charge = credit_service.get(items[0].transaction_id)'

        exec code
        self.assertIsNotNone(items)
        self.assertIsNotNone(charge)

        self._add_document('Get a Transaction', code)

    def test_request_token(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        credit_card = TestCreditCard.valid_visa
        card_holder = TestCardHolder.valid_card_holder
        charge_response = None
        charge_token = None
        auth_response = None
        auth_token = None

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Credit Card above\r\n\r\n'
        code += '# Request Token with Charge\r\n'
        code += ('charge_response = credit_service.charge('
                 '10, \'usd\', credit_card, card_holder, True)\r\n')
        code += 'charge_token = charge_response.token_data.token_value\r\n\r\n'
        code += '# Request Token with Authorize\r\n'
        code += ('auth_response = credit_service.authorize('
                 '10, \'usd\', credit_card, card_holder, True)\r\n')
        code += 'auth_token = auth_response.token_data.token_value'

        exec code
        self.assertIsNotNone(charge_response)
        self.assertEqual(charge_response.response_code, '00')
        self.assertIsNotNone(charge_token,
                             charge_response.token_data.token_rsp_msg)

        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.response_code, '00')
        self.assertIsNotNone(auth_token,
                             auth_response.token_data.token_rsp_msg)
        self._add_document('Requesting a Token', code)

    def test_charge_token(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        card_holder = TestCardHolder.valid_card_holder
        credit_card = TestCreditCard.valid_visa
        response = None

        charge_response = credit_service.charge(
            10, 'usd', credit_card, card_holder, True)
        self.assertIsNotNone(charge_response)
        self.assertEqual(charge_response.response_code, '00')

        charge_token = charge_response.token_data.token_value

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Requesting a Token above\r\n\r\n'
        code += ('response = credit_service.charge('
                 '10, \'usd\', charge_token, card_holder)\r\n')

        exec code
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')
        self._add_document('Charging a Token', code)

    def test_auth_token(self):
        credit_service = HpsCreditService(
            TestServicesConfig.valid_services_config)
        card_holder = TestCardHolder.valid_card_holder
        credit_card = TestCreditCard.valid_visa
        response = None

        auth_response = credit_service.authorize(
            10, 'usd', credit_card, card_holder, True)
        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.response_code, '00')

        auth_token = auth_response.token_data.token_value

        code = '# See Authentication Methods above\r\n'
        code += '# See Creating a Card Holder above\r\n'
        code += '# See Creating a Requesting a Token above\r\n\r\n'
        code += ('response = credit_service.authorize('
                 '10, \'usd\', auth_token, card_holder)\r\n')

        exec code
        self.assertIsNotNone(response)
        self.assertEqual(response.response_code, '00')

        self._add_document('Authorizing a Token', code)
