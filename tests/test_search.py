import asyncio

import pytest

from apksearch import search


@pytest.mark.asyncio
async def test_package_search():
    results = await asyncio.gather(search.package_search(["com.nianticlabs.pokemongo"]))
    result = results[0]
    assert isinstance(result, dict)
