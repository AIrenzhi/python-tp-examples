"""

"""
from process.process import _hash
import json
from process.const import *
from datetime import datetime


def wrap_address_header(header):
    public_key = header.signer_public_key
    family_name = header.family_name
    address = _hash(family_name)[:6] + _hash(public_key)[:64]
    return address


def warp_adderss(namespace, key):
    return _hash(namespace)[:6] + _hash(key)[:64]


user_info_struct = {
    CUSTOMER.NAME: {
        CUSTOMER.INIT_ORDER: {},
        CUSTOMER.RECV_ORDER: {},
        CUSTOMER.CONF_ORDER: {},
        CUSTOMER.SUCC_ORDER: {}
    },
    SUPPLIER.NAME: {
        SUPPLIER.DEAL_ORDER: {},
        SUPPLIER.SEND_ORDER: {},
        SUPPLIER.CONM_ORDER: {},
        SUPPLIER.SUCE_ORDER: {}
    },
    PRODUCER.NAME: {
        PRODUCER.COME_ORDER: {},
        PRODUCER.SUCS_ORDER: {}
    }
}


def register(content, header, payload_dict):
    """
    注册
    :param content:
    :param header:
    :param payload_dict:{'role': role,
                      'action': 'regist',
                      "public_key": client._public_key}
    """
    role = payload_dict['role']
    struct = user_info_struct[role]
    address = wrap_address_header(header)
    content.set_state({address, json.dumps(struct)})


def get_user_info(content, namespace, key):
    info = content.get_state(warp_adderss(namespace, key))
    info = json.loads(info.decode())
    return info


def user_info2byte(info):
    info = json.dumps(info)
    return info.encode()


def set_init_order(content, header, payload_dict):
    """
    订单生成
    :param content:
    :param header:
    :param payload_dict: {
    'role': self._role,
    'action': 'init',
    'proto': {
        'num': _hash(num)[:70],  # 交易日期+key
        'title': title,
        'content': content,
        'money': money,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}
    :return:
    """
    public_key = header.signer_public_key
    family_name = header.family_name
    address = _hash(family_name)[:6] + _hash(public_key)[:64]
    user_info = content.get_state(address).decode()
    user_info = json.loads(user_info)
    user_info[CUSTOMER.INIT_ORDER][payload_dict['proto']['num']] = payload_dict
    content.set_state({address: json.dumps(user_info).encode()})


def deal_init_order(content, header, payload_dict):
    """
    供应商接单
    :param content:
    :param header:
    :param payload_dict: {
            'role': self._role,
            'address': [public_key],
            'action': 'deal',
            'data': {
                'order_num': order_num,
                'public_key': public_key
            }
        }
    :return:
    """
    customer_key = payload_dict['data']['public_key']
    order_num = payload_dict['data']['order_num']
    customer_address = warp_adderss(header.family_name, customer_key)
    customer_info = content.get_state(customer_address)
    customer_info = json.loads(customer_info.decode())
    order = customer_info[CUSTOMER.INIT_ORDER][order_num]
    order['deal_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order['proto_num'] = _hash(order['deal_date'] + customer_key + header.signer_public_key)
    order[CUSTOMER.NAME] = customer_key
    order[SUPPLIER.NAME] = header.signer_public_key
    customer_info[CUSTOMER.INIT_ORDER].pop(order_num)
    customer_info[CUSTOMER.RECV_ORDER] = order
    supplier_address = wrap_address_header(header)
    supplier_info = content.get_state(supplier_address)
    supplier_info = json.loads(supplier_info.decode())
    supplier_info[SUPPLIER.DEAL_ORDER][order_num] = order
    customer_info = json.dumps(customer_info)
    supplier_info = json.dumps(supplier_info)
    content.set_state({
        customer_address: customer_info.encode(),
        supplier_address: supplier_info.encode()
    })


def transmit(content, header, payload_dict):
    """
    供应商转发合同
    :param content:
    :param header:
    :param payload_dict:
    :return: {
            'role': self._role,
            'action': 'transmit',
            'address': [public_key],
            'proto': {
                'title': title,
                'content': content,
                'money': money,
                'order_num': order_num
            }
        }
    """
    supplier_address = wrap_address_header(header)
    supplier_info = get_user_info(content, header.family_name, header.signer_public_key)
    # customer_address = warp_adderss(header.family_name, payload_dict['address'][0])
    # customer_info = get_user_info(content, header.family_name, payload_dict['address'][0])
    order = supplier_info[SUPPLIER.DEAL_ORDER][payload_dict['proto']['order_num']]
    new_order = payload_dict['proto']
    new_order['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_order['num'] = _hash(new_order['date'] + header.signer_public_key)[:70]
    new_order['link_order'] = order
    supplier_info[SUPPLIER.DEAL_ORDER].pop(payload_dict['proto']['order_num'])
    supplier_info[SUPPLIER.SEND_ORDER][new_order['num']] = new_order
    content.set_state({supplier_address: user_info2byte(supplier_info)})


def transmit_deal(content, header, payload_dict):
    """
    生产商接到协议
    :param content:
    :param header:
    :param payload_dict: param = {
            'role': 'PRODUCER',
            'action': 'transmit_deal',
            'address': [origin_key, public_key],
            'proto': {
                'order_num': order_num,
                'origin_key': origin_key,
                'public_key': public_key
            }
        }
    :return:
    """
    origin_key = payload_dict['proto']['origin_key']
    order_num = payload_dict['proto']['order_num']
    supplier_key = payload_dict['proto']['public']
    producer_key = header.signer_public_key
    origin_address = warp_adderss(header.family_name, origin_key)
    supplier_address = warp_adderss(header.family_name, supplier_key)
    origin_info = get_user_info(content, header.family_name, origin_key)
    supplier_info = get_user_info(content, header.family_name, supplier_key)
    supplier_order = supplier_info[SUPPLIER.SEND_ORDER][order_num]
    deal_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    supplier_order['deal_date'] = deal_date
    supplier_order['signature'] = _hash(deal_date + origin_key + supplier_key + producer_key)
    supplier_order[PRODUCER.NAME] = producer_key
    origin_order_num = supplier_order['link_order']['num']
    # origin_order = origin_info[CUSTOMER.RECV_ORDER][order_num]
    origin_info[CUSTOMER.RECV_ORDER].pop(origin_order_num)
    origin_info[CUSTOMER.CONF_ORDER][order_num] = supplier_order
    supplier_order[SUPPLIER.SEND_ORDER].pop(order_num)
    supplier_order[SUPPLIER.CONM_ORDER][order_num] = supplier_order
    producer_info = get_user_info(content, header.family_name, producer_key)
    producer_info[PRODUCER.COME_ORDER][order_num] = supplier_order
    content.set_state({
        origin_address: user_info2byte(origin_info),
        supplier_address: user_info2byte(supplier_info),
        wrap_address_header(header): user_info2byte(producer_info)
    })


def success(content, header, payload_dict):
    """
    确认交易成功
    :param content:
    :param header:
    :param payload_dict: {
            'role': self._role,
            'action': 'success',
            'address': [s_key, p_key],
            'deal_num': deal_num,
            'supplier': s_key,
            'producer': p_key
        }
    :return:
    """
    namespace = header.family_name
    origin_key = header.signer_public_key
    supplier_key = payload_dict['supplier']
    producer_key = payload_dict['producer']
    origin_info = get_user_info(content, namespace, origin_key)
    supplier_info = get_user_info(content, namespace, supplier_key)
    