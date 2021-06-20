import logging

import nest_asyncio

from .search import package_search, package_search_async

nest_asyncio.apply()

__all__ = ["package_search", "package_search_async"]


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
