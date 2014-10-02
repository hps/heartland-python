"""
    payplan.py

    This module defines the payplan entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from securesubmit.entities import HpsConsumer, HpsAddress
from securesubmit.infrastructure.enums import HpsPayPlanCustomerStatus


class HpsPayPlanCustomer(HpsConsumer):
    customer_key = None
    customer_id = None
    company = None
    customer_status = None
    title = None
    department = None
    secondary_email = None
    phone_ext = None
    phone_evening = None
    phone_evening_ext = None
    phone_mobile = None
    phone_mobile_ext = None
    fax = None
    status_set_date = None
    creation_date = None
    last_change_date = None

    @classmethod
    def from_dto(cls, dto):
        result = HpsPayPlanCustomer()
        result.company = dto.company
        result.customer_id = dto.customer_identifier
        result.customer_status = HpsPayPlanCustomerStatus.inactive
        if dto.customer_status == 'Active':
            result.customer_status = HpsPayPlanCustomerStatus.inactive
        result.department = dto.department
        result.fax = dto.fax
        result.phone_evening = dto.phone_evening
        result.phone_evening_ext = dto.phone_evening_ext
        result.phone_ext = dto.phone_day_ext
        result.phone_mobile = dto.phone_mobile
        result.phone_mobile_ext = dto.phone_mobile_ext
        result.secondary_email = dto.secondary_email
        result.title = dto.title

        return HpsPayPlanCustomer._hydrate_consumer_info(dto, result)

    @staticmethod
    def _hydrate_consumer_info(dto, consumer):
        consumer.address = HpsAddress()
        consumer.address.address = dto.address_line_1
        consumer.address.city = dto.city
        consumer.address.country = dto.country
        consumer.address.state = dto.state_province
        consumer.address.zip = dto.zip_postal_code

        consumer.email = dto.primary_email
        consumer.first_name = dto.first_name
        consumer.last_name = dto.last_name
        consumer.phone_day = dto.phone_day

        return consumer


class HpsPayPlanCustomerEditOptions(HpsConsumer):
    customer_id = None
    company = None
    customer_status = None
    title = None
    department = None
    secondary_email = None
    phone_ext = None
    phone_evening = None
    phone_evening_ext = None
    phone_mobile = None
    phone_mobile_ext = None
    fax = None


class HpsPayPlanCustomerQueryOptions(object):
    customer_id = None
    company = None
    first_name = None
    last_name = None
    primary_email = None
    customer_status = None
    phone_number = None
    city = None
    state_province = None
    zip_postal_code = None
    country = None
    has_schedules = None
    has_active_schedules = None
    has_payment_methods = None
    has_active_payment_methods = None
