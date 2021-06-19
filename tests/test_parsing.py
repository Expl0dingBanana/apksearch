import os

import pytest

from apksearch import entities, parsing


def build_test(filename, base_entity):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "data", filename)
    with open(path, "rb") as fh:
        return {base_entity: fh.read()}


@pytest.mark.asyncio
async def test_process_search_result():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "data", "search_result.txt")
    pogo_galaxy = {
        "0.203.1": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon"
                "-go-samsung-galaxy-apps-version-0-203-1-release/"
            )
        ),
        "0.203.0": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-203-0-release/"
            )
        ),
        "0.201.1": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-201-1-release/"
            )
        ),
        "0.201.0": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-201-0-release/"
            )
        ),
        "0.199.0": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-199-0-release/"
            )
        ),
    }
    pogo = {
        "0.203.1": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/"
        ),
        "0.203.0": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-0-release/"
        ),
        "0.201.1": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-201-1-release/"
        ),
        "0.201.0": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-201-0-release/"
        ),
        "0.199.0": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-199-0-release/"
        ),
    }
    expected = {
        "Pokemon GO": entities.PackageBase(
            "Pokemon GO",
            info_page="https://www.apkmirror.com/apk/niantic-inc/pokemon-go/",
            versions=pogo,
        ),
        "Pokemon GO (Samsung Galaxy Apps version)": entities.PackageBase(
            "Pokemon GO (Samsung Galaxy Apps version)",
            info_page="https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/",
            versions=pogo_galaxy,
        ),
    }
    with open(path, "rb") as fh:
        res = await parsing.process_search_result([fh.read()])
        assert res == expected


@pytest.mark.asyncio
async def test_process_release_result():
    pogo_samsung = {
        "0.203.1": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-203-1-release/"
            )
        ),
    }
    pogo = {
        "0.203.1": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/"
        ),
    }
    results = {}
    results.update(build_test("pogo.0.203.1.txt", pogo["0.203.1"]))
    results.update(build_test("pogo_samsung.0.203.1.txt", pogo_samsung["0.203.1"]))
    await parsing.process_release_result(results)
    expected_pogo = entities.PackageVersion(
        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/",
        arch_data={
            "armeabi-v7a": [
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2021031800,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
                        "-0-203-1-android-apk-download/"
                    ),
                ),
                entities.PackageVariant(
                    "BUNDLE",
                    "480dpi",
                    2021032200,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
                        "-0-203-1-6-android-apk-download/"
                    ),
                ),
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2021032200,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
                        "-0-203-1-4-android-apk-download/"
                    ),
                ),
            ],
            "arm64-v8a": [
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2021031801,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
                        "-0-203-1-2-android-apk-download/"
                    ),
                ),
                entities.PackageVariant(
                    "BUNDLE",
                    "480-640dpi",
                    2021032201,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
                        "-0-203-1-3-android-apk-download/"
                    ),
                ),
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2021032201,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
                        "-0-203-1-5-android-apk-download/"
                    ),
                ),
            ],
        },
    )
    expected_pogo_samsung = entities.PackageVersion(
        (
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
            "-samsung-galaxy-apps-version-0-203-1-release/"
        ),
        arch_data={
            "armeabi-v7a": [
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2021031800,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/"
                        "pokemon-go-samsung-galaxy-apps-version-0-203-1-release/pokemon-go-samsung-galaxy-"
                        "apps-version-0-203-1-android-apk-download/"
                    ),
                ),
            ],
            "arm64-v8a": [
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2021031801,
                    download_page=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/"
                        "pokemon-go-samsung-galaxy-apps-version-0-203-1-release/pokemon-go-samsung-galaxy"
                        "-apps-version-0-203-1-2-android-apk-download/"
                    ),
                ),
            ],
        },
    )
    assert pogo["0.203.1"] == expected_pogo
    assert pogo_samsung["0.203.1"] == expected_pogo_samsung


@pytest.mark.asyncio
async def test_process_variant():
    variant1 = entities.PackageVariant(
        "APK",
        "nodpi",
        2021031800,
        download_page=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
            "-0-203-1-android-apk-download/"
        ),
    )
    variant2 = entities.PackageVariant(
        "BUNDLE",
        "480dpi",
        2021032200,
        download_page=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/pokemon-go"
            "-0-203-1-6-android-apk-download/"
        ),
    )
    variant3 = entities.PackageVariant(
        "APK",
        "nodpi",
        2021032200,
        download_page=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-203-1-release/"
            "pokemon-go-0-203-1-4-android-apk-download/"
        ),
    )
    results = {}
    results.update(build_test("pogo.2021031800.apk.txt", variant1))
    results.update(build_test("pogo.2021032200.bundle.txt", variant2))
    results.update(build_test("pogo.2021032200.apk.txt", variant3))
    await parsing.process_variant_result(results)
    assert (
        variant1.download_url
        == "https://www.apkmirror.com/wp-content/themes/APKMirror/download.php?id=2071632&forcebaseapk"
    )
    assert variant2.download_url == "https://www.apkmirror.com/wp-content/themes/APKMirror/download.php?id=2089155"
    assert (
        variant3.download_url
        == "https://www.apkmirror.com/wp-content/themes/APKMirror/download.php?id=2086850&forcebaseapk"
    )
