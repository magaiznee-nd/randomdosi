import os
import hmac
import hashlib
import base64
import json
import requests
import random
import string
import time


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


class SignatureGenerator:
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

# NFT를 다른 wallet으로 전송하는 함수
def contract_tokentype_tokenindex_retrive():
    # 환경 변수에서 필요한 정보를 가져옵니다.
    server_url = 'https://api.blockchain.line.me'
    service_api_key = '3e6cb7e0-1d35-4889-b7f4-a83b7a3e5f1a'
    service_api_secret = 'e53cc73e-201a-46d8-b126-93674639bb25'

    # nonce와 timestamp를 생성합니다.
    nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
    timestamp = int(round(time.time() * 1000))

    # 전송할 NFT의 정보를 포함하는 경로를 설정합니다.
    path = '/v1/wallets/link12y3xhlxz3ylc20mhal7qpmfks77vl3h99596nx/item-tokens/658b4b8a/non-fungibles/batch-transfer'

    # 요청 본문을 설정합니다. 이는 전송할 NFT와 수신자의 정보를 포함합니다.
    request_body = {
        'walletSecret': 'NRuS0z8YamUyqZIkdZfdfSF+W6s2eXWvvozt+BvKI2Y=',
        'toAddress': 'link1d7e37qzh72wd0d5kalueldsrwfjf4h865gzdvn',
        'transferList': [
            {
                'tokenId': '10000001000007e8'
            },
            {
                'tokenId': '10000001000007fa'
            },
            {
                'tokenId': '10000001000007d9'
            }
        ]
    }

    # 요청 헤더를 설정합니다. 이는 API 키, nonce, timestamp 등의 정보를 포함합니다.
    headers = {
        'service-api-key': service_api_key,
        'nonce': nonce,
        'timestamp': str(timestamp),
        'Content-Type': 'application/json'
    }

    # 요청에 서명을 추가합니다.
    signature_generator = SignatureGenerator()
    signature = signature_generator.generate(
        secret=service_api_secret,
        method='POST',
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        body=request_body
    )
    headers['signature'] = signature

    # 요청을 보내고 응답을 반환합니다.
    try:
        res = requests.post(server_url + path, headers=headers, json=request_body)
        response = res.json()
        print(f"Response: {response}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None



def searchNFT_wallet(wallet):
    server_url = 'https://api.blockchain.line.me'
    service_api_key = '3e6cb7e0-1d35-4889-b7f4-a83b7a3e5f1a'
    service_api_secret = 'e53cc73e-201a-46d8-b126-93674639bb25'

    nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
    timestamp = int(round(time.time() * 1000))

    path = f'/v1/wallets/{wallet}/item-tokens/658b4b8a/non-fungibles/10000001'

    query_params = {
        'limit': 100,
        'orderBy': 'desc',
        'page': 1
    }

    headers = {
        'service-api-key': service_api_key,
        'nonce': nonce,
        'timestamp': str(timestamp)
    }
    signature_generator = SignatureGenerator()
    signature = signature_generator.generate(
        secret=service_api_secret,
        method='GET',  # 이 부분을 'GET'으로 변경했습니다.
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        query_params=query_params  # body 인자를 제거하고 query_params 인자를 추가했습니다.
    )
    headers['signature'] = signature

    try:
        res = requests.get(server_url + path, params=query_params, headers=headers)
        response = res.json()
        print(f"Response: {response}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None    


# searchNFT_wallet("link1n4psstd0jalvvyz570rz28qyxjpsf7hxrd95y8");
