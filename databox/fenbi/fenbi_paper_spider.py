import json
from typing import Any

import scrapy
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.fenbi.enums import OptionType, XingceModule
from databox.fenbi.items import QuestionItem, MaterialItem, PaperItem


class FenbiPaperSpider(RedisSpider):
    name = 'fenbi_paper'
    redis_key = "databox:" + name

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'ITEM_PIPELINES': {
            'databox.fenbi.pipelines.QuestionPipeline': 800,
        }
    }

    def __init__(self, paper_id=None, *args, **kwargs):
        super(FenbiPaperSpider, self).__init__(*args, **kwargs)
        self.paper_id = paper_id

    def make_request_from_data(self, data):
        data = json.loads(data)
        prefix = data['prefix']
        cookies = {
            'persistent': 'Fws2VUBYmr08vW/0t1l5MXHQpcXP75aIHdC4L6xqpra+sbpoZ2/7yDhv0ADP7aDX7gLrMJCZAYTUP/sdGWH+fw=='
        }
        if data['exercise_id']:
            yield scrapy.Request(f"https://tiku.fenbi.com/api/{prefix}/exercises/{data['exercise_id']}",
                                 cookies=cookies,
                                 meta={'prefix': prefix}, dont_filter=True)
        else:
            formdata = {
                'type': '1',
                'paperId': str(data['paper_id']),
                'exerciseTimeMode': '2'
            }
            yield scrapy.FormRequest(f"https://tiku.fenbi.com/api/{prefix}/exercises",
                                     formdata=formdata, cookies=cookies,
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
        materials = self.extract_materials(response)
        questions = self.extract_questions(response, paper, materials)
        paper_item = PaperItem()
        paper_item['paper_id'] = paper['paperId']
        paper_item['name'] = paper['name']
        paper_item['chapters'] = [chapter['name'] for chapter in paper['chapters']]
        paper_item['materials'] = materials
        paper_item['questions'] = questions
        yield paper_item

    @staticmethod
    def extract_materials(response):
        materials = response.jmespath('materials').getall()
        material_items = []
        for material in materials:
            material_item = MaterialItem()
            material_item['material_id'] = material['id']
            material_item['content'] = material['content']
            material_items.append(material_item)
        return material_items

    @staticmethod
    def extract_questions(response, paper, materials: list[MaterialItem]):
        question_chapter_name_dict = FenbiPaperSpider.get_question_chapter_name_dict(paper)
        questions = response.jmespath('questions').getall()
        question_items = []
        for question in questions:
            question_item = QuestionItem()
            question_item['question_id'] = question['id']
            question_item['content'] = question['content']
            chapter_name = question_chapter_name_dict[question['id']]
            question_item['chapter_name'] = chapter_name
            question_item['module'] = XingceModule(chapter_name)
            if question['accessories']:
                accessory = question['accessories'][0]
                question_item['option_type'] = OptionType(accessory['type'])
                question_item['options'] = accessory['options']
            question_item['answer'] = question['correctAnswer']
            if question['materialIndexes']:
                question_item['material_ids'] = [materials[index]['material_id'] for index in
                                                 question['materialIndexes']]
            question_item['paper_id'] = paper['paperId']
            question_items.append(question_item)
        return question_items

    @staticmethod
    def get_question_chapter_name_dict(paper):
        chapters = paper['chapters']
        question_ids = paper['questionIds']

        question_to_chapter = {}
        current_question_index = 0
        for chapter in chapters:
            for _ in range(chapter["questionCount"]):
                question_to_chapter[question_ids[current_question_index]] = chapter["name"]
                current_question_index += 1
        return question_to_chapter
