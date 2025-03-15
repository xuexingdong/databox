import json
import time

from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from databox.petchain.item_loaders import PetLoader
from databox.petchain.items import PetItem


class PetChainSpider(RedisSpider):
    name = 'petchain'
    redis_batch_size = 64

    def start_requests(self):
        return [self.generate_request(1)]

    custom_settings = {
        'ITEM_PIPELINES':      {
            'databox.petchain.pipelines.PetPipeline': 300,
        },
        'COOKIES_ENABLED':     False,
        'RETRY_TIMES':         10
    }

    def parse(self, response):
        res = json.loads(response.text)
        if not res['data']['hasData']:
            self.logger.info('已到最后一页')
            return
        pets = res['data']['petsOnSale']
        for pet in pets:
            loader = PetLoader(item=PetItem())
            loader.add_value('id', pet['id'])
            loader.add_value('pet_id', pet['petId'])
            loader.add_value('birth_type', pet['birthType'])
            loader.add_value('mutation', pet['mutation'])
            loader.add_value('generation', pet['generation'])
            loader.add_value('rare_degree', pet['rareDegree'])
            loader.add_value('name', pet['desc'])
            loader.add_value('pet_type', pet['petType'])
            loader.add_value('amount', pet['amount'])
            loader.add_value('bg_color', pet['bgColor'])
            loader.add_value('pet_url', pet['petUrl'])
            yield Request('https://pet-chain.baidu.com/data/pet/queryPetById', method='POST',
                          headers=response.headers,
                          body=json.dumps({
                              'petId': pet['petId'],
                              'appId': 1}),
                          meta={
                              'item_loader': loader
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
        loader = response.meta['item_loader']
        loader.add_value('attributes', pet['attributes'])
        loader.add_value('self_status', pet['selfStatus'])
        loader.add_value('father_id', pet['faterId'])
        loader.add_value('mother_id', pet['motherId'])
        loader.add_value('is_on_chain', pet['isOnChain'])
        loader.add_value('eth_addr', pet['ethAddr'])
        loader.add_value('head_icon', pet['headIcon'])
        loader.add_value('username', pet['userName'])
        yield loader.load_item()

    @staticmethod
    def generate_request(page):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {'pageNo':        page,
                'pageSize':      20,
                # 时间戳
                'requestId':     int(round(time.time() * 1000)),
                # 按稀有度排序
                'querySortType': 'RAREDEGREE_DESC',
                'petIds':        [],
                'appId':         1
                }
        return Request('https://pet-chain.baidu.com/data/market/queryPetsOnSale', method='POST', headers=headers,
                       body=json.dumps(data), dont_filter=True)
