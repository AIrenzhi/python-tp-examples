# 发出协议
init_proto = {
    'num': '',  # 交易日期+key
    'title': '',
    'content': '',
    'money': '',
    'date': '',
}

# 达成协议
deal_proto = {
    'title': '',
    'content': '',
    'money': '',
    'date': '',
    'deal_date': '',
    'proto_num': '',  # 交易日期+from_key+to_key
    'customer':'',
    'supplier': ''
}

# 转送协议
transation_proto = {
    'title': '',
    'content': '',
    'money': '',
    'date': '',
    'link_proto': '',
}

# 转送完成
tranastion_complete_proto = {
    'title': '',
    'content': '',
    'money': '',
    'date': '',
    'link_proto': '',
    'deal_date': '',
    'proto_num': ''
}

# 协议完毕
tranastion_deal_proto = {
    'title': '',
    'content': '',
    'money': '',
    'date': '',
    'link_proto': '',
    'deal_date': '',
    'proto_num': '',
    'signature': ''  # 交易日期+from_key+to_key+too_key
}


# 指令
def action(ac, proto):
    return {
        'role': '',
        'action': ac,
        'proto': proto,
    }


# 指令集
actions = {
    'regist': {
        'role': '',
        'public_key': ''
    },
    'init': action('init', init_proto),
    'deal': action('deal', deal_proto),
    'transmit': action('transmit', transation_proto),
    'transmit_deal': action('transmit_deal', tranastion_complete_proto),
    'success': action('success', tranastion_deal_proto)
}
