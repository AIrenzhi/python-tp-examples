from client.client import DemoClient


class Producer:

    def __init__(self, base_url, private_key):
        self._private = private_key
        self._base_url = base_url
        self.client = DemoClient(base_url, private_key)

    def get_order(self, order_num, origin_key, public_key):
        # self.client.wrap_and_send()
        param = {
            'role': 'PRODUCER',
            'action': 'transmit_deal',
            'address': [origin_key, public_key],
            'proto': {
                'order_num': order_num,
                'origin_key': origin_key,
                'public_key': public_key
            }
        }
        self.client.wrap_and_send(param)
