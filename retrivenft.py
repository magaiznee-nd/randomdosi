import hmac
import hashlib
import base64
import random
import string
import time
import requests
import json

class RequestBodyFlattener:

    def __flatten_key_value(self, key, value):
        if (isinstance(value, str)):
            return f"{key}={value}"

        if (isinstance(value, list)):
            l_key_value = {}
            for index, ele in enumerate(value):
                for lkey in list(ele.keys() | l_key_value.keys()):
                    if lkey in ele.keys():
                        lvalue = ele[lkey]
                    else:
                        lvalue = ""

                    if (lkey in l_key_value.keys()):
                        l_key_value[lkey] = f"{l_key_value[lkey]},{lvalue}"
                    else:
                        l_key_value[lkey] = f"{',' * index}{lvalue}"
            return "&".join("%s=%s" % (f"{key}.{lkey}", lvalue) for (lkey, lvalue) in sorted(l_key_value.items()))

    def flatten(self, body: dict = {}):
        sorted_body = sorted(body.items())
        return "&".join(self.__flatten_key_value(key, value) for (key, value) in sorted_body)


import logging

class SignatureGenerator:
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

    def __createSignTarget(self, method, path, timestamp, nonce, parameters: dict = {}):
        signTarget = f'{nonce}{str(timestamp)}{method}{path}'
        if(len(parameters) > 0):
            signTarget = signTarget + "?"

        return signTarget

    def generate(self, secret: str, method: str, path: str, timestamp: int, nonce: str, query_params: dict = {}, body: dict = {}):
        body_flattener = RequestBodyFlattener()
        all_parameters = {}
        all_parameters.update(query_params)
        all_parameters.update(body)

        self.__logger.debug("query_params: " + str(query_params))

        signTarget = self.__createSignTarget(method.upper(), path, timestamp, nonce, all_parameters)

        if (len(query_params) > 0):
            signTarget += '&'.join('%s=%s' % (key, value) for (key, value) in query_params.items())

        if (len(body) > 0):
            if (len(query_params) > 0):
                signTarget += "&" + body_flattener.flatten(body)
            else:
                signTarget += body_flattener.flatten(body)

        raw_hmac = hmac.new(bytes(secret, 'utf-8'), bytes(signTarget, 'utf-8'), hashlib.sha512)
        result = base64.b64encode(raw_hmac.digest()).decode('utf-8')

        return result
    
def contract_tokentype_tokenindex_retrive(tokenid):
    server_url = 'https://api.blockchain.line.me'
    service_api_key = '3e6cb7e0-1d35-4889-b7f4-a83b7a3e5f1a'
    service_api_secret = 'e53cc73e-201a-46d8-b126-93674639bb25'

    nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
    timestamp = int(round(time.time() * 1000))


    path = f'/v1/item-tokens/658b4b8a/non-fungibles/10000001/{tokenid}'

    headers = {
        'service-api-key': service_api_key,
        'nonce': nonce,
        'timestamp': str(timestamp)
    }
    signature_generator = SignatureGenerator()
    # generate 메서드를 사용하여 서명 생성
    signature = signature_generator.generate(secret=service_api_secret, method='GET', path=path, timestamp=timestamp, nonce=nonce)
    headers['signature'] = signature


    with open(f'json/{tokenid}.json', 'w') as file:
        json.dump(requests.get(server_url + path, headers=headers).json(), file, indent=4, ensure_ascii=False)
