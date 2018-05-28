from databox.pipelines import MongoPipeline


class UserPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db['neteasemusic_user'].update_one({'id': item['id']}, {'$set': item}, True)
        return item


class FollowPipeline(MongoPipeline):
    def process_item(self, item, spider):
        # 关注
        follow = self.db['neteasemusic_follow'].find_one({'id1': item['id2'], 'id2': item['id2']})
        # 被关注
        followed = self.db['neteasemusic_follow'].find_one({'id1': item['id2'], 'id2': item['id1']})
        # 没关注也没被关注
        if not follow and not followed:
            self.db['neteasemusic_follow'].insert_one({'id1': item['id1'], 'id2': item['id2'], 'both_status': False})
        # 未关注但是已被关注
        if followed and not follow:
            self.db['neteasemusic_follow'].insert_one({'id1': item['id1'], 'id2': item['id2'], 'both_status': True})
            self.db['neteasemusic_follow'].update_one({'id1': item['id2'], 'id2': item['id1']},
                                                      {'$set': {'both_status': True}})

        # 已关注但未被关注和已关注且已被关注情况不用处理
        return item
