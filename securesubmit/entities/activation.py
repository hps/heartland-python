class DeviceActivationKeyResponse(object):
    merchant_id = None
    activation_code = None,
    secret_api_key = None

    @classmethod
    def from_dict(cls, rsp):
        response = cls()
        response.merchant_id = None if 'merchantId' not in rsp else rsp['merchantId']
        response.activation_code = None if 'activationCode' not in rsp else rsp['activationCode']
        response.secret_api_key = None if 'apiKey' not in rsp else rsp['apiKey']

        return response