import traceback
import re
import os
import web
from securesubmit.services import HpsServicesConfig
from securesubmit.services.gateway import (
    HpsCreditService,
    HpsAddress,
    HpsCardHolder,
    HpsCreditException,
    HpsGatewayException
)

urls = (
    '/', 'Index',
    '/charge', 'Charge'
)
# include this to allow for sending emails
# web.config.smtp_server = ''

application = web.application(urls, globals())

template_dir = os.path.abspath(os.path.dirname(__file__)) + '/templates'
renderer = web.template.render(template_dir)


class Index:
    def GET(self):
        return renderer.index()


class Charge:
    _config = HpsServicesConfig()
    _config.secret_api_key = 'skapi_cert_MYl2AQAowiQAbLp5JesGKh7QFkcizOP2jcX9BrEMqQ'
    _config.version_number = '0000'
    _config.developer_id = '000000'

    _charge_service = HpsCreditService(_config)

    def POST(self):
        request = web.input()
        try:
            email = request['Email']

            address = HpsAddress()
            address.address = request['Address']
            address.city = request['City']
            address.state = request['State']
            address.zip = re.sub('[^0-9]', '', request['Zip'])
            address.country = 'United States'

            card_holder = HpsCardHolder()
            card_holder.first_name = request['FirstName']
            card_holder.last_name = request['LastName']
            card_holder.address = address
            card_holder.phone = re.sub('[^0-9]', '', request['PhoneNumber'])

            su_token = request['token_value']
            response = self.charge_token(su_token, card_holder)
        except KeyError:
            traceback.print_exc()
            raise web.seeother('/')
        except (HpsCreditException, HpsGatewayException):
            traceback.print_exc()
            raise web.seeother('/')
        else:
            body = '<h1>Success!</h1><p>Thank you, %s, for your order of $15.15.</p>' % card_holder.first_name
            print 'Transaction Id: %s' % response.transaction_id
            self.send_email(email, 'donotreply@e-hps.com', 'Successful Charge!', body)
            raise web.seeother('/')

    def charge_token(self, token, card_holder):
        response = self._charge_service.charge(
            15.15,
            'usd',
            token,
            card_holder)
        return response

    def send_email(self, to, from_email, subject, body):
        """ Make sure to set the web.config.smtp_server option to send mail """
        message = '<html><body>%s</body?</html>' % body
        headers = ({
            'From': from_email,
            'Reply-To': from_email,
            'MIME-Version': '1.0',
            'Content-type': 'text/html; charset=ISO-8859-1'
        })
        web.sendmail(from_email, to, subject, message, headers=headers)


if __name__ == '__main__':
    application.run()

