from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject


class Product(AbstractIkologikCustomerObject):

    def __init__(self, customer: str):
        super().__init__(customer)

        self.code = None
        self.description = None
        self.groups = None
        self.pids = None
        self.quantity = None
        self.unit = None
        self.price = None
        self.rate = None
