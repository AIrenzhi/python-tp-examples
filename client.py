import hashlib
import base64
from base64 import b64encode
import time
import requests
import yaml
import json

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch


FAMILY_NAME='simplewallet'
publicKeyStr = '03b0a21a6ef6abcfe2cccb5fc67bde5d0219a90767463df8a927ba5a570d84c29c'
# privateKeyStr = 'abea62da5c1e392d99603f12fadf238165d0a952a153b4982e35222166acbb0f'
privateKeyStr = '48f7f528ad712c26cb70a47e98cb1e13bf1f1f927d01b44cf274ae86d2e3bfd2'

def _hash(data):
    return hashlib.sha512(data).hexdigest()

class SimpleTestClient:

    def __init__(self, baseUrl):
        self._baseUrl = baseUrl
        privateKey = Secp256k1PrivateKey.from_hex(privateKeyStr)
        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(privateKey)
        self._publicKey = self._signer.get_public_key().as_hex()
        self.publicKey = self._signer.get_public_key().as_hex()

        self._address = _hash(FAMILY_NAME.encode('utf-8'))[0:6]
                        # _hash(self._publicKey.encode('utf-8'))[0:64]


    def wrap_and_send(self, data_dict):
        # rawPayload = action
        # for val in values:
        #     rawPayload = ",".join([rawPayload, str(val)])

        payload = json.dumps(data_dict).encode()

        address = self._address
        inputAddressList = [address]
        outputAddressList = [address]

        header = TransactionHeader(
            signer_public_key=self._publicKey,
            family_name=FAMILY_NAME,
            family_version="1.0",
            inputs=inputAddressList,
            outputs=outputAddressList,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._publicKey,
            nonce=time.time().hex().encode()
        ).SerializeToString()

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transactionList = [transaction]

        header = BatchHeader(
            signer_public_key=self._publicKey,
            transaction_ids=[txn.header_signature for txn in transactionList]
        ).SerializeToString()

        batch = Batch(
            header=header,
            transactions=transactionList,
            header_signature=self._signer.sign(header))

        batch_list = BatchList(batches=[batch])
        return self._send_to_restapi(
            "batches",
            batch_list.SerializeToString(),
            'application/octet-stream')

    def _send_to_restapi(self,
                      suffix,
                      data=None,
                      contentType=None):
        if self._baseUrl.startswith("http://"):
            url = "{}/{}".format(self._baseUrl, suffix)
        else:
            url = "http://{}/{}".format(self._baseUrl, suffix)

        headers = {}

        if contentType is not None:
            headers['Content-Type'] = contentType

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                print('服务器错误')

        except requests.ConnectionError as err:
            print('连接失败',err)
            # raise SimpleWalletException(
            #     'Failed to connect to {}: {}'.format(url, str(err)))

        except BaseException as err:
            # raise SimpleWalletException(err)
            print(err)
        return result.text


    def get_state(self):
        result = self._send_to_restapi(
            "state/{}".format(self._address))
        print(result)
        try:
            return base64.b64decode(yaml.safe_load(result)["data"])
        except BaseException:
            return None

    def get_block(self):
        result = requests.get(self._baseUrl+'/blocks')
        datas = result.json()['data']
        for data in datas:
            # print(data)
            payload = data['batches'][0]['transactions'][0]['payload']
            # print(payload)
            p = base64.b64decode(payload.encode()).decode()
            try:
                print(json.loads(p))
            except:
                pass



if __name__ == '__main__':
    cli = SimpleTestClient('http://192.168.33.130:8008')
    result = cli.wrap_and_send(dict(key=cli.publicKey, action='错误得'))
    # print(result)
    # print(cli.get_state())
    # resp = requests.get('http://127.0.0.1:8008/state')
    # print(resp.json())
    # cli.get_block()

