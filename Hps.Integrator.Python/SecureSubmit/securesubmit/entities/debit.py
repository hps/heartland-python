from securesubmit.entities import HpsTransaction


class HpsDebitAuthorization(HpsTransaction):
    authorization_code = None
    available_balance = None
    avs_result_code = None
    cvv_result_code = None
    avs_result_text = None
    cvv_result_text = None
    card_type = None
    authorized_amount = None

    @classmethod
    def from_dict(cls, rsp):
        sale_response = rsp['Transaction'].itervalues().next()

        sale = super(HpsDebitAuthorization, cls).from_dict(rsp)
        if 'AuthCode' in sale_response:
            sale.authorization_code = sale_response['AuthCode']

        if 'AVSRsltCode' in sale_response:
            sale.avs_result_code = sale_response['AVSRsltCode']

        if 'AVSRsltText' in sale_response:
            sale.avs_result_text = sale_response['AVSRsltText']

        if 'CVVRsltCode' in sale_response:
            sale.cvv_result_code = sale_response['CVVRsltCode']

        if 'CVVRsltText' in sale_response:
            sale.cvv_result_text = sale_response['CVVRsltText']

        if 'CardType' in sale_response:
            sale.card_type = sale_response['CardType']

        if 'AvailableBalance' in sale_response:
            sale.available_balance = sale_response['AvailableBalance']

        if 'AuthAmt' in sale_response:
            sale.authorized_amount = sale_response['AuthAmt']

        return sale