import arrow

from databox.wechat.game import constants


def get_game_group_list_url(session_id):
    return constants.PREFIX + '/cgi-bin/groupwap/getweappgrouplistindex?session_id=' + session_id


def get_game_group_url(session_id):
    return constants.PREFIX + '/cgi-bin/groupwap/getgamegroup?session_id=' + session_id


def get_game_group_url_data(appid, count=15, offset=0):
    return {
        "base":                {
            "appid": appid
        },
        "page_list":           [{
            "count":       count,
            "my_offset":   offset,
            "sort_weight": 0,
            "offset":      0,
            "type":        1
        }],
        "need_extra_topics":   False,
        "need_viewed_history": True
    }


def get_topic_url(session_id):
    return constants.PREFIX + '/cgi-bin/groupwap/getgamereplylist?session_id' + session_id


def get_topic_url_data(appid, topic_id):
    return {
        "topic_id":        topic_id,
        "need_topic":      1,
        "need_guide_info": True,
        "view_add":        True,
        "base":            {
            "appid":          appid,
            "client_version": 0,
            "role":           1,
            "source_type":    2
        },
        "child_reply_id":  "",
        "page_info":       {
            "type":      3,
            "offset":    0,
            "count":     10,
            "my_offset": 0
        },
        "type":            0,
        "view_scene":      2
    }


def get_game_reply_list_url(session_id):
    return constants.PREFIX + '/cgi-bin/groupwap/getgamereplylist?session_id=' + session_id


def get_reply_url_data(appid, topic_id, parent_reply_id=None, count=10, offset=0):
    data = {
        "topic_id":        topic_id,
        "need_topic":      0,
        "need_guide_info": False,
        "view_add":        False,
        "base":            {
            "appid":          appid,
            "client_version": 0,
            "role":           1,
            "source_type":    2
        },
        "child_reply_id":  "",
        "page_info":       {
            "type":      3,
            "offset":    offset,
            "count":     count,
            "my_offset": 0
        },
        "type":            0,
        "view_scene":      2,
    }
    if parent_reply_id:
        data.update({
            'parent_reply_id': parent_reply_id
        })
    else:
        data.update({
            'back': False
        })
    return data


def is_timestamp_outdated(ts):
    return ts + 24 * 60 * 60 < arrow.now().timestamp
