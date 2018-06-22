import hashlib
import logging
import traceback
import json

import sys
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

log = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

FAMILY_NAME = "simplewallet"

def _hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

sw_namespace = _hash(FAMILY_NAME)

class SawtoothTestTransactionHandler(TransactionHandler):

    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return self._namespace_prefix

    def apply(self, transaction, context):
        header = transaction.header
        payload = transaction.payload
        # print(header)
        # print(payload)
        try:
            payload_dict = json.loads(payload.decode())
            key = payload_dict['key']
            address = _hash(FAMILY_NAME)[:6]+_hash('USERINFO')[:64]
            # addresse = _hash('demot')[:6]+_hash(key)[:64]
            action = payload_dict['action']
            # raise InvalidTransaction('错误代码')
            # print(payload_dict)
            print(context.get_state([address])[0].data.decode())
            # context.set_state({address: action.encode()})

        except Exception as e:
            print('格式错误', e)



def main():
    try:
        processor = TransactionProcessor(url='tcp://127.0.0.1:4004')
        handler = SawtoothTestTransactionHandler(sw_namespace)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

