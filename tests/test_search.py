import pytest

from apksearch import search


@pytest.mark.asyncio
async def test_package_search_async():
    results = await search.package_search_async(["com.nianticlabs.pokemongo"])
    assert isinstance(results, dict)
    assert "Pokemon GO" in results


def test_package_search():
    results = search.package_search(["com.nianticlabs.pokemongo"])
    assert isinstance(results, dict)
    assert "Pokemon GO" in results
