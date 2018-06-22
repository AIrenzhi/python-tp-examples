from client.client import DemoClient, _hash, wrap_address
from datetime import datetime

class Customer(DemoClient):

    def __init__(self, base_url, private_key):
        super(Customer,self).__init__(base_url, private_key)
        # self._private = private_key
        # self._base_url = base_url
        self._role = 'CUSTOMER'

    def send_order(self, title, content, money):
        num = str(int(datetime.now().timestamp()))+self._public_key
        action = {
            'role': self._role,
            'action': 'init',
            'proto': {
                'num': _hash(num)[:70],  # 交易日期+key
                'title': title,
                'content': content,
                'money': money,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        }
        self.wrap_and_send(action)


    def confirm_order(self, deal_num, s_key, p_key):
        action = {
            'role': self._role,
            'action': 'success',
            'address': [s_key, p_key],
            'deal_num': deal_num,
            'supplier': s_key,
            'producer': p_key
        }
        self.wrap_and_send(action)


if __name__ == '__main__':
    publicKeyStr = '03b0a21a6ef6abcfe2cccb5fc67bde5d0219a90767463df8a927ba5a570d84c29c'
    privateKeyStr = 'abea62da5c1e392d99603f12fadf238165d0a952a153b4982e35222166acbb0f'

    cus = Customer('sasa', privateKeyStr)
    cus.send_order('dsada', 'sdadas', 23)