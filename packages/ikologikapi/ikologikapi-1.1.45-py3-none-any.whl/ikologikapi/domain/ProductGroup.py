from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class ProductGroup(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.name = None
        self.count = None
