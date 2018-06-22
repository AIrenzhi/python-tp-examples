from client.client import DemoClient


class Producer:

    def __init__(self, base_url, private_key):
        self._private = private_key
        self._base_url = base_url
        self.client = DemoClient(base_url, private_key)
        self._role = 'SUPPLIER'

    def get_order(self, order_num, public_key):
        param = {
            'role': self._role,
            'address': [public_key],
            'action': 'deal',
            'data': {
                'order_num': order_num,
                'public_key': public_key
            }
        }
        self.client.wrap_and_send(param)

    def send_order(self, title, content, money, order_num, public_key):
        param = {
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
        self.client.wrap_and_send(param)
    