from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class Product(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str = None):
        super().__init__(customer, installation)

        self.groups = None
        self.code = None
        self.description = None
        self.pids = None
        self.quantity = None
        self.price = None
        self.rate = None
