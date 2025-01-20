import json

import httpx
from sqlalchemy.orm import Session

from databox.fenbi.model.models import Paper, Material, Question
from databox.pipelines import DBPipeline


class PaperPipeline:
    url = 'http://localhost:8081/land/papers/add'

    def __init__(self):
        self.client = httpx.Client(verify=False, timeout=300)

    def process_item(self, item, spider):
        r = self.client.post(self.url, json=dict(item))

    def close_spider(self, spider):
        self.client.close()


class QuestionPipeline(DBPipeline):

    def process_item(self, item, spider):
        paper = Paper()
        paper.paper_id = item.get('paper_id')
        paper.name = item.get('name', None)
        paper.chapters = item.get('chapters', None)
        materials = []
        for material_item in item.get('materials', []):
            material = Material()
            material.material_id = material_item.get('material_id')
            material.content = material_item.get('content', None)
            materials.append(material)
        questions = []
        for question_item in item.get('questions', []):
            question = Question()
            question.question_id = question_item.get('question_id')
            question.content = question_item.get('content', None)
            question.chapter_name = question_item.get('chapter_name', None)
            question.module = question_item.get('module').name
            question.option_type = question_item.get('option_type').value
            question.options = json.dumps(question_item.get('options', []), ensure_ascii=False)
            question.answer = question_item.get('answer', None)
            question.material_ids = json.dumps(question_item.get('material_ids', []), ensure_ascii=False)
            question.paper_id = question_item.get('paper_id', None)
            questions.append(question)
        with Session(self.engine) as session:
            session.add(paper)
            if materials:
                session.add_all(materials)
            if questions:
                session.add_all(questions)
            session.commit()
        return item
