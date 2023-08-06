from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class ProductImage(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.shopProduct = None
        self.imagePath = None
        self.imageThumbnailPath = None
        self.imageViewpath = None
        self.fileName = None
        self.fileSize = None
        self.fileType = None
        self.uploadUrl = None
        self.downloadUrl = None
        self.downloadThumbnailUrl = None
        self.downloadViewUrl = None
