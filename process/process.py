import hashlib
import logging
import traceback
import json

import sys
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

from process.role.actions import actions, register

log = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

FAMILY_NAME = "demo"


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
        try:
            payload_dict = json.loads(payload.decode())
            action = payload_dict['action']
            if actions == 'regist':
                register(context, header, payload_dict)
                return
            actions[action](context, header, payload_dict)
        except:
            print('格式错误')
