import random
import unittest
import datetime

from securesubmit.entities.payplan import HpsPayPlanCustomer, HpsPayPlanPaymentMethod, HpsPayPlanSchedule, \
    HpsPayPlanAmount
from securesubmit.infrastructure import HpsException, HpsCreditException, HpsCheckException
from securesubmit.infrastructure.enums import HpsPayPlanCustomerStatus, HpsPayPlanPaymentMethodType, \
    HpsPayPlanScheduleStatus, HpsPayPlanScheduleFrequency, HpsPayPlanScheduleDuration
from securesubmit.services import HpsServicesConfig, HpsPayPlanServiceConfig
from securesubmit.services.fluent.gateway import HpsFluentCreditService, HpsFluentCheckService
from securesubmit.services.gateway import HpsPayPlanService, HpsBatchService


class RecurringTests(unittest.TestCase):
    pp_config = HpsPayPlanServiceConfig()
    pp_config.secret_api_key = 'skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A'
    service = HpsPayPlanService(pp_config, True)

    config = HpsServicesConfig()
    config.secret_api_key = 'skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A'

    batch_service = HpsBatchService(config)
    credit_service = HpsFluentCreditService().with_config(config)
    check_service = HpsFluentCheckService().with_config(config)

    customer_person_key = None
    customer_company_key = None
    payment_method_key_visa = None
    payment_method_key_mastercard = None
    payment_method_key_check_ppd = None
    payment_method_key_check_ccd = None
    schedule_key_visa = None
    schedule_key_mastercard = None
    schedule_key_check_ppd = None
    schedule_key_check_ccd = None

    today_date = datetime.date.today().strftime('%Y%m%d')
    identifier_base = '{0}-{1}-' + ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))

    def get_identifier(self, identifier):
        rvalue = self.identifier_base.format(self.today_date, identifier)
        print rvalue
        return rvalue

    """ Batching """

    def test_000_close_batch(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")
            print 'batch id: {0}'.format(response.id)
            print 'sequence number: {0}'.format(response.sequence_number)
        except HpsException, e:
            if e.message != 'Transaction was rejected because it requires a batch to be open.':
                self.fail(e.message)

    """ Clean up """

    def test_999_clean_up(self):
        #  remove the schedules
        sch_results = self.service.page(500, 0).find_all_schedules()
        for schedule in sch_results.results:
            try:
                self.service.delete_schedule(schedule, True)
            except HpsException:
                pass

        #  remove payment methods
        pm_results = self.service.page(500, 0).find_all_payment_methods()
        for pm in pm_results.results:
            try:
                self.service.delete_payment_method(pm, True)
            except HpsException:
                pass

        #  remove customers
        cust_results = self.service.page(500, 0).find_all_customers()
        for c in cust_results.results:
            try:
                self.service.delete_customer(c, True)
            except HpsException:
                pass
        pass

    """ Customer Setup """

    def test_001_add_customer_person(self):
        customer = HpsPayPlanCustomer()
        customer.customer_identifier = self.get_identifier('Person')
        customer.first_name = 'John'
        customer.last_name = 'Doe'
        customer.customer_status = HpsPayPlanCustomerStatus.ACTIVE
        customer.primary_email = 'john.doe@email.com'
        customer.address_line_1 = '123 Main St'
        customer.city = 'Dallas'
        customer.state_province = 'TX'
        customer.zip_postal_code = '98765'
        customer.country = 'USA'
        customer.phone_day = '5551112222'

        response = self.service.add_customer(customer)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.customer_key)
        self.__class__.customer_person_key = response.customer_key

    def test_002_add_customer_company(self):
        customer = HpsPayPlanCustomer()
        customer.customer_identifier = self.get_identifier('Business')
        customer.company = 'AcmeCo'
        customer.customer_status = HpsPayPlanCustomerStatus.ACTIVE
        customer.primary_email = 'acme@email.com'
        customer.address_line_1 = '987 Elm St'
        customer.city = 'Princeton'
        customer.state_province = 'NJ'
        customer.zip_postal_code = '12345'
        customer.country = 'USA'
        customer.phone_day = '5551112222'

        response = self.service.add_customer(customer)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.customer_key)
        self.__class__.customer_company_key = response.customer_key

    """ Payment Setup """

    def test_003_add_payment_credit_visa(self):
        payment_method = HpsPayPlanPaymentMethod()
        payment_method.payment_method_identifier = self.get_identifier('CreditV')
        payment_method.payment_method_type = HpsPayPlanPaymentMethodType.CREDIT_CARD
        payment_method.name_on_account = 'John Doe'
        payment_method.account_number = '4012002000060016'
        payment_method.expiration_date = '1225'
        payment_method.customer_key = self.__class__.customer_person_key
        payment_method.country = 'USA'

        response = self.service.add_payment_method(payment_method)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.payment_method_key)
        self.__class__.payment_method_key_visa = response.payment_method_key

    def test_004_add_payment_credit_mastercard(self):
        payment_method = HpsPayPlanPaymentMethod()
        payment_method.payment_method_identifier = self.get_identifier('CreditMC')
        payment_method.payment_method_type = HpsPayPlanPaymentMethodType.CREDIT_CARD
        payment_method.name_on_account = 'John Doe'
        payment_method.account_number = '5473500000000014'
        payment_method.expiration_date = '1225'
        payment_method.customer_key = self.__class__.customer_person_key
        payment_method.country = 'USA'

        response = self.service.add_payment_method(payment_method)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.payment_method_key)
        self.__class__.payment_method_key_mastercard = response.payment_method_key

    def test_005_add_payment_check_ppd(self):
        payment_method = HpsPayPlanPaymentMethod()
        payment_method.payment_method_identifier = self.get_identifier('CheckPPD')
        payment_method.payment_method_type = HpsPayPlanPaymentMethodType.ACH
        payment_method.ach_type = 'Checking'
        payment_method.account_type = 'Personal'
        payment_method.telephone_indicator = 0
        payment_method.routing_number = '490000018'
        payment_method.name_on_account = 'John Doe'
        payment_method.drivers_license_number = '7418529630'
        payment_method.drivers_license_state = 'TX'
        payment_method.account_number = '24413815'
        payment_method.address_line_1 = '123 Main St'
        payment_method.city = 'Dallas'
        payment_method.state_province = 'TX'
        payment_method.zip_postal_code = '98765'
        payment_method.customer_key = self.__class__.customer_person_key
        payment_method.country = 'USA'
        payment_method.account_holder_yob = '1989'

        response = self.service.add_payment_method(payment_method)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.payment_method_key)
        self.__class__.payment_method_key_check_ppd = response.payment_method_key

    def test_006_add_payment_check_ccd(self):
        payment_method = HpsPayPlanPaymentMethod()
        payment_method.payment_method_identifier = self.get_identifier('CheckCCD')
        payment_method.payment_method_type = HpsPayPlanPaymentMethodType.ACH
        payment_method.ach_type = 'Checking'
        payment_method.account_type = 'Business'
        payment_method.telephone_indicator = 0
        payment_method.routing_number = '490000018'
        payment_method.name_on_account = 'Acme Co'
        payment_method.drivers_license_number = '3692581470'
        payment_method.drivers_license_state = 'TX'
        payment_method.account_number = '24413815'
        payment_method.address_line_1 = '987 Elm St'
        payment_method.city = 'Princeton'
        payment_method.state_province = 'NJ'
        payment_method.zip_postal_code = '12345'
        payment_method.customer_key = self.__class__.customer_company_key
        payment_method.country = 'USA'
        payment_method.account_holder_yob = '1989'

        response = self.service.add_payment_method(payment_method)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.payment_method_key)
        self.__class__.payment_method_key_check_ccd = response.payment_method_key

    """ Payment Setup - Declined """

    def test_007_add_payment_check_ppd(self):
        payment_method = HpsPayPlanPaymentMethod()
        payment_method.payment_method_identifier = self.get_identifier('CheckPPD')
        payment_method.payment_method_type = HpsPayPlanPaymentMethodType.ACH
        payment_method.ach_type = 'Checking'
        payment_method.account_type = 'Personal'
        payment_method.telephone_indicator = 0
        payment_method.routing_number = '490000050'
        payment_method.name_on_account = 'John Doe'
        payment_method.drivers_license_number = '7418529630'
        payment_method.account_number = '24413815'
        payment_method.address_line_1 = '123 Main St'
        payment_method.city = 'Dallas'
        payment_method.state_province = 'TX'
        payment_method.zip_postal_code = '98765'
        payment_method.customer_key = self.customer_person_key

        self.assertRaises(HpsException, self.service.add_payment_method, payment_method)

    """ Recurring Billing using PayPlan - Managed Schedule """

    def test_008_add_schedule_credit_visa(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_identifier('CreditV')
        schedule.customer_key = self.__class__.customer_person_key
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        schedule.payment_method_key = self.__class__.payment_method_key_visa
        schedule.subtotal_amount = HpsPayPlanAmount(3001)
        schedule.start_date = '02012027'
        schedule.frequency = HpsPayPlanScheduleFrequency.WEEKLY
        schedule.duration = HpsPayPlanScheduleDuration.ONGOING
        schedule.reprocessing_count = 1

        response = self.service.add_schedule(schedule)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.schedule_key)
        self.__class__.schedule_key_visa = response.schedule_key

    def test_009_add_schedule_credit_mastercard(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_identifier('CreditMC')
        schedule.customer_key = self.__class__.customer_person_key
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        schedule.payment_method_key = self.__class__.payment_method_key_mastercard
        schedule.subtotal_amount = HpsPayPlanAmount(3002)
        schedule.start_date = '02012027'
        schedule.frequency = HpsPayPlanScheduleFrequency.WEEKLY
        schedule.duration = HpsPayPlanScheduleDuration.END_DATE
        schedule.end_date = '04012027'
        schedule.reprocessing_count = 2

        response = self.service.add_schedule(schedule)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.schedule_key)
        self.__class__.schedule_key_mastercard = response.schedule_key

    def test_010_add_schedule_check_ppd(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_identifier('CheckPPD')
        schedule.customer_key = self.__class__.customer_person_key
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        schedule.payment_method_key = self.__class__.payment_method_key_check_ppd
        schedule.subtotal_amount = HpsPayPlanAmount(3003)
        schedule.start_date = '02012027'
        schedule.frequency = HpsPayPlanScheduleFrequency.MONTHLY
        schedule.duration = HpsPayPlanScheduleDuration.LIMITED_NUMBER
        schedule.reprocessing_count = 1
        schedule.number_of_payments = 2
        schedule.processing_date_info = '1'

        response = self.service.add_schedule(schedule)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.schedule_key)
        self.__class__.schedule_key_check_ppd = response.schedule_key

    def test_011_add_schedule_check_ccd(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_identifier('CheckCCD')
        schedule.customer_key = self.__class__.customer_company_key
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        schedule.payment_method_key = self.__class__.payment_method_key_check_ccd
        schedule.subtotal_amount = HpsPayPlanAmount(3004)
        schedule.start_date = '02012027'
        schedule.frequency = HpsPayPlanScheduleFrequency.BIWEEKLY
        schedule.duration = HpsPayPlanScheduleDuration.ONGOING
        schedule.reprocessing_count = 1

        response = self.service.add_schedule(schedule)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.schedule_key)
        self.__class__.schedule_key_check_ccd = response.schedule_key

    """ Recurring Billing - Declined """

    def test_012_add_schedule_credit_visa(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_identifier('CreditV')
        schedule.customer_key = self.__class__.customer_person_key
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        schedule.payment_method_key = self.__class__.payment_method_key_visa
        schedule.subtotal_amount = HpsPayPlanAmount(1008)
        schedule.start_date = '02012027'
        schedule.frequency = HpsPayPlanScheduleFrequency.WEEKLY
        schedule.duration = HpsPayPlanScheduleDuration.ONGOING
        schedule.reprocessing_count = 2

        self.assertRaises(HpsException, self.service.add_schedule, schedule)

    def test_013_add_schedule_check_ppd(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_identifier('CheckPPD')
        schedule.customer_key = self.__class__.customer_person_key
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        schedule.payment_method_key = self.__class__.payment_method_key_check_ppd
        schedule.subtotal_amount = HpsPayPlanAmount(2501)
        schedule.start_date = '02012027'
        schedule.frequency = HpsPayPlanScheduleFrequency.WEEKLY
        schedule.duration = HpsPayPlanScheduleDuration.LIMITED_NUMBER
        schedule.reprocessing_count = 1
        schedule.number_of_payments = 2
        schedule.processing_date_info = '1'

        self.assertRaises(HpsException, self.service.add_schedule, schedule)

    """ Recurring Billing using PayPlan - Managed Schedule """

    def test_014_recurring_billing_visa(self):
        response = self.credit_service.recurring(20.01)\
            .with_payment_method_key(self.__class__.payment_method_key_visa)\
            .with_schedule(self.__class__.schedule_key_visa)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_015_recurring_billing_mastercard(self):
        response = self.credit_service.recurring(20.02)\
            .with_payment_method_key(self.__class__.payment_method_key_mastercard)\
            .with_schedule(self.__class__.schedule_key_mastercard)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_016_recurring_billing_check_ppd(self):
        response = self.check_service.recurring(20.03)\
            .with_payment_method_key(self.__class__.payment_method_key_check_ppd)\
            .with_schedule(self.__class__.schedule_key_check_ppd)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_017_recurring_billing_check_ccd(self):
        response = self.check_service.recurring(20.04)\
            .with_payment_method_key(self.__class__.payment_method_key_check_ccd)\
            .with_schedule(self.__class__.schedule_key_check_ccd)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ One Time Bill Payment """

    def test_018_recurring_billing_visa(self):
        response = self.credit_service.recurring(20.06)\
            .with_payment_method_key(self.__class__.payment_method_key_visa)\
            .with_one_time(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_019_recurring_billing_mastercard(self):
        response = self.credit_service.recurring(20.07)\
            .with_payment_method_key(self.__class__.payment_method_key_mastercard)\
            .with_one_time(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_020_recurring_billing_check_ppd(self):
        response = self.check_service.recurring(20.08)\
            .with_payment_method_key(self.__class__.payment_method_key_check_ppd)\
            .with_one_time(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    def test_021_recurring_billing_check_ccd(self):
        response = self.check_service.recurring(20.09)\
            .with_payment_method_key(self.__class__.payment_method_key_check_ccd)\
            .with_one_time(True)\
            .execute()
        self.assertIsNotNone(response)
        self.assertEqual('0', response.response_code)

    """ One Time Bill Payment - Declined """

    def test_022_recurring_billing_visa(self):
        builder = self.credit_service.recurring(10.08)\
            .with_payment_method_key(self.__class__.payment_method_key_visa)\
            .with_one_time(True)
        self.assertRaises(HpsCreditException, builder.execute)

    def test_023_recurring_billing_check_ppd(self):
        builder = self.check_service.recurring(25.02)\
            .with_payment_method_key(self.__class__.payment_method_key_check_ppd)\
            .with_one_time(True)
        self.assertRaises(HpsCheckException, builder.execute)

    """ CLOSE BATCH """

    def test_998_close_batch(self):
        try:
            response = self.batch_service.close_batch()
            if response is None:
                self.fail("Response is None")

            print 'batch id: {0}'.format(response.id)
            print 'sequence number: {0}'.format(response.sequence_number)
            # print self.__class__.customer_person_key
            # print self.__class__.customer_company_key
            # print self.__class__.payment_method_key_visa
            # print self.__class__.payment_method_key_mastercard
            # print self.__class__.payment_method_key_check_ppd
            # print self.__class__.payment_method_key_check_ccd
            # print self.__class__.schedule_key_visa
            # print self.__class__.schedule_key_mastercard
            # print self.__class__.schedule_key_check_ppd
            # print self.__class__.schedule_key_check_ccd
        except HpsException, e:
            self.fail(e.message)