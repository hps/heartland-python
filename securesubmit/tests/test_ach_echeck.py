import unittest

from securesubmit.services.gateway import HpsCheckService
from securesubmit.infrastructure.enums import\
    DataEntryModeType, CheckTypeType, AccountTypeType, SecCode
from securesubmit.tests.test_data \
    import (TestServicesConfig,
            TestCheck)


class CheckTests(unittest.TestCase):
    """ ach debit consumer tests """

    def test_ach_debit_consumer_swipe(self):
        check = TestCheck.certification
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_services_config, True)
        response = check_service.sale(check, 11.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_ach_debit_consumer_swipe_checking_business(self):
        check = TestCheck.certification
        check.check_type = CheckTypeType.business
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 12.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_consumer_swipe_savings_personal(self):
        check = TestCheck.certification
        check.account_type = AccountTypeType.savings
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 14.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_consumer_swipe_savings_business(self):
        check = TestCheck.certification
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 15.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_consumer(self):
        check = TestCheck.certification

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 16.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_ach_debit_consumer_checking_business(self):
        check = TestCheck.certification
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 17.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_consumer_savings_personal(self):
        check = TestCheck.certification
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 18.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_consumer_savings_business(self):
        check = TestCheck.certification
        check.check_type = CheckTypeType.business
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 19.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    """ end ach debit consumer tests """

    """ begin ach debit corporate tests """

    def test_ach_debit_corporate_swipe(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.data_entry_mode = DataEntryModeType.swipe
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 11.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_corporate_swipe_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.check_type = CheckTypeType.business
        check.data_entry_mode = DataEntryModeType.swipe
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 12.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_ach_debit_corporate_swipe_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.account_type = AccountTypeType.savings
        check.data_entry_mode = DataEntryModeType.swipe
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 14.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_corporate_swipe_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business
        check.data_entry_mode = DataEntryModeType.swipe
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 15.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_consumer_corporate(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 16.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_corporate_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.check_type = CheckTypeType.business
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 17.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_ach_debit_corporate_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.account_type = AccountTypeType.savings
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 18.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_ach_debit_corporate_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ccd
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business
        check.check_holder.check_name = 'Heartland Pays'

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 19.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    """ end ach debit corporate tests """

    """ begin ach gold tests """

    def test_e_gold_swipe(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 11.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_gold_swipe_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.check_type = CheckTypeType.business
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 12.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_gold_swipe_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 14.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_e_gold_swipe_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 15.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_gold(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ppd

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 16.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_gold_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ppd
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 17.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_gold_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ppd
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 18.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_e_gold_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.ppd
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 19.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    """ end ach gold tests """

    """ begin ach silver tests """

    def test_e_silver_swipe(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 11.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_silver_swipe_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.check_type = CheckTypeType.business
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 12.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_silver_swipe_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 14.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_e_silver_swipe_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 15.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_silver(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 16.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_silver_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 17.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_silver_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 18.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

        void_response = check_service.void(response.transaction_id)
        self.assertEqual('0', void_response.response_code)
        self.assertEqual('Transaction Approved', void_response.response_text)

    def test_e_silver_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.pop
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_e_gold_config)
        response = check_service.sale(check, 19.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    """ end ach e silver tests """

    """ begin ach e bronze tests """

    def test_e_bronze_verify_swipe_checking_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_swipe_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_swipe_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_swipe_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_checking_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_checking_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_savings_personal(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 19.00)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)

    def test_e_bronze_verify_savings_business(self):
        check = TestCheck.certification
        check.sec_code = SecCode.e_bronze
        check.data_entry_mode = DataEntryModeType.swipe
        check.account_type = AccountTypeType.savings
        check.check_type = CheckTypeType.business

        check_service = HpsCheckService(TestServicesConfig.valid_services_config)
        response = check_service.sale(check, 1)
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)
        self.assertEqual('Transaction Approved', response.response_text)