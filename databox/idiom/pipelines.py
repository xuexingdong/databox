from databox.pipelines import HttpPipeline


class IdiomPipeline(HttpPipeline):
    def get_path(self):
        return '/land/idioms/add'
