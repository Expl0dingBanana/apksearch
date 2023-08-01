import asyncio
import copy
import logging
import ssl
from typing import Awaitable, Dict, Hashable, List, Tuple, Union

import aiohttp

from . import parsing
from .entities import PackageBase, PackageVariant, PackageVersion

__all__ = ["package_search_match", "generate_download_url"]


QUERY_URL: str = "https://www.apkmirror.com"
QUERY_PARAMS: Dict[str, str] = {
    "post_type": "app_release",
    "searchtype": "apk",
    "s": "",
    "minapi": "true",
}
HEADERS = {
    "user-agent": "apksearch APKMirrorSearcher/1.0.0",
}

logger = logging.getLogger(__name__)


async def gather_from_dict(tasks: Dict[Hashable, Awaitable], return_exceptions=False):
    results = await asyncio.gather(*tasks.values(), return_exceptions=return_exceptions)
    return dict(zip(tasks.keys(), results))


def _generate_params_list(packages: List[str]) -> List[str]:
    param_list = []
    for package in packages:
        params = copy.copy(QUERY_PARAMS)
        params["s"] = package
        param_list.append(params)
    return param_list


def package_search(packages: List[str]) -> Dict[str, PackageBase]:
    """Entrypoint for performing the search"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(package_search_async(packages))


async def package_search_async(packages: List[str]) -> Dict[str, PackageBase]:
    """Entrypoint for performing the search async"""
    search_results = await execute_package_search(packages)
    package_defs = parsing.process_search_result(search_results)
    logger.debug("Packages found: %s", ",".join(list(package_defs.keys())))
    release_defs = await execute_release_info(package_defs)
    parsing.process_release_result(release_defs)
    variant_defs = await execute_variant_info(package_defs)
    parsing.process_variant_result(variant_defs)
    return package_defs


async def package_search_match(package_url: [str], versions: List[str]) -> PackageBase:
    """Perform a targeted search on a root page

    :param package_url: URL to the package
    :param version: Version string to process
    """
    package_defs = await execute_package_page([package_url])
    package_name = list(package_defs.keys())[0]
    for pkg_version in list(package_defs[package_name].versions.keys())[:]:
        if pkg_version not in versions:
            del package_defs[package_name].versions[pkg_version]
    if len(package_defs[package_name].versions) != len(versions):
        diff = set(versions).difference(set(package_defs[package_name].versions))
        raise RuntimeError("{} is missing {}".format(package_name, diff))
    release_defs = await execute_release_info(package_defs)
    parsing.process_release_result(release_defs)
    return package_defs[package_name]


async def generate_download_url(variant: PackageVariant) -> str:
    """Generates a packages temporary download URL

    :param variant: Variant to determine URL
    """
    results = await _perform_basic_query([variant.variant_info])
    variant_defs = {variant: results[0]}
    parsing.process_variant_result(variant_defs)
    results = await _perform_basic_query([variant.variant_download_page])
    download_results = {variant: results[0]}
    parsing.process_variant_download_result(download_results)
    return variant.download_url


async def execute_package_search(packages: List[str]) -> List[str]:
    """Perform aiohttp requests to APKMirror

    :param list packages: Packages that will be searched for. Each package will generate a new
        request

    :return: A list of results containing the first page of each package search
    :rtype: list
    """
    param_list: List[str] = _generate_params_list(packages)
    return await _perform_search(param_list)


async def execute_package_page(packages: List[str]) -> Dict[str, PackageBase]:
    """Query all root package pages

    :param packages: List of root package pages to query
    """
    results = await _perform_basic_query(packages)
    return parsing.process_package_page(results)


async def execute_release_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    """Execute all requests related to the package versions

    :param dict package_defs: Current found information from the initial search. It will be updated
        in place with the release information found during the step
    """
    releases = []
    for info in packages.values():
        for package_version in info.versions.values():
            releases.append(package_version)
    return await _perform_dict_lookup(releases)


async def execute_variant_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    variants = []
    for info in packages.values():
        for package_version in info.versions.values():
            for arch in package_version.arch.values():
                variants.extend(arch)
    return await _perform_dict_lookup(variants)


async def gather_release_info(releases: List[PackageBase]) -> Tuple[PackageVersion, PackageVariant, str]:
    loop = asyncio.get_running_loop()
    results = loop.run_until_complete(_perform_dict_lookup(releases))
    return results


async def _fetch_one(session, url, params):
    async with session.get(url, ssl=ssl.SSLContext(), params=params, headers=HEADERS) as response:
        logger.debug("About to query %s", response.request_info)
        return await response.text()


async def _perform_search(query_params: List[str]):
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        required_urls = [_fetch_one(session, QUERY_URL, param) for param in query_params]
        logger.info("About to query %s packages", len(required_urls))
        results = await asyncio.gather(
            *required_urls,
            return_exceptions=True,
        )
        return results


async def _perform_basic_query(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        required_urls = [_fetch_one(session, url, {}) for url in urls]
        logger.info("About to query %s packages", len(required_urls))
        results = await asyncio.gather(
            *required_urls,
            return_exceptions=True,
        )
        return results


async def _perform_dict_lookup(requests: List[Union[PackageVersion, PackageVariant]]):
    if len(requests) == 0:
        return []
    if isinstance(requests[0], PackageVersion):
        identifier = "releases"
        url_attr = "link"
    else:
        identifier = "variants"
        url_attr = "variant_download_page"
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = {}
        logger.info("About to query %s %s", len(requests), identifier)
        for request in requests:
            tasks[request] = _fetch_one(session, getattr(request, url_attr), {})
        results = await gather_from_dict(tasks)
        return results
