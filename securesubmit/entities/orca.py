class OrcaServiceResource(object):
    def get_json_data(self):
        fields = dict()

        for k in self.__dict__.keys():
            value = self.__getattribute__(k)
            if value is not None:
                fields[self.to_camel_case(k)] = value

        return fields

    @staticmethod
    def get_editable_fields():
        pass

    @staticmethod
    def to_camel_case(name):
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])


class DeviceActivationRequest(OrcaServiceResource):
    merchant_id = None
    device_id = None
    email = None
    application_id = None
    hardware_type_name = None
    software_version = None
    configuration_name = None
    peripheral_name = None
    peripheral_software = None


class DeviceActivationResponse(DeviceActivationRequest):
    activation_code = None

    @classmethod
    def from_dict(cls, rsp):
        response = cls()
        response.merchant_id = None if 'merchantId' not in rsp else rsp['merchantId']
        response.device_id = None if 'deviceId' not in rsp else rsp['deviceId']
        response.email = None if 'emailId' not in rsp else rsp['emailId']
        response.application_id = None if 'applicationId' not in rsp else rsp['applicationId']
        response.hardware_type_name = None if 'hardwareTypeName' not in rsp else rsp['hardwareTypeName']
        response.software_version = None if 'softwareVersion' not in rsp else rsp['softwareVersion']
        response.configuration_name = None if 'configurationName' not in rsp else rsp['configurationName']
        response.peripheral_name = None if 'peripheralName' not in rsp else rsp['peripheralName']
        response.peripheral_software = None if 'peripheralSoftware' not in rsp else rsp['peripheralSoftware']
        response.activation_code = None if 'activationCode' not in rsp else rsp['activationCode']

        return response


class DeviceActivationKeyResponse(object):
    merchant_id = None
    application_id = None,
    activation_code = None,
    device_id = None,
    secret_api_key = None

    @classmethod
    def from_dict(cls, rsp):
        response = cls()
        response.merchant_id = None if 'merchantId' not in rsp else rsp['merchantId']
        response.device_id = None if 'deviceId' not in rsp else rsp['deviceId']
        response.application_id = None if 'applicationId' not in rsp else rsp['applicationId']
        response.activation_code = None if 'activationCode' not in rsp else rsp['activationCode']
        response.secret_api_key = None if 'apiKey' not in rsp else rsp['apiKey']

        return response


class DeviceParametersResponse(object):
    parameters = None
    device_id = None
    application_id = None
    hardware_type_name = None

    @classmethod
    def from_dict(cls, rsp):
        response = cls()
        response.parameters = None if 'parameters' not in rsp else rsp['parameters']
        response.device_id = None if 'deviceId' not in rsp else rsp['deviceId']
        response.application_id = None if 'applicationId' not in rsp else rsp['applicationId']
        response.hardware_type_name = None if 'hardwareTypeName' not in rsp else rsp['hardwareTypeName']

        return response


class DeviceApiKeyResponse(object):
    secret_api_key = None
    site_id = None
    device_id = None

    @classmethod
    def from_dict(cls, rsp):
        response = cls()
        response.secret_api_key = None if 'apiKey' not in rsp else rsp['apiKey']
        response.site_id = None if 'siteId' not in rsp else rsp['siteId']
        response.device_id = None if 'deviceId' not in rsp else rsp['deviceId']

        return response
