import json

from scrapy import Request, Spider

from databox.petchain.items import PetItem


class PetChainSpider(Spider):
    name = 'petchain'

    def start_requests(self):
        return [self.generate_request(1)]

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.petchain.pipelines.PetPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'CONCURRENT_REQUESTS': 64,
        'RETRY_TIMES': 10
    }

    def parse(self, response):
        res = json.loads(response.text)
        if '00' != res['errorNo']:
            self.logger.error('请求失败, body: ' + res)
            return
        if not res['data']['hasData']:
            self.logger.warning('暂无数据')
            return
        pets = res['data']['petsOnSale']
        for pet in pets:
            item = PetItem()
            item['id'] = pet['id']
            item['pet_id'] = pet['petId']
            item['birth_type'] = pet['birthType']
            item['mutation'] = pet['mutation']
            item['generation'] = pet['generation']
            item['rare_degree'] = pet['rareDegree']
            item['name'] = pet['desc']
            item['pet_type'] = pet['petType']
            item['amount'] = float(pet['amount'])
            item['bg_color'] = pet['bgColor']
            item['pet_url'] = pet['petUrl']
            yield Request('https://pet-chain.baidu.com/data/pet/queryPetById', method='POST',
                          headers=response.headers,
                          body=json.dumps({
                              'petId': item['pet_id'],
                              'appId': 1}),
                          meta={
                              'item': item
                          },
                          priority=1,
                          callback=self.parse_pet,
                          dont_filter=True)

        data = json.loads(response.request.body)
        self.logger.info("页码: " + str(data['pageNo'] + 1))
        yield self.generate_request(data['pageNo'] + 1)

    def parse_pet(self, response):
        res = json.loads(response.text)
        if '00' != res['errorNo']:
            self.logger.error('请求失败')
            return
        item = response.meta['item']
        pet = res['data']
        item['attributes'] = pet['attributes']
        item['self_status'] = pet['selfStatus']
        item['father_id'] = pet['faterId']
        item['mother_id'] = pet['motherId']
        item['is_on_chain'] = pet['isOnChain']
        item['eth_addr'] = pet['ethAddr']
        item['head_icon'] = pet['headIcon']
        item['username'] = pet['userName']
        yield item

    @staticmethod
    def generate_request(page):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {'pageNo': page,
                'pageSize': 20,
                # 按稀有度排序
                'querySortType': 'RAREDEGREE_DESC',
                'petIds': [],
                'appId': 1
                }
        return Request('https://pet-chain.baidu.com/data/market/queryPetsOnSale', method='POST', headers=headers,
                       body=json.dumps(data), dont_filter=True)
