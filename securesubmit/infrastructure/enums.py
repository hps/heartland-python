"""
    infrastructure.enums.py

    enumerations

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from enum import Enum, IntEnum


class CheckActionType(Enum):
    SALE = 'SALE'
    OVERRIDE = 'OVERRIDE'
    RETURN = 'RETURN'

    def __str__(self):
        return str(self.value)


class AccountTypeType(Enum):
    checking = 'CHECKING'
    savings = 'SAVINGS'

    def __str__(self):
        return str(self.value)


class DataEntryModeType(Enum):
    manual = 'MANUAL'
    swipe = 'SWIPE'

    def __str__(self):
        return str(self.value)


class CheckTypeType(Enum):
    personal = 'PERSONAL'
    business = 'BUSINESS'
    payroll = 'PAYROLL'

    def __str__(self):
        return str(self.value)


class HpsTransactionType(IntEnum):
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

    def __str__(self):
        return str(self.value)


class HpsExceptionCodes(IntEnum):
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

    def __str__(self):
        return str(self.value)


class SecCode(Enum):
    ppd = 'PPD'
    ccd = 'CCD'
    pop = 'POP'
    web = 'WEB'
    tel = 'TEL'
    e_bronze = 'eBronze'

    def __str__(self):
        return str(self.value)


class EncodingType(Enum):
    base16 = 'base16'
    base64 = 'base64'

    def __str__(self):
        return str(self.value)


class TypeOfPaymentDataType(Enum):
    secure_3d = '3DSecure'

    def __str__(self):
        return str(self.value)


class HpsPayPlanAccountType(Enum):
    BUSINESS = 'Business'
    PERSONAL = 'Personal'

    def __str__(self):
        return str(self.value)


class HpsPayPlanCustomerStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

    def __str__(self):
        return str(self.value)


class HpsPayPlanPaymentMethodStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    INVALID = 'Invalid'
    REVOKED = 'Revoked'
    EXPIRED = 'Expired'
    LOST_STOLEN = 'Lost/Stolen'

    def __str__(self):
        return str(self.value)


class HpsPayPlanPaymentMethodType(Enum):
    ACH = 'ACH'
    CREDIT_CARD = 'Credit Card'

    def __str__(self):
        return str(self.value)


class HpsPayPlanScheduleDuration(Enum):
    ONGOING = 'Ongoing'
    END_DATE = 'End Date'
    LIMITED_NUMBER = 'Limited Number'

    def __str__(self):
        return str(self.value)


class HpsPayPlanScheduleFrequency(Enum):
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Bi-Weekly'
    SEMIMONTHLY = 'Semi-Monthly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANNUALLY = 'Semi-Annually'
    ANNUALLY = 'Annually'

    def __str__(self):
        return str(self.value)


class HpsPayPlanScheduleStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    FAILED = 'FAILED'

    def __str__(self):
        return str(self.value)


class HpsTrackDataMethod(Enum):
    swipe = 'swipe'
    proximity = 'proximity'

    def __str__(self):
        return str(self.value)


class HpsAdditionalAmountType(Enum):
    health_care_total = '4S'
    prescription_subtotal = '4U'
    vision_optical_subtotal = '4V'
    clinic_or_qualified_medical_subtotal = '4W'
    dental_subtotal = '4X'

    def __str__(self):
        return str(self.value)


class HpsTokenMappingType(Enum):
    UNIQUE = 'UNIQUE'
    CONSTANT = 'CONSTANT'

    def __str__(self):
        return str(self.value)


class PaymentDataSource(Enum):
    APPLE_PAY = 'ApplePay'

    def __str__(self):
        return str(self.value)