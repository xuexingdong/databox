import json
import time

from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from databox.petchain.item_loaders import PetLoader
from databox.petchain.items import PetItem


class PetChainSpider(RedisSpider):
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
        if not res['data']['hasData']:
            self.logger.info('已到最后一页')
            return
        pets = res['data']['petsOnSale']
        for pet in pets:
            l = PetLoader(item=PetItem())
            l.add_value('id', pet['id'])
            l.add_value('pet_id', pet['petId'])
            l.add_value('birth_type', pet['birthType'])
            l.add_value('mutation', pet['mutation'])
            l.add_value('generation', pet['generation'])
            l.add_value('rare_degree', pet['rareDegree'])
            l.add_value('name', pet['desc'])
            l.add_value('pet_type', pet['petType'])
            l.add_value('amount', pet['amount'])
            l.add_value('bg_color', pet['bgColor'])
            l.add_value('pet_url', pet['petUrl'])
            yield Request('https://pet-chain.baidu.com/data/pet/queryPetById', method='POST',
                          headers=response.headers,
                          body=json.dumps({
                              'petId': pet['petId'],
                              'appId': 1}),
                          meta={
                              'item_loader': l
                          },
                          priority=1,
                          callback=self.parse_pet_detail,
                          dont_filter=True)

        data = json.loads(response.request.body)
        self.logger.info("页码: " + str(data['pageNo'] + 1))
        yield self.generate_request(data['pageNo'] + 1)

    def parse_pet_detail(self, response):
        res = json.loads(response.text)
        if '00' != res['errorNo']:
            self.logger.error('请求失败')
            return
        pet = res['data']
        l = response.meta['item_loader']
        l.add_value('attributes', pet['attributes'])
        l.add_value('self_status', pet['selfStatus'])
        l.add_value('father_id', pet['faterId'])
        l.add_value('mother_id', pet['motherId'])
        l.add_value('is_on_chain', pet['isOnChain'])
        l.add_value('eth_addr', pet['ethAddr'])
        l.add_value('head_icon', pet['headIcon'])
        l.add_value('username', pet['userName'])
        yield l.load_item()

    @staticmethod
    def generate_request(page):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {'pageNo': page,
                'pageSize': 20,
                # 时间戳
                'requestId': int(round(time.time() * 1000)),
                # 按稀有度排序
                'querySortType': 'RAREDEGREE_DESC',
                'petIds': [],
                'appId': 1
                }
        return Request('https://pet-chain.baidu.com/data/market/queryPetsOnSale', method='POST', headers=headers,
                       body=json.dumps(data), dont_filter=True)
