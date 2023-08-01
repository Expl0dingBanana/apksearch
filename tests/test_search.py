# flake8: noqa E501

import pytest
from aioresponses import aioresponses

from apksearch import entities, search

from . import get_test_contents


@pytest.mark.asyncio
async def test_execute_package_page():
    with aioresponses() as mocked:
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/", status=200, body=get_test_contents("pogo.html")
        )
        results = await search.execute_package_page(["https://www.apkmirror.com/apk/niantic-inc/pokemon-go/"])
    expected = {
        "Pokemon GO": entities.PackageBase(
            "Pokemon GO",
            "com.nianticlabs.pokemongo",
            info_page="https://www.apkmirror.com/apk/niantic-inc/pokemon-go/",
            versions={
                "0.243.0": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/"
                ),
                "0.241.1": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-241-1-release/"
                ),
                "0.241.0": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-241-0-release/"
                ),
                "0.239.2": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-239-2-release/"
                ),
                "0.239.1": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-239-1-release/"
                ),
                "0.239.0": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-239-0-release/"
                ),
                "0.237.0": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-237-0-release/"
                ),
                "0.235.0": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-235-0-release/"
                ),
                "0.233.1": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-233-1-release/"
                ),
                "0.233.0": entities.PackageVersion(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-233-0-release/"
                ),
            },
        )
    }
    assert results == expected


@pytest.mark.asyncio
async def test_package_search_match():
    versions = ["0.243.0", "0.241.0"]
    with aioresponses() as mocked:
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/", status=200, body=get_test_contents("pogo.html")
        )
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/",
            status=200,
            body=get_test_contents("pogo_0.243.0.html"),
        )
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-241-0-release/",
            status=200,
            body=get_test_contents("pogo_0.243.0.html"),
        )
        results = await search.package_search_match(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/", versions=versions
        )
    assert len(versions) == len(results.versions)
    for version in versions:
        assert version in results.versions
        assert "armeabi-v7a" in results.versions[version].arch
        assert "arm64-v8a" in results.versions[version].arch


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "variant,expected_download_url",
    [
        (
            entities.PackageVariant(
                "APK",
                "nodpi",
                2022070700,
                variant_info="https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/",
            ),
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3692376&key=1893849fcf0eaeb278bb3d53c9425a96f190c243&forcebaseapk=true",
        )
    ],
)
async def test_generate_download_url(variant, expected_download_url):
    with aioresponses() as mocked:
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/",
            status=200,
            body=get_test_contents("pogo_0.243.0_32_apk.html"),
        )
        mocked.get(
            "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/download/?key=74cda5696fa78d83b50da3f4fa5c9885d17076a1&forcebaseapk=true",
            status=200,
            body=get_test_contents("pogo_0.243.0_32_apk_download.html"),
        )
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/",
            status=200,
            body=get_test_contents("pogo_0.243.0_32_bundle.html"),
        )
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/",
            status=200,
            body=get_test_contents("pogo_0.243.0_64_bundle.html"),
        )
        mocked.get(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-2-android-apk-download/",
            status=200,
            body=get_test_contents("pogo_0.243.0_64_apk.html"),
        )
        assert await search.generate_download_url(variant) == expected_download_url
