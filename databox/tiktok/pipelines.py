from peewee import Model, CharField, DateTimeField, SqliteDatabase

db = SqliteDatabase('databox.db')


class TiktokVideo(Model):
    id = CharField(unique=True)
    nickname = CharField()
    avatar = CharField()
    create_time = DateTimeField()
    desc = CharField()
    cover = CharField()
    download_addr = CharField()

    class Meta:
        database = db
        legacy_table_names = False


class TiktokVideoPipeline:
    def __init__(self):
        db.connect()
        db.create_tables([TiktokVideo])

    def process_item(self, item, spider):
        TiktokVideo.replace(id=item['id'],
                            nickname=item['nickname'],
                            avatar=item['avatar'],
                            create_time=item['create_time'],
                            desc=item['desc'],
                            cover=item['cover'],
                            download_addr=item['download_addr']
                            ).execute()
        return item

    def close_spider(self, spider):
        # 在爬虫结束时关闭数据库连接
        db.close()
