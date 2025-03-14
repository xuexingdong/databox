import json
from typing import Any

import scrapy
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.fenbi.items import QuestionItem, MaterialItem, PaperItem, ChapterItem


class FenbiPaperSpider(RedisSpider):
    name = 'fenbi_paper'
    redis_key = "databox:" + name
    redis_batch_size = 2
    max_idle_time = 60

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.fenbi.pipelines.PaperPipeline': 800,
        }
    }

    def __init__(self, paper_id=None, cookies=None, *args, **kwargs):
        super(FenbiPaperSpider, self).__init__(*args, **kwargs)
        self.paper_id = paper_id
        self.cookies = cookies

    def make_request_from_data(self, data):
        data = json.loads(data)
        prefix = data['prefix']

        if data['exercise_id']:
            yield scrapy.Request(f"https://tiku.fenbi.com/api/{prefix}/exercises/{data['exercise_id']}",
                                 cookies=self.cookies,
                                 meta={'prefix': prefix}, dont_filter=True)
        else:
            yield scrapy.FormRequest(f"https://tiku.fenbi.com/api/{prefix}/exercises",
                                     formdata={
                                         'type': '1',
                                         'paperId': str(data['paper_id']),
                                         'exerciseTimeMode': '2'
                                     },
                                     cookies=self.cookies,
                                     meta={'prefix': prefix}, dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        paper = response.jmespath('sheet').get()
        prefix = response.meta['prefix']
        exercise_id = response.jmespath('id').get()
        yield scrapy.Request(f"https://tiku.fenbi.com/api/{prefix}/universal/auth/questions?id={exercise_id}",
                             callback=self.parse_paper, cookies=response.request.cookies,
                             meta={'paper': paper}, dont_filter=True)

    def parse_paper(self, response: Response):
        paper = response.meta['paper']
        chapters = self.extract_chapters(paper)
        materials = self.extract_materials(response)
        questions = self.extract_questions(response)
        paper_item = PaperItem()
        paper_item['out_paper_id'] = paper['paperId']
        paper_item['name'] = paper['name']
        paper_item['question_count'] = paper['questionCount']
        paper_item['chapters'] = chapters
        paper_item['materials'] = materials
        paper_item['questions'] = questions
        yield paper_item

    @staticmethod
    def extract_materials(response):
        materials = response.jmespath('materials').getall()
        material_items = []
        for material in materials:
            material_item = MaterialItem()
            material_item['out_material_id'] = material['id']
            material_item['content'] = material['content']
            material_items.append(dict(material_item))
        return material_items

    @staticmethod
    def extract_questions(response):
        questions = response.jmespath('questions').getall()
        question_items = []
        for question in questions:
            question_item = QuestionItem()
            question_item['out_question_id'] = question['id']
            question_item['content'] = question['content']
            if question['accessories']:
                accessory = question['accessories'][0]
                question_item['option_type'] = accessory['type']
                question_item['options'] = accessory['options']
            question_item['answer'] = question['correctAnswer']
            if question['materialIndexes']:
                question_item['material_indexes'] = question['materialIndexes']
            question_items.append(dict(question_item))
        return question_items

    @staticmethod
    def extract_chapters(paper):
        chapter_items = []
        for chapter in paper['chapters']:
            chapter_item = ChapterItem()
            chapter_item['name'] = chapter['name']
            chapter_item['desc'] = chapter['desc']
            chapter_item['question_count'] = chapter['questionCount']
            chapter_items.append(dict(chapter_item))
        return chapter_items
