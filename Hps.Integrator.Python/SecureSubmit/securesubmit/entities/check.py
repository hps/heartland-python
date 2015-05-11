"""
    check.py

    This module defines the check entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""

from securesubmit.entities import HpsConsumer, HpsTransaction


class HpsCheck(object):
    routing_number = None
    account_number = None
    check_number = None
    micr_number = None

    """Account Type: Checking, Savings.
       NOTE: If processing with Colonnade,
       Account Type must be specified."""
    account_type = None

    """Data Entry Mode indicating whether
       the check data was manually entered
       or obtained from a check reader."""
    data_entry_mode = None
    check_type = None

    """Indicates check verify. Requires
       processor setup to utilize. Please
       contact your HPS representative for
       more information on the GETI eBronze
       program."""
    check_verify = False

    """NACHA Standard Entry Class Code.
       NOTE: If processing with Colonnade,
       SECCode is required for Check Sale
       transactions."""
    sec_code = None
    check_holder = None


class HpsCheckHolder(HpsConsumer):
    check_name = None
    dl_state = None
    dl_number = None
    ssnl4 = None
    dob_year = None
    courtesy_card = None


class HpsCheckResponse(HpsTransaction):
    authorization_code = None
    customer_id = None
    details = None

    @classmethod
    def from_dict(cls, rsp):
        response = rsp['Transaction'].itervalues().next()

        sale = super(HpsCheckResponse, cls).from_dict(rsp)
        if 'RspCode' in response:
            sale.response_code = str(response['RspCode'])

        if 'RspMessage' in response:
            sale.response_text = response['RspMessage']

        if 'AuthCode' in response:
            sale.authorization_code = response['AuthCode']

        def _hydrate_rsp_details(check_info):
            details = HpsCheckResponseDetails()
            if 'Type' in check_info:
                details.message_type = check_info['Type']

            if 'Code' in check_info:
                details.code = check_info['Code']

            if 'Message' in check_info:
                details.message = check_info['Message']

            if 'FieldNumber' in check_info:
                details.field_number = check_info['FieldNumber']

            if 'FieldName' in check_info:
                details.field_name = check_info['FieldName']

            return details

        if ('CheckRspInfo' in response and
                len(response['CheckRspInfo']) > 0):
            sale.details = []
            if isinstance(response['CheckRspInfo'], list):
                for details in response['CheckRspInfo']:
                    sale.details.append(_hydrate_rsp_details(details))
            else:
                sale.details.append(
                    _hydrate_rsp_details(response['CheckRspInfo']))

        return sale


class HpsCheckResponseDetails(object):
    message_type = None
    code = None
    message = None
    field_number = None
    field_name = None
