import asyncio
import copy
import logging
import ssl
from typing import Awaitable, Dict, Hashable, List, Tuple, Union

import aiohttp

from . import parsing
from .entities import PackageBase, PackageVariant, PackageVersion

__all__ = ["package_search", "package_search_async"]


QUERY_URL: str = "https://www.apkmirror.com"
QUERY_PARAMS: Dict[str, str] = {
    "post_type": "app_release",
    "searchtype": "apk",
    "s": "",
    "minapi": "true",
}
HEADERS = {
    "user-agent": "apksearch APKMirrorSearcher/0.0.2",
}

logger = logging.getLogger(__name__)


async def gather_from_dict(tasks: Dict[Hashable, Awaitable], loop=None, return_exceptions=False):
    results = await asyncio.gather(*tasks.values(), loop=loop, return_exceptions=return_exceptions)
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


async def execute_package_search(packages: List[str]) -> List[str]:
    """Perform aiohttp requests to APKMirror

    :param list packages: Packages that will be searched for. Each package will generate a new
        request

    :return: A list of results containing the first page of each package search
    :rtype: list
    """
    param_list: List[str] = _generate_params_list(packages)
    loop = asyncio.get_running_loop()
    return await _perform_search(loop, param_list)


async def execute_release_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    """Execute all requests related to the package versions

    :param dict package_defs: Current found information from the initial search. It will be updated
        in place with the release information found during the step
    """
    releases = []
    for info in packages.values():
        for package_version in info.versions.values():
            releases.append(package_version)
    loop = asyncio.get_running_loop()
    return await _perform_dict_lookup(loop, releases)


async def execute_variant_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    variants = []
    for info in packages.values():
        for package_version in info.versions.values():
            for arch in package_version.arch.values():
                variants.extend(arch)
    loop = asyncio.get_running_loop()
    return await _perform_dict_lookup(loop, variants)


async def gather_release_info(releases: List[PackageBase]) -> Tuple[PackageVersion, PackageVariant, str]:
    loop = asyncio.get_running_loop()
    results = loop.run_until_complete(_perform_dict_lookup(loop, releases))
    return results


async def _fetch_one(session, url, params):
    async with session.get(url, ssl=ssl.SSLContext(), params=params, headers=HEADERS) as response:
        logger.debug("About to query %s", response.request_info)
        return await response.text()


async def _perform_search(loop, query_params: List[str]):
    async with aiohttp.ClientSession(loop=loop) as session:
        required_urls = [_fetch_one(session, QUERY_URL, param) for param in query_params]
        logger.info("About to query %s packages", len(required_urls))
        results = await asyncio.gather(
            *required_urls,
            return_exceptions=True,
        )
        return results


async def _perform_dict_lookup(loop, requests: List[Union[PackageVersion, PackageVariant]]):
    if len(requests) == 0:
        return []
    if type(requests[0]) == PackageVersion:
        identifier = "releases"
        url_attr = "link"
    else:
        identifier = "variants"
        url_attr = "download_page"
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = {}
        logger.info("About to query %s %s", len(requests), identifier)
        for request in requests:
            tasks[request] = _fetch_one(session, getattr(request, url_attr), {})
        results = await gather_from_dict(tasks)
        return results
