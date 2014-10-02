"""
    dto.py

    defines the payplan data transfer objects.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from securesubmit.infrastructure.enums import HpsPayPlanCustomerStatus


class HpsPayPlanResponse(object):
    total_result_count = None
    results = None


class _PayPlanCustomer(object):
    customer_key = None
    customer_identifier = None
    first_name = None
    last_name = None
    company = None
    customer_status = None
    title = None
    department = None
    primary_email = None
    secondary_email = None
    phone_day = None
    phone_day_ext = None
    phone_evening = None
    phone_evening_ext = None
    phone_mobile = None
    phone_mobile_ext = None
    fax = None
    address_line_1 = None
    address_line_2 = None
    city = None
    state_province = None
    zip_postal_code = None
    country = None
    status_set_date = None
    creation_date = None
    last_change_date = None

    @classmethod
    def from_hps(cls, options):
        result = cls()
        result.company = options.company
        result.customer_identifier = options.customer_id
        result.customer_status = 'Inactive'
        if options.customer_status == HpsPayPlanCustomerStatus.active:
            result.customer_status = 'Active'
        result.department = options.department
        result.phone_day_ext = options.phone_day_ext
        result.phone_evening = options.phone_evening
        result.phone_evening_ext = options.phone_evening_ext
        result.phone_mobile = options.phone_mobile
        result.phone_mobile_ext = options.phone_mobile_ext
        result.secondary_email = options.secondary_email
        result.title = options.title

        return _PayPlanCustomer._hydrate_consumer_info(options, result)

    @staticmethod
    def _hydrate_consumer_info(options, dto):
        if options.address is not None:
            dto.address_line_1 = options.address.address
            dto.city = options.address.city
            dto.country = options.address.country
            dto.state_province = options.address.state
            dto.zip_postal_code = options.address.zip

        dto.primary_email = options.email
        dto.first_name = options.first_name
        dto.last_name = options.last_name
        dto.phone_day = options.phone

        return dto
