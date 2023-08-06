from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class InstallationShopProduct(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.code = None
        self.description = None
        self.groups = None
        self.pids = None
        self.quantity = None
        self.unit = None
        self.price = None
        self.rate = None
