"""
    infrastructure.enums.py

    enumerations

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from enum import Enum


class CheckActionType(Enum):
    SALE = 'SALE'
    OVERRIDE = 'OVERRIDE'
    RETURN = 'RETURN'


class AccountTypeType(Enum):
    checking = 'CHECKING'
    savings = 'SAVINGS'


class DataEntryModeType(Enum):
    manual = 'MANUAL'
    swipe = 'SWIPE'


class CheckTypeType(Enum):
    personal = 'PERSONAL'
    business = 'BUSINESS'
    payroll = 'PAYROLL'


class HpsTransactionType(Enum):
    Authorize = 1
    Capture = 2
    Charge = 3
    Refund = 4
    Reverse = 5
    Verify = 6
    List = 7
    Get = 8
    Void = 9
    SecurityError = 10
    BatchClose = 11


class HpsGiftCardAliasAction(Enum):
    delete = 'DELETE'
    add = 'ADD'
    create = 'CREATE'


class HpsExceptionCodes(Enum):
    # general codes
    authentication_error = 0,
    invalid_configuration = 1

    # input codes
    invalid_amount = 2
    missing_currency = 3
    invalid_currency = 4
    invalid_date = 5
    missing_check_name = 27

    # gateway codes
    unknown_gateway_error = 6
    invalid_original_transaction = 7
    no_open_batch = 8
    invalid_cpc_data = 9
    invalid_card_data = 10
    invalid_number = 11
    gateway_timeout = 12
    unexpected_gateway_response = 13
    gateway_timeout_reversal_error = 14

    # credit issuer codes
    incorrect_number = 15
    expired_card = 16
    invalid_pin = 17
    pin_entries_exceeded = 18
    invalid_expiry = 19
    pin_verification = 20
    issuer_timeout = 21
    incorrect_cvc = 22
    card_declined = 23
    processing_error = 24
    issuer_timeout_reversal_error = 25
    unknown_credit_error = 26


class HpsTaxType(Enum):
    not_used = 'NOTUSED'
    sales_tax = 'SALESTAX'
    tax_exempt = 'TAXEXEMPT'


class SecCode(Enum):
    ppd = 'PPD'
    ccd = 'CCD'
    pop = 'POP'
    web = 'WEB'
    tel = 'TEL'
    e_bronze = 'eBronze'


class EncodingType(Enum):
    base16 = 'base16'
    base64 = 'base64'


class TypeOfPaymentDataType(Enum):
    secure_3d = '3DSecure'


class HpsPayPlanAccountType(Enum):
    BUSINESS = 'Business'
    PERSONAL = 'Personal'


class HpsPayPlanCustomerStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class HpsPayPlanPaymentMethodStatus(HpsPayPlanCustomerStatus):
    INVALID = 'Invalid'
    REVOKED = 'Revoked'
    EXPIRED = 'Expired'
    LOST_STOLEN = 'Lost/Stolen'


class HpsPayPlanPaymentMethodType(Enum):
    ACH = 'ACH'
    CREDIT_CARD = 'Credit Card'


class HpsPayPlanScheduleDuration(Enum):
    ONGOING = 'Ongoing'
    END_DATE = 'End Date'
    LIMITED_NUMBER = 'Limited Number'


class HpsPayPlanScheduleFrequency(Enum):
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Bi-Weekly'
    SEMIMONTHLY = 'Semi-Monthly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANNUALLY = 'Semi-Annually'
    ANNUALLY = 'Annually'


class HpsPayPlanScheduleStatus(HpsPayPlanCustomerStatus):
    FAILED = 'FAILED'


class HpsTrackDataMethod(Enum):
    swipe = 'swipe'
    proximity = 'proximity'


class HpsAdditionalAmountType(Enum):
    health_care_total = '4S'
    prescription_subtotal = '4U'
    vision_optical_subtotal = '4V'
    clinic_or_qualified_medical_subtotal = '4W'
    dental_subtotal = '4X'


class HpsTokenMappingType(Enum):
    UNIQUE = 'UNIQUE'
    CONSTANT = 'CONSTANT'