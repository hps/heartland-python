"""
    payplan.py

    This module defines the pay plan entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""
from securesubmit.infrastructure.enums import HpsPayPlanPaymentMethodType


class HpsPayPlanResource(object):
    creation_date = None
    last_change_date = None
    status_set_date = None

    def get_json_data(self):
        fields = dict()

        for k in self.__dict__.keys():
            value = self.__getattribute__(k)
            if k in self.get_editable_fields() and value is not None:
                fields[self.to_camel_case(k)] = value

        return fields

    @staticmethod
    def get_editable_fields():
        pass

    @staticmethod
    def to_camel_case(name):
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])


class HpsPayPlanCustomer(HpsPayPlanResource):
    customer_key = None
    customer_identifier = None
    first_name = None
    last_name = None
    company = None
    customer_status = None
    primary_email = None
    secondary_email = None
    phone_day = None
    phone_day_ext = None
    phone_evening = None
    phone_evening_ext = None
    phone_mobile = None
    phone_mobile_ext = None
    fax = None
    title = None
    department = None
    address_line_1 = None
    address_line_2 = None
    city = None
    country = None
    state_province = None
    zip_postal_code = None
    payment_methods = None
    schedules = None

    @classmethod
    def from_dict(cls, rsp):
        customer = cls()
        customer.customer_key = None if 'customerKey' not in rsp else rsp['customerKey']
        customer.customer_identifier = None if 'customerIdentifier' not in rsp else rsp['customerIdentifier']
        customer.first_name = None if 'firstName' not in rsp else rsp['firstName']
        customer.last_name = None if 'lastName' not in rsp else rsp['lastName']
        customer.company = None if 'company' not in rsp else rsp['company']
        customer.customer_status = None if 'customerStatus' not in rsp else rsp['customerStatus']
        customer.primary_email = None if 'primaryEmail' not in rsp else rsp['primaryEmail']
        customer.phone_day = None if 'phoneDay' not in rsp else rsp['phoneDay']
        customer.phone_day_ext = None if 'phoneDayExt' not in rsp else rsp['phoneDayExt']
        customer.phone_evening = None if 'phoneEvening' not in rsp else rsp['phoneEvening']
        customer.phone_evening_ext = None if 'phoneEveningExt' not in rsp else rsp['phoneEveningExt']
        customer.phone_mobile = None if 'phoneMobile' not in rsp else rsp['phoneMobile']
        customer.phone_mobile_ext = None if 'phoneMobileExt' not in rsp else rsp['phoneMobileExt']
        customer.fax = None if 'fax' not in rsp else rsp['fax']
        customer.title = None if 'title' not in rsp else rsp['title']
        customer.department = None if 'department' not in rsp else rsp['department']
        customer.address_line_1 = None if 'addressLine1' not in rsp else rsp['addressLine1']
        customer.address_line_2 = None if 'addressLine2' not in rsp else rsp['addressLine2']
        customer.city = None if 'city' not in rsp else rsp['city']
        customer.country = None if 'country' not in rsp else rsp['country']
        customer.state_province = None if 'stateProvince' not in rsp else rsp['stateProvince']
        customer.zip_postal_code = None if 'zipPostalCode' not in rsp else rsp['zipPostalCode']
        customer.creation_date = None if 'creationDate' not in rsp else rsp['creationDate']
        customer.last_change_date = None if 'lastChangeDate' not in rsp else rsp['lastChangeDate']
        customer.status_set_date = None if 'statusSetDate' not in rsp else rsp['statusSetDate']

        customer.payment_methods = []
        if 'paymentMethods' in rsp:
            for payment_method in rsp['paymentMethods']:
                customer.payment_methods.append(HpsPayPlanPaymentMethod.from_dict(payment_method))

        customer.schedules = []
        if 'schedules' in rsp:
            for schedule in rsp['schedules']:
                customer.schedules.append(HpsPayPlanSchedule.from_dict(schedule))

        return customer

    @staticmethod
    def get_editable_fields():
        return {
            'customer_identifier',
            'first_name',
            'last_name',
            'company',
            'customer_status',
            'title',
            'department',
            'primary_email',
            'secondary_email',
            'phone_day',
            'phone_day_ext',
            'phone_evening',
            'phone_evening_ext',
            'phone_mobile',
            'phone_mobile_ext',
            'fax',
            'address_line_1',
            'address_line_2',
            'city',
            'state_province',
            'zip_postal_code',
            'country'
        }


class HpsPayPlanPaymentMethod(HpsPayPlanResource):
    payment_method_key = None
    payment_method_type = None
    preferred_payment = None
    payment_status = None
    payment_method_identifier = None
    customer_key = None
    customer_identifier = None
    customer_status = None
    first_name = None
    last_name = None
    company = None
    name_on_account = None
    account_number_last_4 = None
    payment_method = None
    card_brand = None
    expiration_date = None
    cvv_response_code = None
    avs_response_code = None
    ach_type = None
    account_type = None
    routing_number = None
    telephone_indicator = None
    address_line_1 = None
    address_line_2 = None
    city = None
    state_province = None
    zip_postal_code = None
    country = None
    account_holder_yob = None
    drivers_license_state = None
    drivers_license_number = None
    social_security_number_last_4 = None
    has_schedules = None
    has_active_schedules = None

    def get_json_data(self):
        fields = HpsPayPlanResource.get_json_data(self)

        additional_fields = {}
        if self.payment_method_type == HpsPayPlanPaymentMethodType.ACH:
            additional_fields = {
                'telephone_indicator',
                'account_holder_yob',
                'drivers_license_state',
                'drivers_license_number',
                'social_security_number_last_4',
                'ach_type',
                'routing_number',
                'account_number',
                'account_type'
            }
        elif self.payment_method_type == HpsPayPlanPaymentMethodType.CREDIT_CARD:
            additional_fields = {
                'expiration_date',
                'country'
            }

        for k in additional_fields:
            try:
                value = self.__getattribute__(k)
                if value is not None:
                    fields[self.to_camel_case(k)] = value
            except AttributeError:
                pass

        return fields

    @classmethod
    def from_dict(cls, rsp):
        payment_method = cls()
        payment_method.payment_method_key = None if 'paymentMethodKey' not in rsp else rsp['paymentMethodKey']
        payment_method.payment_method_type = None if 'paymentMethodType' not in rsp else rsp['paymentMethodType']
        payment_method.preferred_payment = None if 'preferredPayment' not in rsp else rsp['preferredPayment']
        payment_method.payment_status = None if 'paymentStatus' not in rsp else rsp['paymentStatus']
        payment_method.payment_method_identifier = None
        if 'paymentMethodIdentifier' in rsp:
            payment_method.payment_method_identifier = rsp['paymentMethodIdentifier']
        payment_method.customer_key = None if 'customerKey' not in rsp else rsp['customerKey']
        payment_method.customer_identifier = None if 'customerIdentifier' not in rsp else rsp['customerIdentifier']
        payment_method.customer_status = None if 'customerStatus' not in rsp else rsp['customerStatus']
        payment_method.first_name = None if 'firstName' not in rsp else rsp['firstName']
        payment_method.last_name = None if 'lastName' not in rsp else rsp['lastName']
        payment_method.company = None if 'company' not in rsp else rsp['company']
        payment_method.name_on_account = None if 'nameOnAccount' not in rsp else rsp['nameOnAccount']
        payment_method.account_number_last_4 = None if 'accountNumberLast4' not in rsp else rsp['accountNumberLast4']
        payment_method.payment_method = None if 'paymentMethod' not in rsp else rsp['paymentMethod']
        payment_method.card_brand = None if 'cardBrand' not in rsp else rsp['cardBrand']
        payment_method.expiration_date = None if 'expirationDate' not in rsp else rsp['expirationDate']
        payment_method.cvv_response_code = None if 'cvvResponseCode' not in rsp else rsp['cvvResponseCode']
        payment_method.avs_response_code = None if 'avsResponseCode' not in rsp else rsp['avsResponseCode']
        payment_method.ach_type = None if 'achType' not in rsp else rsp['achType']
        payment_method.account_type = None if 'accountType' not in rsp else rsp['accountType']
        payment_method.routing_number = None if 'routingNumber' not in rsp else rsp['routingNumber']
        payment_method.telephone_indicator = None if 'telephoneIndicator' not in rsp else rsp['telephoneIndicator']
        payment_method.address_line_1 = None if 'addressLine1' not in rsp else rsp['addressLine1']
        payment_method.address_line_2 = None if 'addressLine2' not in rsp else rsp['addressLine2']
        payment_method.city = None if 'city' not in rsp else rsp['city']
        payment_method.state_province = None if 'stateProvince' not in rsp else rsp['stateProvince']
        payment_method.zip_postal_code = None if 'zipPostalCode' not in rsp else rsp['zipPostalCode']
        payment_method.country = None if 'country' not in rsp else rsp['country']
        payment_method.account_holder_yob = None if 'accountHolderYob' not in rsp else rsp['accountHolderYob']
        payment_method.divers_license_number = None
        if 'driversLicenseNumber' in rsp:
            payment_method.divers_license_number = rsp['driversLicenseNumber']
        payment_method.social_security_number_last_4 = None
        if 'socialSecurityNumberLast4' in rsp:
            payment_method.social_security_number_last_4 = rsp['socialSecurityNumberLast4']
        payment_method.has_schedules = None if 'hasSchedules' not in rsp else rsp['hasSchedules']
        payment_method.has_active_schedules = None if 'hasActiveSchedules' not in rsp else rsp['hasActiveSchedules']
        payment_method.creation_date = None if 'creationDate' not in rsp else rsp['creationDate']
        payment_method.last_change_date = None if 'lastChangeDate' not in rsp else rsp['lastChangeDate']
        payment_method.status_set_date = None if 'statusSetDate' not in rsp else rsp['statusSetDate']

        return payment_method

    @staticmethod
    def get_editable_fields(payment_type=None):
        return {
            'preferred_payment',
            'payment_status',
            'payment_method_identifier',
            'name_on_account',
            'address_line_1',
            'address_line_2',
            'city',
            'state_province',
            'zip_postal_code',
        }


class HpsPayPlanSchedule(HpsPayPlanResource):
    schedule_key = None
    schedule_identifier = None
    customer_key = None
    schedule_name = None
    schedule_status = None
    payment_method_key = None
    subtotal_amount = None
    tax_amount = None
    totalAmount = None
    device_id = None
    start_date = None
    processing_date_info = None
    frequency = None
    duration = None
    end_date = None
    processing_count = None
    email_receipt = None
    email_advance_notice = None
    next_processing_date = None
    previous_processing_date = None
    approved_transaction_count = None
    failure_count = None
    total_approved_amount_to_date = None
    number_of_payments = None
    number_of_payment_remaining = None
    cancellation_date = None
    schedule_started = None

    def __init__(self):
        self.email_receipt = 'Never'
        self.email_advance_notice = 'No'

    def get_json_data(self):
        fields = dict()

        editable_fields = self.get_editable_fields(self.schedule_started)
        for k in self.__dict__.keys():
            value = self.__getattribute__(k)
            if k in editable_fields and value is not None:
                fields[self.to_camel_case(k)] = value

        return fields

    @staticmethod
    def get_editable_fields(is_started=False):
        fields = {
            'schedule_name',
            'schedule_status',
            'device_id',
            'payment_method_key',
            'subtotal_amount',
            'tax_amount',
            'number_of_payments_remaining',
            'end_date',
            'cancellation_date',
            'reprocessing_count',
            'email_receipt',
            'email_advance_notice',
            'processing_date_info',
        }

        started_fields = {
            'schedule_identifier',
            'start_date',
            'frequency',
            'duration',
        }

        not_started_fields = {
            'next_processing_date'
        }

        if is_started:
            return fields.union(not_started_fields)
        else: return fields.union(started_fields)

    @classmethod
    def from_dict(cls, rsp):
        schedule = cls()
        schedule.schedule_key = None if 'scheduleKey' not in rsp else rsp['scheduleKey']
        schedule.schedule_identifier = None if 'scheduleIdentifier' not in rsp else rsp['scheduleIdentifier']
        schedule.customer_key = None if 'customerKey' not in rsp else rsp['customerKey']
        schedule.schedule_name = None if 'scheduleName' not in rsp else rsp['scheduleName']
        schedule.schedule_status = None if 'scheduleStatus' not in rsp else rsp['scheduleStatus']
        schedule.payment_method_key = None if 'paymentMethodKey' not in rsp else rsp['paymentMethodKey']
        schedule.subtotal_amount = None if 'subtotalAmount' not in rsp else rsp['subtotalAmount']
        schedule.tax_amount = None if 'taxAmount' not in rsp else rsp['taxAmount']
        schedule.totalAmount = None if 'totalAmount' not in rsp else rsp['totalAmount']
        schedule.device_id = None if 'deviceId' not in rsp else rsp['deviceId']
        schedule.start_date = None if 'startDate' not in rsp else rsp['startDate']
        schedule.processing_date_info = None if 'processingDateInfo' not in rsp else rsp['processingDateInfo']
        schedule.frequency = None if 'frequency' not in rsp else rsp['frequency']
        schedule.duration = None if 'duration' not in rsp else rsp['duration']
        schedule.end_date = None if 'endDate' not in rsp else rsp['endDate']
        schedule.processing_count = None if 'processingCount' not in rsp else rsp['processingCount']
        schedule.email_receipt = None if 'emailReceipt' not in rsp else rsp['emailReceipt']
        schedule.email_advance_notice = None
        if 'emailAdvanceNotice' in rsp:
            schedule.email_advance_notice = rsp['emailAdvanceNotice']
        schedule.next_processing_date = None if 'nextProcessingDate' not in rsp else rsp['nextProcessingDate']
        schedule.previous_processing_date = None
        if 'previousProcessingDate' in rsp:
            schedule.previous_processing_date = rsp['previousProcessingDate']
        schedule.approved_transaction_count = None
        if 'approvedTransactionCount' in rsp:
            schedule.approved_transaction_count = rsp['approvedTransactionCount']
        schedule.failure_count = None if 'failureCount' not in rsp else rsp['failureCount']
        schedule.total_approved_amount_to_date = None
        if 'totalApprovedAmountToDate' in rsp:
            schedule.total_approved_amount_to_date = rsp['totalApprovedAmountToDate']
        schedule.number_of_payments = None if 'numberOfPayments' not in rsp else rsp['numberOfPayments']
        schedule.number_of_payment_remaining = None
        if 'numberOfPaymentsRemaining' in rsp:
            schedule.number_of_payment_remaining = rsp['numberOfPaymentsRemaining']
        schedule.cancellation_date = None if 'cancellationDate' not in rsp else rsp['cancellationDate']
        schedule.schedule_started = None if 'scheduleStarted' not in rsp else rsp['scheduleStarted']
        schedule.creation_date = None if 'creationDate' not in rsp else rsp['creationDate']
        schedule.last_change_date = None if 'lastChangeDate' not in rsp else rsp['lastChangeDate']
        schedule.status_set_date = None if 'statusSetDate' not in rsp else rsp['statusSetDate']

        return schedule


class HpsPayPlanResourceCollection(object):
    offset = None
    limit = None
    total = None
    results = None

    @classmethod
    def from_dict(cls, rsp):
        collection = cls()

        collection.offset = None if 'offset' not in rsp else rsp['offset']
        collection.limit = None if 'limit' not in rsp else rsp['limit']
        collection.total = None if 'total' not in rsp else rsp['total']

        return collection


class HpsPayPlanCustomerCollection(HpsPayPlanResourceCollection):
    @classmethod
    def from_dict(cls, rsp):
        collection = super(HpsPayPlanCustomerCollection, cls).from_dict(rsp)
        if 'results' in rsp:
            collection.results = []

            for result in rsp['results']:
                collection.results.append(HpsPayPlanCustomer.from_dict(result))

        return collection


class HpsPayPlanPaymentMethodCollection(HpsPayPlanResourceCollection):
    @classmethod
    def from_dict(cls, rsp):
        collection = super(HpsPayPlanPaymentMethodCollection, cls).from_dict(rsp)
        if 'results' in rsp:
            collection.results = []

            for result in rsp['results']:
                collection.results.append(HpsPayPlanPaymentMethod.from_dict(result))

        return collection


class HpsPayPlanScheduleCollection(HpsPayPlanResourceCollection):
    @classmethod
    def from_dict(cls, rsp):
        collection = super(HpsPayPlanScheduleCollection, cls).from_dict(rsp)
        if 'results' in rsp:
            collection.results = []

            for result in rsp['results']:
                collection.results.append(HpsPayPlanSchedule.from_dict(result))

        return collection


class HpsPayPlanAmount(object):
    value = None
    currency = 'USD'

    def __init__(self, value, currency=None):
        self.value = value
        if currency is not None:
            self.currency = currency