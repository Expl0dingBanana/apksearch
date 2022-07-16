import logging
import re
import unicodedata
from typing import Dict, List
import urllib

from bs4 import BeautifulSoup

from .entities import PackageBase, PackageVariant, PackageVersion

logger = logging.getLogger(__name__)

# Regex for extracting title and version from the search page
title_info = re.compile(r"(.*) ([\d\.]+)$")

# Base URL when querying apkmirror
BASE_URL: str = "https://www.apkmirror.com"

# Download URL that can be auto-generated
DOWNLOAD_URL: str = "https://apkmirror.com/wp-content/themes/APKMirror/download.php?{}"


def process_search_result(results: List[str]) -> Dict[str, PackageBase]:
    """Process the result of the search

    :param list results: List of results from querying the search page

    :return: Dictionary containing the known information from the search
    :rtype: dict
    """
    package_defs: Dict[str, PackageBase] = {}
    for package_result in results:
        dom = BeautifulSoup(package_result, "html5lib")
        download_area = dom.findAll("div", {"class": "listWidget"})[0]
        packages = download_area.findAll("div", {"class": "appRow"})
        for package in packages:
            app_details = package.find("h5", {"class": "appRowTitle"})
            title_details = title_info.search(app_details["title"])
            link = "{}{}".format(BASE_URL, app_details.find("a")["href"])
            main_page = "{}/".format(link.rsplit("/", 2)[0])
            title: str = unicodedata.normalize("NFKD", title_details.group(1)).encode("ascii", "ignore").decode()
            version: str = title_details.group(2)
            package_details = PackageBase(title, main_page)
            if title not in package_defs:
                package_defs[title] = package_details
            if version not in package_defs[title].versions:
                package_defs[title].versions[version] = PackageVersion(link)
    return package_defs


def process_release_result(results: Dict[PackageVersion, str]):
    """Process the result of the release page

    :param dict results: Results from the aiohttp request
    """
    for package_version, result in results.items():
        dom = BeautifulSoup(result, "html5lib")
        download_area = dom.findAll("div", {"class": "listWidget"})[0]
        variants = download_area.findAll("div", {"class": "headerFont"})[1:]
        for variant in variants:
            variant_info = variant.findAll("div", {"class": "table-cell"})
            package_info = variant_info[0].findAll("span")
            apk_type = package_info[0].text
            if apk_type != "APK":
                apk_type = "BUNDLE"
            version_code = int(variant_info[0].findAll("span", {"class": "colorLightBlack"})[0].text)
            architecture = variant_info[1].text
            dpi = variant_info[3].text
            variant_info = "{}{}".format(BASE_URL, variant_info[4].find("a")["href"])
            package_variant = PackageVariant(apk_type, dpi, version_code, variant_info=variant_info)
            if architecture not in package_version.arch:
                package_version.arch[architecture] = []
            package_version.arch[architecture].append(package_variant)


def process_variant_result(results: Dict[PackageVariant, str]):
    """Processes the result of a specific variant

    :param dict results: Results from the aiohttp request
    """
    for package_variant, result in results.items():
        dom = BeautifulSoup(result, "html5lib")
        download_button = dom.findAll("a", {"class": "downloadButton"})[0]
        package_variant.variant_download_page = "https://apkmirror.com{}".format(download_button["href"])
        package_area = dom.find("div", {"class": "appspec-value"})
        package_variant.package = package_area.findAll("span")[-1].text.split(" ", 1)[1].strip()


def process_variant_download_result(results: Dict[PackageVariant, str]):
    """Processes the result of a specific variant

    :param dict results: Results from the aiohttp request
    """
    for package_variant, result in results.items():
        package_variant.download_url = generate_download_link(result)


def generate_download_link(result: str) -> str:
    """Parse the download information of a specific variant

    :param str result: Result from the request
    """
    dom = BeautifulSoup(result, "html5lib")
    download_form = dom.findAll("form", {"id": "filedownload"})[0]
    link_attrs = download_form.findAll("input")
    query_params = {}
    for link_attr in link_attrs:
        query_params[link_attr["name"]] = link_attr["value"]
    params = urllib.parse.urlencode(query_params)
    return DOWNLOAD_URL.format(params)
