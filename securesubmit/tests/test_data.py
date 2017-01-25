import copy

from securesubmit.applepay.ecv1 import PaymentData
from securesubmit.entities.credit import HpsCardHolder, HpsCreditCard, HpsTrackData, HpsEncryptionData
from securesubmit.entities import HpsAddress
from securesubmit.entities.check import HpsCheck, HpsCheckHolder
from securesubmit.entities.gift import HpsGiftCard
from securesubmit.infrastructure.enums import CheckTypeType, AccountTypeType, SecCode, HpsTrackDataMethod
from securesubmit.services import HpsServicesConfig, HpsPayPlanServiceConfig


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

    # certification check
    certification = HpsCheck()
    certification.account_number = '24413815'
    certification.routing_number = '490000018'
    certification.check_type = CheckTypeType.personal
    certification.sec_code = SecCode.ppd
    certification.account_type = AccountTypeType.checking

    certification.check_holder = HpsCheckHolder()
    certification.check_holder.address = HpsAddress()
    certification.check_holder.address.address = '123 Main St.'
    certification.check_holder.address.city = 'Downtown'
    certification.check_holder.address.state = 'NJ'
    certification.check_holder.address.zip = '12345'
    certification.check_holder.dl_number = '09876543210'
    certification.check_holder.dl_state = 'TX'
    certification.check_holder.first_name = 'John'
    certification.check_holder.last_name = 'Doe'
    certification.check_holder.phone = '8003214567'
    certification.check_holder.dob_year = '1985'


class TestCreditCard(object):
    # valid visa
    valid_visa = HpsCreditCard()
    valid_visa.cvv = 123
    valid_visa.exp_month = 12
    valid_visa.exp_year = 2025
    valid_visa.number = "4012002000060016"

    # valid visa no cvv
    valid_visa_no_cvv = copy.deepcopy(valid_visa)
    valid_visa_no_cvv.cvv = None

    # valid visa track data
    valid_visa_track = HpsTrackData()
    valid_visa_track.method = HpsTrackDataMethod.swipe
    valid_visa_track.value = '%B4012001000000016^VI TEST CREDIT^251200000000000000000000?'
    valid_visa_track.value += ';4012001000000016=25120000000000000000?'

    # valid visa track data e3 v1
    valid_visa_track_e3v1 = HpsTrackData()
    valid_visa_track_e3v1.method = HpsTrackDataMethod.swipe
    valid_visa_track_e3v1.value = '<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|m3VpZL7Km3cqqty3xcIUJ+hKb1lwraqDBvnqQjZybcl95ywOAmdNTKTua|+++++++/q6S49jif|11;4012001000000016=25120000000000000000?|1dxxl54agM6av5oo3myo37RH4wo|+++++++/q6S49jif|00|||/wECAQECAoFGAgEH2wMBTDT6jRZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0AemN+EBuiWATgwIPfIVLybYKTlitSTmJYek5yD3nxtfsR0Rfd9UAaMTxDEGYeQDVmlgJICy8r0RE3QK5tgGCmWXF+GzMmAyB5h4o+jqbIluSs/MbKURSand61aTi5rRhbQSeBNjlvajCtZULmXXjpn6nuXI4QhN89sYwYm5tFwwA6yBN6fDDx8cH5I7MB6wn+AjVzrCCvV347WA2iujV0ZjTFDPT|>'
    valid_visa_track_e3v1.encryption_data = HpsEncryptionData()
    valid_visa_track_e3v1.encryption_data.version = '01'

    # valid visa track data e3 v2
    valid_visa_track_e3v2 = HpsTrackData()
    valid_visa_track_e3v2.method = HpsTrackDataMethod.swipe
    valid_visa_track_e3v2.value = '1dxxl54agM6av5oo3myo37RH4wo'
    valid_visa_track_e3v2.encryption_data = HpsEncryptionData()
    valid_visa_track_e3v2.encryption_data.version = '02'
    valid_visa_track_e3v2.encryption_data.encrypted_track_number = '2'
    valid_visa_track_e3v2.encryption_data.ktb = '/wECAQECAoFGAgEH2wMBTDT6jRZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0AemN+EBuiWATgwIPfIVLybYKTlitSTmJYek5yD3nxtfsR0Rfd9UAaMTxDEGYeQDVmlgJICy8r0RE3QK5tgGCmWXF+GzMmAyB5h4o+jqbIluSs/MbKURSand61aTi5rRhbQSeBNjlvajCtZULmXXjpn6nuXI4QhN89sYwYm5tFwwA6yBN6fDDx8cH5I7MB6wn+AjVzrCCvV347WA2iujV0ZjTFDPT'

    # valid visa proximity data
    valid_visa_proximity = HpsTrackData()
    valid_visa_proximity.method = HpsTrackDataMethod.proximity
    valid_visa_proximity.value = '%B4012001000000016^VI TEST CREDIT^251200000000000000000000?'
    valid_visa_proximity.value += ';4012001000000016=25120000000000000000?'

    # valid visa track data e3 v1
    valid_visa_proximity_e3v1 = HpsTrackData()
    valid_visa_proximity_e3v1.method = HpsTrackDataMethod.proximity
    valid_visa_proximity_e3v1.value = '<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|m3VpZL7Km3cqqty3xcIUJ+hKb1lwraqDBvnqQjZybcl95ywOAmdNTKTua|+++++++/q6S49jif|11;4012001000000016=25120000000000000000?|1dxxl54agM6av5oo3myo37RH4wo|+++++++/q6S49jif|00|||/wECAQECAoFGAgEH2wMBTDT6jRZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0AemN+EBuiWATgwIPfIVLybYKTlitSTmJYek5yD3nxtfsR0Rfd9UAaMTxDEGYeQDVmlgJICy8r0RE3QK5tgGCmWXF+GzMmAyB5h4o+jqbIluSs/MbKURSand61aTi5rRhbQSeBNjlvajCtZULmXXjpn6nuXI4QhN89sYwYm5tFwwA6yBN6fDDx8cH5I7MB6wn+AjVzrCCvV347WA2iujV0ZjTFDPT|>'
    valid_visa_proximity_e3v1.encryption_data = HpsEncryptionData()
    valid_visa_proximity_e3v1.encryption_data.version = '01'

    # valid visa track data e3 v2
    valid_visa_proximity_e3v2 = HpsTrackData()
    valid_visa_proximity_e3v2.method = HpsTrackDataMethod.proximity
    valid_visa_proximity_e3v2.value = '1dxxl54agM6av5oo3myo37RH4wo'
    valid_visa_proximity_e3v2.encryption_data = HpsEncryptionData()
    valid_visa_proximity_e3v2.encryption_data.version = '02'
    valid_visa_proximity_e3v2.encryption_data.encrypted_track_number = '2'
    valid_visa_proximity_e3v2.encryption_data.ktb = '/wECAQECAoFGAgEH2wMBTDT6jRZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0AemN+EBuiWATgwIPfIVLybYKTlitSTmJYek5yD3nxtfsR0Rfd9UAaMTxDEGYeQDVmlgJICy8r0RE3QK5tgGCmWXF+GzMmAyB5h4o+jqbIluSs/MbKURSand61aTi5rRhbQSeBNjlvajCtZULmXXjpn6nuXI4QhN89sYwYm5tFwwA6yBN6fDDx8cH5I7MB6wn+AjVzrCCvV347WA2iujV0ZjTFDPT'

    # valid mastercard
    valid_mastercard = HpsCreditCard()
    valid_mastercard.cvv = 123
    valid_mastercard.exp_month = 12
    valid_mastercard.exp_year = 2025
    valid_mastercard.number = "5473500000000014"

    # valid mastercard no cvv
    valid_mastercard_no_cvv = copy.deepcopy(valid_mastercard)
    valid_mastercard_no_cvv.cvv = None

    # valid discover card
    valid_discover = HpsCreditCard()
    valid_discover.cvv = 123
    valid_discover.exp_month = 12
    valid_discover.exp_year = 2025
    valid_discover.number = "6011000990156527"

    # valid discover no cvv
    valid_discover_no_cvv = copy.deepcopy(valid_discover)
    valid_discover_no_cvv.cvv = None

    # valid amex
    valid_amex = HpsCreditCard()
    valid_amex.cvv = 1234
    valid_amex.exp_month = 12
    valid_amex.exp_year = 2025
    valid_amex.number = "372700699251018"

    # valid amex no cvv
    valid_amex_no_cvv = copy.deepcopy(valid_amex)
    valid_amex_no_cvv.cvv = None

    # valid jcb
    valid_jcb = HpsCreditCard()
    valid_jcb.cvv = 123
    valid_jcb.exp_month = 12
    valid_jcb.exp_year = 2025
    valid_jcb.number = "3566007770007321"

    # valid jcb no cvv
    valid_jcb_no_cvv = copy.deepcopy(valid_jcb)
    valid_jcb_no_cvv.cvv = None

    # invalid card
    invalid_card = HpsCreditCard()
    invalid_card.cvv = 123
    invalid_card.exp_month = 12
    invalid_card.exp_year = 2025
    invalid_card.number = "12345"


class TestGiftCard(object):
    # valid gift card
    valid_gift_card_manual = HpsGiftCard()
    valid_gift_card_manual.card_number = "5022440000000000098"
    valid_gift_card_manual.exp_month = 12
    valid_gift_card_manual.exp_year = 39

    # another valid gift card
    valid_gift_card_manual_2 = HpsGiftCard()
    valid_gift_card_manual_2.card_number = "5022440000000000007"
    valid_gift_card_manual_2.exp_month = 12
    valid_gift_card_manual_2.exp_year = 39

    # invalid gift card
    invalid_gift_card_manual = HpsGiftCard()
    invalid_gift_card_manual.card_number = "1234"
    invalid_gift_card_manual.exp_month = 12
    invalid_gift_card_manual.exp_year = 39


class TestServicesConfig(object):
    _service_uri = ('https://cert.api2.heartlandportico.com'
                    '/Hps.Exchange.PosGateway'
                    '/PosGatewayService.asmx?wsdl')

    valid_services_config = HpsServicesConfig()
    valid_services_config.credential_token = 'pkapi_cert_P6dRqs1LzfWJ6HgGVZ'
    valid_services_config.secret_api_key = 'skapi_cert_MYl2AQAowiQAbLp5JesGKh7QFkcizOP2jcX9BrEMqQ'
    valid_services_config.service_uri = _service_uri

    valid_e_gold_config = HpsServicesConfig()
    valid_e_gold_config.site_id = '95881'
    valid_e_gold_config.license_id = '95878'
    valid_e_gold_config.device_id = '90911485'
    valid_e_gold_config.username = '777700778679'
    valid_e_gold_config.password = '$Test1234'
    valid_e_gold_config.service_uri = _service_uri

    valid_pay_plan_config = HpsPayPlanServiceConfig()
    # valid_pay_plan_config.secret_api_key = 'skapi_uat_MY5OAAAUrmIFvLDRpO_ufLlFQkgg0Rms2G8WoI1THQ'
    valid_pay_plan_config.secret_api_key = 'skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A'


class TestData(object):
    PAYMENT_TOKEN_MC_3DS_JSON = ("{\n" +
            "    \"data\": \"XXXXXXXXXXAs10FfwmMthvxrp4BB0MudUwk/xrYkerm0zrkK24ICMDL3a6pyz9uC3bTyvuTSk4S0fbewBBWIwVeCXbr8qD6DRkUe8od77LgY0gdK4P0PvIvEzrOHe0eH9/UZ32RijNaQ+1xt+Y0lJ53NAUzuymynO4kFHXTdUTKWOl6qxYhI3sckpLot6108AYy4EDEaG+Y2iENjzIHYlI6t/mOgYUn7EZAYM1148UhxVKpdAkDBna3BL/GLFxP7vT3CoW87zjscUCEbbqbTMZPkcJa2B21kbDABItQjI9gYlkJjprd3ltx3r2reO8Ea8UtEVCOM6Tg4D4L3H/KXUZiLLeFTK+BUksPbdjQVgOBI14rjfNKgenujUmPxetI5B9XPMaNcBErKdw==\",\n" +
            "    \"header\": {\n" +
            "        \"ephemeralPublicKey\": \"XXXXXXXXXXZIzj0CAQYIKoZIzj0DAQcDQgAElJ0FU66tKNvnBqvkykrTsVw37gw1kRW2jLd4N4jqvqGuHB+KaiWcrMKEI5SI0AKTgR6zIEnYahZmOd4ScZHqOQ==\",\n" +
            "        \"publicKeyHash\": \"XXXXXXXXXX/t54x445nFoX8BcHVeenIHikQRURYqjuY=\",\n" +
            "        \"transactionId\": \"XXXXXXXXXX561c4b4c1c5d2c4de38b124f01a67bbe3ab8910b91a8991c293c71\"\n" +
            "    },\n" +
            "    \"signature\": \"XXXXXXXXXXb3DQEHAqCAMIACAQExDzANBglghkgBZQMEAgEFADCABgkqhkiG9w0BBwEAAKCAMIID4jCCA4igAwIBAgIIJEPyqAad9XcwCgYIKoZIzj0EAwIwejEuMCwGA1UEAwwlQXBwbGUgQXBwbGljYXRpb24gSW50ZWdyYXRpb24gQ0EgLSBHMzEmMCQGA1UECwwdQXBwbGUgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkxEzARBgNVBAoMCkFwcGxlIEluYy4xCzAJBgNVBAYTAlVTMB4XDTE0MDkyNTIyMDYxMVoXDTE5MDkyNDIyMDYxMVowXzElMCMGA1UEAwwcZWNjLXNtcC1icm9rZXItc2lnbl9VQzQtUFJPRDEUMBIGA1UECwwLaU9TIFN5c3RlbXMxEzARBgNVBAoMCkFwcGxlIEluYy4xCzAJBgNVBAYTAlVTMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwhV37evWx7Ihj2jdcJChIY3HsL1vLCg9hGCV2Ur0pUEbg0IO2BHzQH6DMx8cVMP36zIg1rrV1O/0komJPnwPE6OCAhEwggINMEUGCCsGAQUFBwEBBDkwNzA1BggrBgEFBQcwAYYpaHR0cDovL29jc3AuYXBwbGUuY29tL29jc3AwNC1hcHBsZWFpY2EzMDEwHQYDVR0OBBYEFJRX22/VdIGGiYl2L35XhQfnm1gkMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUI/JJxE+T5O8n5sT2KGw/orv9LkswggEdBgNVHSAEggEUMIIBEDCCAQwGCSqGSIb3Y2QFATCB/jCBwwYIKwYBBQUHAgIwgbYMgbNSZWxpYW5jZSBvbiB0aGlzIGNlcnRpZmljYXRlIGJ5IGFueSBwYXJ0eSBhc3N1bWVzIGFjY2VwdGFuY2Ugb2YgdGhlIHRoZW4gYXBwbGljYWJsZSBzdGFuZGFyZCB0ZXJtcyBhbmQgY29uZGl0aW9ucyBvZiB1c2UsIGNlcnRpZmljYXRlIHBvbGljeSBhbmQgY2VydGlmaWNhdGlvbiBwcmFjdGljZSBzdGF0ZW1lbnRzLjA2BggrBgEFBQcCARYqaHR0cDovL3d3dy5hcHBsZS5jb20vY2VydGlmaWNhdGVhdXRob3JpdHkvMDQGA1UdHwQtMCswKaAnoCWGI2h0dHA6Ly9jcmwuYXBwbGUuY29tL2FwcGxlYWljYTMuY3JsMA4GA1UdDwEB/wQEAwIHgDAPBgkqhkiG92NkBh0EAgUAMAoGCCqGSM49BAMCA0gAMEUCIHKKnw+Soyq5mXQr1V62c0BXKpaHodYu9TWXEPUWPpbpAiEAkTecfW6+W5l0r0ADfzTCPq2YtbS39w01XIayqBNy8bEwggLuMIICdaADAgECAghJbS+/OpjalzAKBggqhkjOPQQDAjBnMRswGQYDVQQDDBJBcHBsZSBSb290IENBIC0gRzMxJjAkBgNVBAsMHUFwcGxlIENlcnRpZmljYXRpb24gQXV0aG9yaXR5MRMwEQYDVQQKDApBcHBsZSBJbmMuMQswCQYDVQQGEwJVUzAeFw0xNDA1MDYyMzQ2MzBaFw0yOTA1MDYyMzQ2MzBaMHoxLjAsBgNVBAMMJUFwcGxlIEFwcGxpY2F0aW9uIEludGVncmF0aW9uIENBIC0gRzMxJjAkBgNVBAsMHUFwcGxlIENlcnRpZmljYXRpb24gQXV0aG9yaXR5MRMwEQYDVQQKDApBcHBsZSBJbmMuMQswCQYDVQQGEwJVUzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABPAXEYQZ12SF1RpeJYEHduiAou/ee65N4I38S5PhM1bVZls1riLQl3YNIk57ugj9dhfOiMt2u2ZwvsjoKYT/VEWjgfcwgfQwRgYIKwYBBQUHAQEEOjA4MDYGCCsGAQUFBzABhipodHRwOi8vb2NzcC5hcHBsZS5jb20vb2NzcDA0LWFwcGxlcm9vdGNhZzMwHQYDVR0OBBYEFCPyScRPk+TvJ+bE9ihsP6K7/S5LMA8GA1UdEwEB/wQFMAMBAf8wHwYDVR0jBBgwFoAUu7DeoVgziJqkipnevr3rr9rLJKswNwYDVR0fBDAwLjAsoCqgKIYmaHR0cDovL2NybC5hcHBsZS5jb20vYXBwbGVyb290Y2FnMy5jcmwwDgYDVR0PAQH/BAQDAgEGMBAGCiqGSIb3Y2QGAg4EAgUAMAoGCCqGSM49BAMCA2cAMGQCMDrPcoNRFpmxhvs1w1bKYr/0F+3ZD3VNoo6+8ZyBXkK3ifiY95tZn5jVQQ2PnenC/gIwMi3VRCGwowV3bF3zODuQZ/0XfCwhbZZPxnJpghJvVPh6fRuZy5sJiSFhBpkPCZIdAAAxggFeMIIBWgIBATCBhjB6MS4wLAYDVQQDDCVBcHBsZSBBcHBsaWNhdGlvbiBJbnRlZ3JhdGlvbiBDQSAtIEczMSYwJAYDVQQLDB1BcHBsZSBDZXJ0aWZpY2F0aW9uIEF1dGhvcml0eTETMBEGA1UECgwKQXBwbGUgSW5jLjELMAkGA1UEBhMCVVMCCCRD8qgGnfV3MA0GCWCGSAFlAwQCAQUAoGkwGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHATAcBgkqhkiG9w0BCQUxDxcNMTQxMTE0MDQzMzUzWjAvBgkqhkiG9w0BCQQxIgQgN0R4zqz8uzwHg7F3dtXRSk21uTT0+N1tYTQ6pgp6JTowCgYIKoZIzj0EAwIERjBEAiBkKFNsb70s38ZpQxoYnWGlsKd+4zDLVhJBmlf7//EreQIgRm86eZk1wl+wMAadVXkJvpcikq3sAXHUN8GUzhtYF10AAAAAAAA=\",\n" +
            "    \"version\": \"EC_v1\"\n" +
            "}")

    PAYMENT_DATA_VISA_DECRYPTED_JSON = ("{\n" +
            "    \"applicationExpirationDate\": \"200228\",\n" +
            "    \"applicationPrimaryAccountNumber\": \"4111111111111111\",\n" +
            "    \"currencyCode\": \"840\",\n" +
            "    \"deviceManufacturerIdentifier\": \"040010030273\",\n" +
            "    \"paymentData\": {\n" +
            "        \"eciIndicator\": \"5\",\n" +
            "        \"onlinePaymentCryptogram\": \"XXXXf98AAajXbDRg3HSUMAACAAA=\"\n" +
            "    },\n" +
            "    \"paymentDataType\": \"3DSecure\",\n" +
            "    \"transactionAmount\": 100\n" +
            "}\n")

    PAYMENT_DATA_AMEX_DECRYPTED_JSON = ("{\n" +
            "    \"applicationExpirationDate\": \"190228\",\n" +
            "    \"applicationPrimaryAccountNumber\": \"372700699251018\",\n" +
            "    \"currencyCode\": \"840\",\n" +
            "    \"deviceManufacturerIdentifier\": \"030010030273\",\n" +
            "    \"paymentData\": {\n" +
            "        \"onlinePaymentCryptogram\": \"XXXXXXXXUImjWgXRSUccwAACgAAGhgEDoLABAAhAgAABAAAABJ0vEw==\"\n" +
            "    },\n" +
            "    \"paymentDataType\": \"3DSecure\",\n" +
            "    \"transactionAmount\": 100\n" +
            "}\n")

    PAYMENT_DATA_MC_DECRYPTED_JSON = ("{\n" +
            "    \"applicationExpirationDate\": \"171130\",\n" +
            "    \"applicationPrimaryAccountNumber\": \"5473500000000014\",\n" +
            "    \"currencyCode\": \"840\",\n" +
            "    \"deviceManufacturerIdentifier\": \"050110030273\",\n" +
            "    \"paymentData\": {\n" +
            "        \"onlinePaymentCryptogram\": \"XXXXbKK+J9Z5AAWj9GzwAoABFA==\"\n" +
            "    },\n" +
            "    \"paymentDataType\": \"3DSecure\",\n" +
            "    \"transactionAmount\": 1\n" +
            "}\n")

    @staticmethod
    def visa_payment_data():
        return PaymentData(TestData.PAYMENT_DATA_VISA_DECRYPTED_JSON)

    @staticmethod
    def amex_payment_data():
        return PaymentData(TestData.PAYMENT_DATA_AMEX_DECRYPTED_JSON)

    @staticmethod
    def mc_payment_data():
        return PaymentData(TestData.PAYMENT_DATA_MC_DECRYPTED_JSON)
