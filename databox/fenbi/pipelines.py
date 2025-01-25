from databox.pipelines import HttpPipeline


class PaperPipeline(HttpPipeline):
    def get_path(self):
        return '/land/papers/add'
