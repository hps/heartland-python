import random
import unittest
import datetime
import calendar

from securesubmit.entities.payplan import HpsPayPlanSchedule, HpsPayPlanAmount
from securesubmit.infrastructure.enums import HpsPayPlanPaymentMethodStatus, HpsPayPlanScheduleFrequency, \
    HpsPayPlanScheduleDuration, HpsPayPlanScheduleStatus
from securesubmit.services.gateway import HpsPayPlanService
from securesubmit.tests.test_data import TestServicesConfig


class PayPlanScheduleTests(unittest.TestCase):
    service = HpsPayPlanService(TestServicesConfig.valid_pay_plan_config, True)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    payment_method = service.page(1, 0).find_all_payment_methods(
        {'customerIdentifier': 'SecureSubmit', 'paymentStatus': 'Active'}
    ).results[0]

    def get_schedule_identifier(self):
        return datetime.date.today().strftime('%Y%m%d') + '-SecureSubmit-' + ''.join(random.sample(self.alphabet, 10))

    def last_day_of_the_month(self):
        today = datetime.date.today()
        last_day = str(calendar.monthrange(today.year, today.month)[1])
        return today.strftime('%m{0}%Y').format(last_day)

    def test_add(self):
        schedule = HpsPayPlanSchedule()
        schedule.schedule_identifier = self.get_schedule_identifier()
        schedule.customer_key = self.payment_method.customer_key
        schedule.payment_method_key = self.payment_method.payment_method_key
        schedule.subtotal_amount = HpsPayPlanAmount(100)
        schedule.start_date = self.last_day_of_the_month()
        schedule.frequency = HpsPayPlanScheduleFrequency.WEEKLY
        schedule.duration = HpsPayPlanScheduleDuration.LIMITED_NUMBER
        schedule.number_of_payments = 3
        schedule.reprocessing_count = 2
        schedule.email_receipt = 'Never'
        schedule.email_advance_notice = 'No'
        schedule.schedule_status = HpsPayPlanScheduleStatus.ACTIVE

        response = self.service.add_schedule(schedule)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.schedule_key)

    def test_edit(self):
        results = self.service.page(1, 0).find_all_schedules({'scheduleIdentifier': 'SecureSubmit'})
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        schedule = results.results[0]
        schedule_status = HpsPayPlanScheduleStatus.ACTIVE
        if schedule.schedule_status == HpsPayPlanScheduleStatus.ACTIVE:
            schedule_status = HpsPayPlanScheduleStatus.INACTIVE
        schedule.schedule_status = str(schedule_status)
        schedule.start_date = None

        response = self.service.edit_schedule(schedule)
        self.assertIsNotNone(response)
        self.assertEqual(schedule.schedule_key, response.schedule_key)
        self.assertEqual(schedule.schedule_status, response.schedule_status)

        response = self.service.get_schedule(schedule.schedule_key)
        self.assertIsNotNone(response)
        self.assertEqual(schedule.schedule_key, response.schedule_key)
        self.assertEqual(schedule.schedule_status, response.schedule_status)

    def test_find_all(self):
        results = self.service.find_all_schedules()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) > 0)

    def test_find_all_with_paging(self):
        results = self.service.page(1, 0).find_all_schedules()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

    def test_find_all_with_filters(self):
        results = self.service.find_all_schedules({'scheduleIdentifier': 'SecureSubmit'})
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) >= 1)

    def test_get_by_schedule(self):
        results = self.service.page(1, 0).find_all_schedules()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        response = self.service.get_schedule(results.results[0])
        self.assertIsNotNone(response)
        self.assertEqual(results.results[0].schedule_key, response.schedule_key)

    def test_get_by_key(self):
        results = self.service.page(1, 0).find_all_schedules()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        response = self.service.get_schedule(results.results[0].schedule_key)
        self.assertIsNotNone(response)
        self.assertEqual(results.results[0].schedule_key, response.schedule_key)

    def test_delete_by_schedule(self):
        self.test_add()

        results = self.service.page(1, 0).find_all_schedules()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        response = self.service.delete_schedule(results.results[0])
        self.assertIsNone(response)

    def test_delete_by_key(self):
        self.test_add()

        results = self.service.page(1, 0).find_all_schedules()
        self.assertIsNotNone(results)
        self.assertEqual(True, len(results.results) == 1)

        response = self.service.delete_schedule(results.results[0].schedule_key)
        self.assertIsNone(response)
