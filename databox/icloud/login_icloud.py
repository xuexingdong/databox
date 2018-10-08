import json

from scrapy.commands import ScrapyCommand
from scrapy_redis import connection

from databox.icloud.icloud_system import ICloudSystem


class Command(ScrapyCommand):

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('-u', '--username',
                          dest='username',
                          help='icloud username'
                          )
        parser.add_option('-p', '--password',
                          dest='password',
                          help='icloud password'
                          )

    def run(self, args, opts):
        # 账号密码设置进入redis
        conn = connection.from_settings(self.settings)
        conn.set('databox:icloud:username', opts.username)
        conn.set('databox:icloud:password', opts.password)

        driver_path = self.settings.get('CHROME_DRIVER_PATH')
        icloud = ICloudSystem(driver_path)
        icloud.login(opts.username, opts.password)
        cookies = icloud.get_cookies()
        icloud.close()
        conn.set('databox:icloud:cookies', json.dumps(cookies))
