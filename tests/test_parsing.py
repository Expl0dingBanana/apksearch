# flake8: noqa E501

import pytest

from apksearch import entities, parsing

from . import get_test_contents


def build_test(filename, base_entity):
    return {base_entity: get_test_contents(filename)}


@pytest.mark.parametrize(
    "filename,expected",
    [
        (
            "pogo_0.243.0_32_apk_download.html",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3692376&key=1893849fcf0eaeb278bb3d53c9425a96f190c243&forcebaseapk=true",
        ),
        (
            "pogo_0.243.0_32_bundle_download.html",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3694845&key=82896f35e2a70709ab00137be28fc968624a661c",
        ),
    ],
)
def test_generate_download_link(filename, expected):
    content = get_test_contents(filename)
    assert parsing.generate_download_link(content) == expected


@pytest.mark.parametrize(
    "variant,filename,expected",
    [
        (
            entities.PackageVariant(
                "APK",
                "nodpi",
                2022070700,
                variant_info=(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/"
                ),
            ),
            "pogo_0.243.0_32_apk_download.html",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3692376&key=1893849fcf0eaeb278bb3d53c9425a96f190c243&forcebaseapk=true",
        ),
        (
            entities.PackageVariant(
                "BUNDLE",
                "nodpi",
                2022070700,
                variant_info=(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/"
                ),
            ),
            "pogo_0.243.0_32_bundle_download.html",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3694845&key=82896f35e2a70709ab00137be28fc968624a661c",
        ),
        (
            entities.PackageVariant(
                "APK",
                "nodpi",
                2022070701,
                variant_info=(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/"
                ),
            ),
            "pogo_0.243.0_64_bundle_download.html",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3694846&key=1ba4afa3a8584742f2fcc2ac09dfc6376fb20a07",
        ),
    ],
)
def test_process_variant_download_result(variant, filename, expected):
    results = {variant: get_test_contents(filename)}
    parsing.process_variant_download_result(results)
    assert variant.download_url == expected


@pytest.mark.parametrize(
    "variant,filename,expected",
    [
        (
            entities.PackageVariant(
                "APK",
                "nodpi",
                2022070700,
                variant_info=(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/"
                ),
            ),
            "pogo_0.243.0_32_apk.html",
            "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/download/?key=74cda5696fa78d83b50da3f4fa5c9885d17076a1&forcebaseapk=true",
        ),
        (
            entities.PackageVariant(
                "BUNDLE",
                "nodpi",
                2022070700,
                variant_info=(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/"
                ),
            ),
            "pogo_0.243.0_32_bundle.html",
            "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/download/?key=0b0631f224bb3c03a3b5ff4ad37cc99db53cf9ac",
        ),
        (
            entities.PackageVariant(
                "APK",
                "nodpi",
                2022070701,
                variant_info=(
                    "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/"
                ),
            ),
            "pogo_0.243.0_64_bundle.html",
            "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/download/?key=5a99f61e71380269ef0e71e33715ddbc073f966c",
        ),
    ],
)
def test_process_variant(variant, filename, expected):
    results = {variant: get_test_contents(filename)}
    parsing.process_variant_result(results)
    assert variant.variant_download_page == expected


# @TODO
def test_process_release_result():
    pass


@pytest.mark.parametrize(
    "filename,expected",
    [
        (
            "pogo.html",
            {
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
            },
        ),
    ],
)
def test_parse_package_page(filename, expected):
    data = get_test_contents(filename)
    assert parsing.process_package_page([data]) == expected
