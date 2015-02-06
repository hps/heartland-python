import re
import traceback
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from securesubmit.services import HpsServicesConfig
from securesubmit.services.gateway import (
    HpsCreditService,
    HpsAddress,
    HpsCardHolder,
    HpsCreditException,
    HpsGatewayException
)


def index(request):
    return render(request, 'ssexample/index.html')


def charge(request):
    try:
        email = request.POST['Email']

        address = HpsAddress()
        address.address = request.POST['Address']
        address.city = request.POST['City']
        address.state = request.POST['State']
        address.zip = re.sub('[^0-9]', '', request.POST['Zip'])
        address.country = 'United States'

        card_holder = HpsCardHolder()
        card_holder.first_name = request.POST['FirstName']
        card_holder.last_name = request.POST['LastName']
        card_holder.address = address
        card_holder.phone = re.sub('[^0-9]', '', request.POST['PhoneNumber'])

        su_token = request.POST['token_value']
        response = charge_token(su_token, card_holder)
    except KeyError:
        traceback.print_exc()
        return HttpResponseRedirect(reverse('ssexample:index'))
    except (HpsCreditException, HpsGatewayException):
        traceback.print_exc()
        return HttpResponseRedirect(reverse('ssexample:index'))
    else:
        body = 'Success!\r\nThank you, %s, for your order of $15.15.' % card_holder.first_name
        print 'Transaction Id: %s' % response.transaction_id
        send_email(email, 'donotreply@e-hps.com', 'Successful Charge!', body)
        return HttpResponseRedirect(reverse('ssexample:index'))


def charge_token(token, card_holder):
    config = HpsServicesConfig()
    config.secret_api_key = 'skapi_cert_MYl2AQAowiQAbLp5JesGKh7QFkcizOP2jcX9BrEMqQ'
    config.version_number = '0000'
    config.developer_id = '000000'

    charge_service = HpsCreditService(config)
    response = charge_service.charge(
        15.15,
        'usd',
        token,
        card_holder)
    return response


def send_email(to, from_email, subject, body):
    """
    You will need to set the EMAIL_HOST & EMAIL_PORT
    in the settings.py file for email to work.
    """
    send_mail(subject, body, from_email, [to], True)
