import datetime
import unittest

from securesubmit.entities.credit import HpsCPCData
from securesubmit.infrastructure import HpsArgumentException
from securesubmit.infrastructure.enums import HpsTaxType, HpsPayPlanScheduleStatus
from securesubmit.services.fluent.gateway import HpsFluentCreditService
from securesubmit.services.gateway import HpsPayPlanService
from securesubmit.services.token import HpsTokenService
from securesubmit.tests.test_data import TestServicesConfig, TestCreditCard, TestCardHolder


class FluentCreditTests(unittest.TestCase):
    service = HpsFluentCreditService().with_config(TestServicesConfig.valid_services_config)
    pp_service = HpsPayPlanService(TestServicesConfig.valid_pay_plan_config)
    schedule = None
    try:
        schedule = pp_service.page(1, 0).find_all_schedules({
            'scheduleStatus': 'Active',
            'scheduleIdentifier': 'SecureSubmit'
        }).results[0]
    except IndexError:
        pass

    def test_authorize_and_capture(self):
        auth_response = self.service.authorize(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(auth_response)
        self.assertEqual('00', auth_response.response_code)

        capture = self.service.capture(auth_response.transaction_id).execute()
        self.assertIsNotNone(capture)
        self.assertEqual('00', capture.response_code)

    def test_authorize_no_amount(self):
        builder = self.service.authorize()\
            .with_currency('usd')\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_authorize_no_currency(self):
        builder = self.service.authorize(10)\
            .with_currency(None)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_authorize_multiple_payment_options(self):
        builder = self.service.authorize(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_token('123456789')\
            .with_card_holder(TestCardHolder.valid_card_holder)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_authorize_with_gratuity(self):
        auth_response = self.service.authorize(13)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_gratuity(3)\
            .execute()

        self.assertIsNotNone(auth_response)
        self.assertEqual('00', auth_response.response_code)

    def test_capture_no_transaction_id(self):
        builder = self.service.capture()
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_charge(self):
        response = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_charge_no_amount(self):
        builder = self.service.charge()\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_charge_no_currency(self):
        builder = self.service.charge(10)\
            .with_currency(None)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_charge_multiple_payment_options(self):
        builder = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_token('123456789')\
            .with_card_holder(TestCardHolder.valid_card_holder)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_charge_with_card_present(self):
        response = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_card_present(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_charge_with_reader_present(self):
        response = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_reader_present(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_charge_with_gratuity(self):
        response = self.service.charge(13)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_gratuity(3)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_cpc_edit(self):
        charge = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(charge.transaction_id)

        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '12345'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = 0.06

        cpc_edit = self.service.cpc_edit()\
            .with_transaction_id(charge.transaction_id)\
            .with_cpc_data(cpc_data)\
            .execute()

        self.assertIsNotNone(cpc_edit)
        self.assertEqual('00', cpc_edit.response_code)

    def test_cpc_edit_no_transaction_id(self):
        cpc_data = HpsCPCData()
        cpc_data.card_holder_po_number = '12345'
        cpc_data.tax_type = HpsTaxType.sales_tax
        cpc_data.tax_amount = 0.06

        builder = self.service.cpc_edit()\
            .with_cpc_data(cpc_data)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_cpc_edit_no_cpc_data(self):
        builder = self.service.cpc_edit()\
            .with_transaction_id('123456')

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_edit(self):
        charge = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(charge.transaction_id)

        edit = self.service.edit()\
            .with_transaction_id(charge.transaction_id)\
            .with_amount(11)\
            .execute()

        self.assertIsNotNone(edit)
        self.assertEqual('00', edit.response_code)

    def test_edit_no_transaction_id(self):
        builder = self.service.edit()\
            .with_amount(11)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_get(self):
        charge = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(charge.transaction_id)

        get = self.service.get(charge.transaction_id).execute()

        self.assertIsNotNone(get)
        self.assertEqual('00', get.response_code)

    def test_get_no_transaction_id(self):
        builder = self.service.get(None)

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_list(self):
        items = self.service.list()\
            .with_utc_start_date(datetime.datetime.utcnow() + datetime.timedelta(-10))\
            .with_utc_end_date(datetime.datetime.utcnow())\
            .execute()
        self.assertIsNotNone(items)

    def test_list_no_start(self):
        builder = self.service.list()\
            .with_utc_end_date(datetime.datetime.utcnow())
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_list_no_end(self):
        builder = self.service.list()\
            .with_utc_start_date(datetime.datetime.utcnow() + datetime.timedelta(-10))
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_refund_by_transaction_id(self):
        charge = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertEqual('00', charge.response_code)
        self.assertIsNotNone(charge.transaction_id)

        refund = self.service.refund(10)\
            .with_transaction_id(charge.transaction_id)\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(refund)
        self.assertEqual('00', refund.response_code)

    def test_refund_by_card(self):
        charge = self.service.charge(11)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertEqual('00', charge.response_code)

        refund = self.service.refund(11)\
            .with_card(TestCreditCard.valid_visa)\
            .execute()
        self.assertIsNotNone(refund)
        self.assertEqual('00', refund.response_code)

    def test_refund_by_token(self):
        charge = self.service.charge(12)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(charge.token_data)

        refund = self.service.refund(12)\
            .with_token(charge.token_data.token_value)\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(refund)
        self.assertEqual('00', refund.response_code)

    def test_refund_no_amount(self):
        builder = self.service.refund()\
            .with_transaction_id('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_refund_no_currency(self):
        builder = self.service.refund(10)\
            .with_currency(None)\
            .with_transaction_id('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_refund_transaction_id_and_card(self):
        builder = self.service.refund(10)\
            .with_transaction_id('123456')\
            .with_card(TestCreditCard.valid_visa)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_refund_transaction_id_and_token(self):
        builder = self.service.refund(10)\
            .with_transaction_id('123456')\
            .with_token('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_refund_card_and_token(self):
        builder = self.service.refund(10)\
            .with_token('123456')\
            .with_card(TestCreditCard.valid_visa)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_refund_no_payment_method(self):
        builder = self.service.refund(10)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_by_transaction_id(self):
        charge = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertEqual('00', charge.response_code)
        self.assertIsNotNone(charge.transaction_id)

        reverse = self.service.reverse(10)\
            .with_transaction_id(charge.transaction_id)\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(reverse)
        self.assertEqual('00', reverse.response_code)

    def test_reverse_by_card(self):
        charge = self.service.charge(11)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertEqual('00', charge.response_code)

        reverse = self.service.reverse(11)\
            .with_card(TestCreditCard.valid_visa)\
            .execute()
        self.assertIsNotNone(reverse)
        self.assertEqual('00', reverse.response_code)

    def test_reverse_by_token(self):
        charge = self.service.charge(12)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_request_multi_use_token(True)\
            .execute()

        self.assertIsNotNone(charge.token_data)

        reverse = self.service.reverse(12)\
            .with_token(charge.token_data.token_value)\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(reverse)
        self.assertEqual('00', reverse.response_code)

    def test_reverse_no_amount(self):
        builder = self.service.reverse()\
            .with_transaction_id('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_no_currency(self):
        builder = self.service.reverse(10)\
            .with_currency(None)\
            .with_transaction_id('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_transaction_id_and_card(self):
        builder = self.service.reverse(10)\
            .with_transaction_id('123456')\
            .with_card(TestCreditCard.valid_visa)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_transaction_id_and_token(self):
        builder = self.service.reverse(10)\
            .with_transaction_id('123456')\
            .with_token('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_card_and_token(self):
        builder = self.service.reverse(10)\
            .with_token('123456')\
            .with_card(TestCreditCard.valid_visa)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_reverse_no_payment_method(self):
        builder = self.service.reverse(10)
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_verify(self):
        verify = self.service.verify()\
            .with_card(TestCreditCard.valid_visa)\
            .execute()
        self.assertIsNotNone(verify)
        self.assertEqual('85', verify.response_code)

    def test_verify_multiple_payment_options(self):
        builder = self.service.verify()\
            .with_card(TestCreditCard.valid_visa)\
            .with_token('123456')
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_void(self):
        charge = self.service.charge(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertEqual('00', charge.response_code)
        self.assertIsNotNone(charge.transaction_id)

        void = self.service.void(charge.transaction_id).execute()
        self.assertIsNotNone(void)
        self.assertEqual('00', void.response_code)

    def test_void_no_transaction_id(self):
        builder = self.service.void()
        self.assertRaises(HpsArgumentException, builder.execute)

    def test_void_partial(self):
        response = self.service.authorize(145)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_allow_partial_auth(True)\
            .execute()

        self.assertEqual('10', response.response_code)
        self.assertIsNotNone(response.transaction_id)
        self.assertIsNotNone(response.authorized_amount)

        void = self.service.void(response.transaction_id)\
            .execute()
        self.assertIsNotNone(void)
        self.assertEqual('00', void.response_code)

    def test_recurring_one_time_with_card(self):
        if self.schedule is None:
            self.skipTest('Schedule was none')

        recurring = self.service.recurring(10)\
            .with_schedule(self.schedule)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_one_time(True)\
            .execute()

        self.assertIsNotNone(recurring)
        self.assertEqual('00', recurring.response_code)

    def test_recurring_one_time_with_token(self):
        if self.schedule is None:
            self.skipTest('Schedule was none')

        token_service = HpsTokenService(TestServicesConfig.valid_services_config.credential_token)
        token_response = token_service.get_token(TestCreditCard.valid_visa)
        self.assertIsNotNone(token_response)
        self.assertIsNotNone(token_response.token_value)

        recurring = self.service.recurring(10)\
            .with_schedule(self.schedule)\
            .with_token(token_response.token_value)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .with_one_time(True)\
            .execute()

        self.assertIsNotNone(recurring)
        self.assertEqual('00', recurring.response_code)

    def test_recurring_with_card(self):
        if self.schedule is None:
            self.skipTest('Schedule was none')

        recurring = self.service.recurring(10)\
            .with_schedule(self.schedule)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(recurring)
        self.assertEqual('00', recurring.response_code)

    def test_recurring_with_token(self):
        if self.schedule is None:
            self.skipTest('Schedule was none')

        token_service = HpsTokenService(TestServicesConfig.valid_services_config.credential_token)
        token_response = token_service.get_token(TestCreditCard.valid_visa)
        self.assertIsNotNone(token_response)
        self.assertIsNotNone(token_response.token_value)

        recurring = self.service.recurring(10)\
            .with_schedule(self.schedule)\
            .with_token(token_response.token_value)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(recurring)
        self.assertEqual('00', recurring.response_code)

    def test_additional_auth(self):
        auth_response = self.service.authorize(10)\
            .with_card(TestCreditCard.valid_visa)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()
        self.assertIsNotNone(auth_response)
        self.assertEqual('00', auth_response.response_code)

        additional_auth = self.service.additional_auth(3)\
            .with_transaction_id(auth_response.transaction_id)\
            .execute()
        self.assertIsNotNone(additional_auth)
        self.assertEqual('00', additional_auth.response_code)

        capture = self.service.capture(auth_response.transaction_id)\
            .with_amount(13)\
            .execute()
        self.assertIsNotNone(capture)
        self.assertEqual('00', capture.response_code)

    def test_additional_auth_no_amount(self):
        builder = self.service.additional_auth()

        self.assertRaises(HpsArgumentException, builder.execute)

    def test_swipe_no_encryption(self):
        response = self.service.charge(10)\
            .with_track_data(TestCreditCard.valid_visa_track)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_swipe_encryption_v1(self):
        response = self.service.charge(10)\
            .with_track_data(TestCreditCard.valid_visa_track_e3v1)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_swipe_encryption_v2(self):
        response = self.service.charge(10)\
            .with_track_data(TestCreditCard.valid_visa_track_e3v2)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_proximity_no_encryption(self):
        response = self.service.charge(10)\
            .with_track_data(TestCreditCard.valid_visa_proximity)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_proximity_encryption_v1(self):
        response = self.service.charge(10)\
            .with_track_data(TestCreditCard.valid_visa_proximity_e3v1)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)

    def test_proximity_encryption_v2(self):
        response = self.service.charge(10)\
            .with_track_data(TestCreditCard.valid_visa_proximity_e3v2)\
            .with_card_holder(TestCardHolder.valid_card_holder)\
            .with_allow_duplicates(True)\
            .execute()

        self.assertIsNotNone(response)
        self.assertEqual('00', response.response_code)