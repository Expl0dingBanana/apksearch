from typing import Dict, List


class PackageVariant(object):
    def __init__(
        self,
        apk_type: str,
        dpi: str,
        version_code: int,
        download_url: str = None,
        variant_info: str = None,
        variant_download_page: str = None,
        package: str = None,
    ):
        self.apk_type: str = apk_type
        self.download_url: str = download_url
        self.variant_info: str = variant_info
        self.variant_download_page: str = variant_download_page
        self.dpi: str = dpi
        self.version_code: int = version_code
        self.package = package

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash(str(self))


class PackageVersion(object):
    def __init__(self, link, arch_data: Dict[str, List[PackageVariant]] = None):
        self.link = link
        if arch_data is None:
            arch_data: Dict[str, List[PackageVariant]] = {}
        self.arch = arch_data
        # @TODO - Do we want to have a version-code lookup here?

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash(str(self))


class PackageBase(object):
    def __init__(
        self,
        title: str,
        package_name: str,
        info_page: str = None,
        versions: Dict[str, PackageVersion] = None,
    ):
        self.title: str = title
        self.package_name = package_name
        self.info_page: str = info_page
        self.versions: dict[str, PackageVersion] = versions if versions else {}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ and self.versions == other.versions

    def __str__(self):
        return str(self.__dict__)
