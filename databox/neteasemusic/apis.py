def get_user_url(id: int) -> str:
    return 'http://music.163.com/user/home?id=' + str(id)


def get_comment_url(song_id: str, limit: int = 10, offset: int = 0) -> str:
    return 'http://music.163.com/api/v1/resource/comments/R_SO_4_%s&limit=%d&offset=%d' % (song_id, limit, offset)


def get_follows_url(id: int) -> str:
    return 'http://music.163.com/weapi/user/getfollows/' + str(id)


def get_followeds_url(id: int) -> str:
    return 'http://music.163.com/weapi/user/getfolloweds/' + str(id)
