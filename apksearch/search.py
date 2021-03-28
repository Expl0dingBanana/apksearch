import asyncio
import copy
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
    search_results = execute_package_search(packages)
    package_defs = parsing.process_search_result(search_results)
    release_defs = execute_release_info(package_defs)
    parsing.process_release_result(release_defs)
    variant_defs = execute_variant_info(package_defs)
    parsing.process_variant_result(variant_defs)
    return package_defs


def execute_package_search(packages: List[str]) -> Dict[str, PackageBase]:
    """Perform aiohttp requests to APKMirror

    :param list packages: Packages that will be searched for. Each package will generate a new
        request

    :return: A list of results containing the first page of each package search
    :rtype: list
    """
    param_list: List[str] = _generate_params_list(packages)
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_perform_search(loop, param_list))


def execute_release_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    """Execute all requests related to the package versions

    :param dict package_defs: Current found information from the initial search. It will be updated
        in place with the release information found during the step
    """
    releases = []
    for info in packages.values():
        for package_version in info.versions.values():
            releases.append(package_version)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_perform_release(loop, releases))
    return results


def execute_variant_info(packages: Dict[str, PackageBase]) -> Dict[PackageVersion, str]:
    variants = []
    for info in packages.values():
        for package_version in info.versions.values():
            for arch in package_version.arch.values():
                variants.extend(arch)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_perform_variant(loop, variants))
    return results


def gather_release_info(releases: List[PackageBase]) -> Tuple[PackageVersion, PackageVariant, str]:
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_perform_release(loop, releases))
    return results


async def _fetch_one(session, url, params):
    async with session.get(url, ssl=ssl.SSLContext(), params=params, headers=HEADERS) as response:
        return await response.text()


async def _perform_search(loop, query_params: List[str]):
    async with aiohttp.ClientSession(loop=loop) as session:
        results = await asyncio.gather(
            *[_fetch_one(session, QUERY_URL, param) for param in query_params],
            return_exceptions=True,
        )
        return results


async def _perform_release(loop, releases: List[PackageVersion]):
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = {}
        for request in releases:
            tasks[request] = _fetch_one(session, request.link, {})
        results = await gather_from_dict(tasks)
        return results


async def _perform_variant(loop, variants: List[PackageVariant]):
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = {}
        for request in variants:
            tasks[request] = _fetch_one(session, request.download_page, {})
        results = await gather_from_dict(tasks)
        return results
