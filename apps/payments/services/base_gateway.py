class BasePaymentGateway:

    def create_payment(self, order):
        raise NotImplementedError

    def verify_payment(self, data):
        raise NotImplementedError