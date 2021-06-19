import asyncio
import copy
import logging
import ssl
from typing import Awaitable, Dict, Hashable, List, Tuple

import aiohttp

from . import parsing
from .entities import PackageBase, PackageVariant, PackageVersion

__all__ = ["package_search"]


QUERY_URL: str = "https://www.apkmirror.com"
QUERY_PARAMS: Dict[str, str] = {
    "post_type": "app_release",
    "searchtype": "apk",
    "s": "",
    "minapi": "true",
}
HEADERS = {
    "user-agent": "apksearch APKMirrorSearcher/0.0.1",
}

logger = logging.getLogger(__name__)


async def gather_from_dict(tasks: Dict[Hashable, Awaitable], loop=None, return_exceptions=False):
    results = await asyncio.gather(*tasks.values(), loop=loop, return_exceptions=return_exceptions)
    return dict(zip(tasks.keys(), results))


async def _generate_params_list(packages: List[str]) -> List[str]:
    param_list = []
    for package in packages:
        params = copy.copy(QUERY_PARAMS)
        params["s"] = package
        param_list.append(params)
    return param_list


async def package_search(packages: List[str]) -> Dict[str, PackageBase]:
    """Entrypoint for performing the search"""
    search_results = await execute_package_search(packages)
    package_defs = await parsing.process_search_result(search_results)
    logger.debug("Packages found: %s", ",".join(list(package_defs.keys())))
    release_defs = await execute_release_info(package_defs)
    await parsing.process_release_result(release_defs)
    variant_defs = await execute_variant_info(package_defs)
    await parsing.process_variant_result(variant_defs)
    return package_defs


async def execute_package_search(packages: List[str]) -> List[str]:
    """Perform aiohttp requests to APKMirror

    :param list packages: Packages that will be searched for. Each package will generate a new
        request

    :return: A list of results containing the first page of each package search
    :rtype: list
    """
    param_list: List[str] = await _generate_params_list(packages)
    search_results = await asyncio.gather(_perform_search(param_list))
    return search_results[0]


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
    results = loop.run_until_complete(_perform_release(loop, releases))
    return results


async def execute_variant_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    variants = []
    for info in packages.values():
        for package_version in info.versions.values():
            for arch in package_version.arch.values():
                variants.extend(arch)
    loop = asyncio.get_running_loop()
    results = loop.run_until_complete(_perform_variant(loop, variants))
    return results


async def gather_release_info(releases: List[PackageBase]) -> Tuple[PackageVersion, PackageVariant, str]:
    loop = asyncio.get_running_loop()
    results = loop.run_until_complete(_perform_release(loop, releases))
    return results


async def _fetch_one(session, url, params):
    async with session.get(url, ssl=ssl.SSLContext(), params=params, headers=HEADERS) as response:
        logger.debug("About to query %s", response.request_info)
        return await response.text()


async def _perform_search(query_params: List[str], loop=None):
    if loop is None:
        loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        required_urls = [_fetch_one(session, QUERY_URL, param) for param in query_params]
        logger.info("About to query %s packages", len(required_urls))
        results = await asyncio.gather(
            *required_urls,
            return_exceptions=True,
        )
        return results


async def _perform_release(loop, releases: List[PackageVersion]):
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = {}
        logger.info("About to query %s releases", len(releases))
        for request in releases:
            tasks[request] = _fetch_one(session, request.link, {})
        results = await gather_from_dict(tasks)
        return results


async def _perform_variant(loop, variants: List[PackageVariant]):
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = {}
        logger.info("About to query %s releases", len(variants))
        for request in variants:
            tasks[request] = _fetch_one(session, request.download_page, {})
        results = await gather_from_dict(tasks)
        return results
