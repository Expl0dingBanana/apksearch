import os
import pytest

from apksearch import entities, parsing


def build_test(filename, base_entity):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "data", filename)
    with open(path, "rb") as fh:
        return {base_entity: fh.read()}


def test_process_search_result():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "data", "search_result.txt")
    pogo_galaxy = {
        "0.243.0": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon"
                "-go-samsung-galaxy-apps-version-0-243-0-release/"
            )
        ),
        "0.241.1": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-241-1-release/"
            )
        ),
        "0.241.0": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-241-0-release/"
            )
        ),
        "0.239.2": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-239-2-release/"
            )
        ),
        "0.239.1": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-239-1-release/"
            )
        ),
    }
    pogo = {
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
    }
    expected = {
        "Pokemon GO": entities.PackageBase(
            "Pokemon GO",
            info_page="https://www.apkmirror.com/apk/niantic-inc/pokemon-go/",
            versions=pogo,
        ),
        "Pokemon GO (Samsung Galaxy Store)": entities.PackageBase(
            "Pokemon GO (Samsung Galaxy Store)",
            info_page="https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/",
            versions=pogo_galaxy,
        ),
    }
    with open(path, "rb") as fh:
        res = parsing.process_search_result([fh.read()])
        assert res == expected


def test_process_release_result():
    pogo_samsung = {
        "0.243.0": entities.PackageVersion(
            (
                "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
                "-samsung-galaxy-apps-version-0-243-0-release/"
            )
        ),
    }
    pogo = {
        "0.243.0": entities.PackageVersion(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/"
        ),
    }
    results = {}
    results.update(build_test("pogo.0.243.0.txt", pogo["0.243.0"]))
    results.update(build_test("pogo_samsung.0.243.0.txt", pogo_samsung["0.243.0"]))
    parsing.process_release_result(results)
    expected_pogo = entities.PackageVersion(
        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/",
        arch_data={
            "armeabi-v7a": [
                entities.PackageVariant(
                    "BUNDLE",
                    "nodpi",
                    2022070700,
                    variant_info=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/"
                    ),
                ),
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2022070700,
                    variant_info=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/"
                    ),
                ),
            ],
            "arm64-v8a": [
                entities.PackageVariant(
                    "BUNDLE",
                    "nodpi",
                    2022070701,
                    variant_info=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/"
                    ),
                ),
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2022070701,
                    variant_info=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-2-android-apk-download/"
                    ),
                ),
            ],
        },
    )
    expected_pogo_samsung = entities.PackageVersion(
        (
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go"
            "-samsung-galaxy-apps-version-0-243-0-release/"
        ),
        arch_data={
            "arm64-v8a": [
                entities.PackageVariant(
                    "APK",
                    "nodpi",
                    2022070701,
                    variant_info=(
                        "https://www.apkmirror.com/apk/niantic-inc/pokemon-go-samsung-galaxy-apps-version/pokemon-go-samsung-galaxy-apps-version-0-243-0-release/pokemon-go-samsung-galaxy-store-0-243-0-android-apk-download/"
                    ),
                ),
            ],
        },
    )
    assert pogo["0.243.0"] == expected_pogo
    assert pogo_samsung["0.243.0"] == expected_pogo_samsung


def test_process_variant():
    # v7a / bundle
    variant1 = entities.PackageVariant(
        "APK",
        "nodpi",
        2022070700,
        variant_info=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/"
        ),
    )
    # v7a / apk
    variant2 = entities.PackageVariant(
        "BUNDLE",
        "nodpi",
        2022070700,
        variant_info=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/"
        ),
    )
    # v8a / apk
    variant3 = entities.PackageVariant(
        "APK",
        "nodpi",
        2022070701,
        variant_info=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/"
        ),
    )
    results = {}
    results.update(build_test("pogo.2022070700.bundle.txt", variant1))
    results.update(build_test("pogo.2022070700.apk.txt", variant2))
    results.update(build_test("pogo.2022070701.apk.txt", variant3))
    parsing.process_variant_result(results)
    assert variant1.variant_download_page == "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/download/?key=f38111b72fa406d0cfe673f737180de89b8d510a"
    assert variant2.variant_download_page == "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/download/?key=3ed61bef351d701567edf2b30df0f5fdf9c4c997&forcebaseapk=true"
    assert variant3.variant_download_page == "https://apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-2-android-apk-download/download/?key=5ea12fae1fcd938d0cc3d79fd2616fe641f8ced3&forcebaseapk=true"
    assert variant1.package == "com.nianticlabs.pokemongo"


@pytest.mark.parametrize(
    "filename,expected", [
        (
            "pogo.2022070700.bundle.download.txt",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3694845&key=6534b93ad807a70f7aa1b9eebfba23d586876b29"
        ),
        (
            "pogo.2022070700.apk.download.txt",
            "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3692376&key=71a5c3c608d755126c1c3081dd148aadfabc6b35&forcebaseapk=true"
        ),
    ]
)
def test_generate_download_link(filename, expected):
    fpath = os.path.join("tests", "data", filename)
    with open(fpath, "r") as fh:
        content = fh.read()
    assert parsing.generate_download_link(content) == expected


def test_process_variant_download_result():
    # v7a / bundle
    variant1 = entities.PackageVariant(
        "APK",
        "nodpi",
        2022070700,
        variant_info=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-android-apk-download/"
        ),
    )
    # v7a / apk
    variant2 = entities.PackageVariant(
        "BUNDLE",
        "nodpi",
        2022070700,
        variant_info=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-3-android-apk-download/"
        ),
    )
    # v8a / apk
    variant3 = entities.PackageVariant(
        "APK",
        "nodpi",
        2022070701,
        variant_info=(
            "https://www.apkmirror.com/apk/niantic-inc/pokemon-go/pokemon-go-0-243-0-release/pokemon-go-0-243-0-4-android-apk-download/"
        ),
    )
    results = {}
    results.update(build_test("pogo.2022070700.bundle.download.txt", variant1))
    results.update(build_test("pogo.2022070700.apk.download.txt", variant2))
    results.update(build_test("pogo.2022070701.apk.download.txt", variant3))
    parsing.process_variant_download_result(results)
    assert variant1.download_url == "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3694845&key=6534b93ad807a70f7aa1b9eebfba23d586876b29"
    assert variant2.download_url == "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3692376&key=71a5c3c608d755126c1c3081dd148aadfabc6b35&forcebaseapk=true"
    assert variant3.download_url == "https://apkmirror.com/wp-content/themes/APKMirror/download.php?id=3692379&key=0b3688c612fd32101b34adb2b6a00e09c032e1ae&forcebaseapk=true"
