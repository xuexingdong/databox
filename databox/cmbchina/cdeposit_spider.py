from typing import Any

from scrapy import Spider
from scrapy.http import Response

from databox.cmbchina import constants


class CDeposit(Spider):
    name = 'CDeposit'
    start_urls = [constants.URL]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        print(response.text)
