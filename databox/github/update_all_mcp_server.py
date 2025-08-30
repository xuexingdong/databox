import os

from redis import StrictRedis
from sqlalchemy import create_engine, text

from databox.github.github_repo_search_spider import GithubRepoSearchSpider


def main():
    connection_string = os.getenv('PG_URL')
    engine = create_engine(connection_string)
    r = StrictRedis.from_url(os.getenv('REDIS_URL'), decode_responses=True)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM projects where url !='' and user_uuid is null order by update_time asc limit 1"))
        rows = result.fetchall()
        for row in rows:
            r.rpush(GithubRepoSearchSpider.redis_key, {'url': row['url']})
        print(rows)


if __name__ == '__main__':
    main()
