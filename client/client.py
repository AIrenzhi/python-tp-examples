import hashlib
from base64 import b64decode, b64encode
import time
import requests
import yaml
import json

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

FAMILY_NAME = 'demo'
publicKeyStr = '03b0a21a6ef6abcfe2cccb5fc67bde5d0219a90767463df8a927ba5a570d84c29c'
privateKeyStr = 'abea62da5c1e392d99603f12fadf238165d0a952a153b4982e35222166acbb0f'


def create_user():
    private_key = Secp256k1PrivateKey.new_random().as_hex()
    # public_key = CryptoFactory(create_context('secp256k1')).new_signer(private_key)
    return private_key


def _hash(data):
    return hashlib.sha512(data.encode()).hexdigest()


def wrap_address(pulic_key):
    return _hash(FAMILY_NAME)[:6] + _hash(pulic_key)[:64]


class DemoClient:

    def __init__(self, base_url, private_key=privateKeyStr):
        self._base_url = base_url
        self._signer = CryptoFactory(create_context('secp256k1')).new_signer(
            Secp256k1PrivateKey.from_hex(private_key))
        self._public_key = self._signer.get_public_key().as_hex()
        self._address = _hash(FAMILY_NAME)[:6] + _hash(self._public_key)[:64]

    @classmethod
    def register(cls, base_url, role):
        private_key = create_user()
        client = DemoClient(base_url, private_key)
        client.wrap_and_send({'role': role,
                              'action': 'regist',
                              "public_key": client._public_key})
        return private_key

    def wrap_and_send(self, data_dict):

        payload = json.dumps(data_dict).encode()

        address = self._address
        inputAddressList = [address]
        outputAddresslist = [address]

        relate_address = data_dict.get('address', [])
        for re_address in relate_address:
            # if relate_address:
            inputAddressList.append(wrap_address(re_address))
            outputAddresslist.append(wrap_address(re_address))

        header = TransactionHeader(
            signer_public_key=self._public_key,
            family_name=FAMILY_NAME,
            family_version='1.0',
            inputs=inputAddressList,
            outputs=outputAddresslist,
            dependencies=[],
            payload_sha512=_hash(payload.decode()),
            batcher_public_key=self._public_key,
            nonce=time.time().hex().encode()
        ).SerializeToString()

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transactionList = [transaction]

        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in transactionList]
        ).SerializeToString()

        batch = Batch(
            header=header,
            transactions=transactionList,
            header_signature=self._signer.sign(header)
        )

        batch_list_serialize = BatchList(batches=[batch]).SerializeToString()
        return self._send_to_restapi('batches', batch_list_serialize,
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
                return result.text
        except requests.ConnectionError as err:
            print('连接失败', err)
        except BaseException as err:
            print(err)
