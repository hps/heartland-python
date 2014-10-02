import copy
from securesubmit.entities.credit import HpsCardHolder, HpsCreditCard
from securesubmit.entities import HpsAddress
from securesubmit.entities.check import HpsCheck, HpsCheckHolder
from securesubmit.entities.gift import HpsGiftCard
from securesubmit.infrastructure.enums import CheckTypeType, AccountTypeType
from securesubmit.services import HpsServicesConfig


class TestCardHolder(object):
    # heartland's address
    _heartland_address = HpsAddress()
    _heartland_address.address = 'One Heartland Way'
    _heartland_address.city = 'Jeffersonville'
    _heartland_address.state = 'IN'
    _heartland_address.zip = '47130'
    _heartland_address.country = 'United States'

    # cert address
    _cert_address = HpsAddress()
    _cert_address.address = '6860 Dallas Pkwy'
    _cert_address.city = 'Irvine'
    _cert_address.state = 'TX'
    _cert_address.zip = '750241234'
    _cert_address.country = 'United States'

    # base card holder
    _card_holder = HpsCardHolder()
    _card_holder.first_name = 'Bill'
    _card_holder.last_name = 'Johnson'
    _card_holder.address = _cert_address

    # valid card holder
    valid_card_holder = copy.deepcopy(_card_holder)
    valid_card_holder.address = _heartland_address

    # certification card holder - short zip
    cert_holder_short_zip = copy.deepcopy(_card_holder)
    cert_holder_short_zip.address.zip = '75024'

    # certification card holder - short zip, no street
    cert_holder_short_zip_no_street = copy.deepcopy(_card_holder)
    cert_holder_short_zip_no_street.address.address = '6860'
    cert_holder_short_zip_no_street.address.zip = '75024'

    # certification card holder - long zip
    cert_holder_long_zip = copy.deepcopy(_card_holder)

    # certification card holder - long zip, no street
    cert_holder_long_zip_no_street = copy.deepcopy(_card_holder)
    cert_holder_long_zip_no_street.address.address = '6860'


class TestCheck(object):
    # check holder
    _check_holder = HpsCheckHolder()
    _check_holder.address = HpsAddress()
    _check_holder.address.address = '6860 Dallas Parkway'
    _check_holder.address.city = 'Plano'
    _check_holder.address.state = 'TX'
    _check_holder.address.zip = '75024'
    _check_holder.dl_number = '1234567'
    _check_holder.dl_state = 'TX'
    _check_holder.first_name = 'John'
    _check_holder.last_name = 'Doe'
    _check_holder.phone = '1234567890'

    # good check
    approve = HpsCheck()
    approve.account_number = '24413815'
    approve.routing_number = '490000018'
    approve.check_type = CheckTypeType.personal
    approve.sec_code = 'PPD'
    approve.account_type = AccountTypeType.checking
    approve.check_holder = copy.deepcopy(_check_holder)

    # check w/ invalid check holder
    invalid_check_holder = copy.deepcopy(approve)
    invalid_check_holder.check_holder.dl_number = ''
    invalid_check_holder.check_holder.dl_state = ''
    invalid_check_holder.check_holder.phone = ''

    # bad check
    decline = copy.deepcopy(approve)
    decline.routing_number = '490000034'


class TestCreditCard(object):
    # valid visa
    valid_visa = HpsCreditCard()
    valid_visa.cvv = 123
    valid_visa.exp_month = 12
    valid_visa.exp_year = 2015
    valid_visa.number = "4012002000060016"

    # valid visa no cvv
    valid_visa_no_cvv = copy.deepcopy(valid_visa)
    valid_visa_no_cvv.cvv = None

    # valid mastercard
    valid_mastercard = HpsCreditCard()
    valid_mastercard.cvv = 123
    valid_mastercard.exp_month = 12
    valid_mastercard.exp_year = 2015
    valid_mastercard.number = "5473500000000014"

    # valid mastercard no cvv
    valid_mastercard_no_cvv = copy.deepcopy(valid_mastercard)
    valid_mastercard_no_cvv.cvv = None

    # valid discover card
    valid_discover = HpsCreditCard()
    valid_discover.cvv = 123
    valid_discover.exp_month = 12
    valid_discover.exp_year = 2015
    valid_discover.number = "6011000990156527"

    # valid discover no cvv
    valid_discover_no_cvv = copy.deepcopy(valid_discover)
    valid_discover_no_cvv.cvv = None

    # valid amex
    valid_amex = HpsCreditCard()
    valid_amex.cvv = 1234
    valid_amex.exp_month = 12
    valid_amex.exp_year = 2015
    valid_amex.number = "372700699251018"

    # valid amex no cvv
    valid_amex_no_cvv = copy.deepcopy(valid_amex)
    valid_amex_no_cvv.cvv = None

    # valid jcb
    valid_jcb = HpsCreditCard()
    valid_jcb.cvv = 123
    valid_jcb.exp_month = 12
    valid_jcb.exp_year = 2015
    valid_jcb.number = "3566007770007321"

    # valid jcb no cvv
    valid_jcb_no_cvv = copy.deepcopy(valid_jcb)
    valid_jcb_no_cvv.cvv = None

    # invalid card
    invalid_card = HpsCreditCard()
    invalid_card.cvv = 123
    invalid_card.exp_month = 12
    invalid_card.exp_year = 2015
    invalid_card.number = "12345"


class TestGiftCard(object):
    # valid gift card
    valid_gift_card_manual = HpsGiftCard()
    valid_gift_card_manual.number = "5022440000000000098"
    valid_gift_card_manual.exp_month = 12
    valid_gift_card_manual.exp_year = 39

    # another valid gift card
    valid_gift_card_manual_2 = HpsGiftCard()
    valid_gift_card_manual_2.number = "5022440000000000007"
    valid_gift_card_manual_2.exp_month = 12
    valid_gift_card_manual_2.exp_year = 39

    # invalid gift card
    invalid_gift_card_manual = HpsGiftCard()
    invalid_gift_card_manual.number = "1234"
    invalid_gift_card_manual.exp_month = 12
    invalid_gift_card_manual.exp_year = 39


class TestServicesConfig(object):
    _service_uri = ('https://posgateway.cert.secureexchange.net'
                    '/Hps.Exchange.PosGateway'
                    '/PosGatewayService.asmx?wsdl')

    valid_services_config = HpsServicesConfig()
    valid_services_config.credential_token = 'pkapi_cert_P6dRqs1LzfWJ6HgGVZ'
    valid_services_config.secret_api_key = \
        'skapi_cert_MYl2AQAowiQAbLp5JesGKh7QFkcizOP2jcX9BrEMqQ'
    valid_services_config.service_uri = _service_uri
