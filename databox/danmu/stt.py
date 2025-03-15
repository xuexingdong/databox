class DumpsError(Exception):
    pass


def _escape_string(s):
    s = s.replace("@", "@A")
    s = s.replace('/', '@S')
    return s


def _unescape_string(s):
    s = s.replace("@A", "@")
    s = s.replace('@S', '/')
    return s


def dumps(data) -> str:
    if isinstance(data, dict):
        # 递归处理字典
        return '/'.join([f"{dumps(k)}@={dumps(v)}" for k, v in data.items()]) + '/'
    elif isinstance(data, list):
        # 递归处理列表
        return '/'.join([dumps(i) for i in data]) + '/'
    elif isinstance(data, str):
        # 处理字符串
        return _escape_string(data)
    else:
        return _escape_string(str(data))


def loads(data) -> dict:
    if '/' in data:
        datas = filter(None, data.split('/'))  # 去除空字符串
        decoded_items = []
        d = {}
        for item in datas:
            decoded_item = loads(item)  # 递归解析
            if isinstance(decoded_item, dict):
                d.update(decoded_item)  # 更新字典
            else:
                decoded_items.append(decoded_item)  # 加入列表
        return d if d else decoded_items
    elif '@=' in data:
        # 处理键值对
        k, v = data.split('@=')
        return {loads(k): loads(v)}
    else:
        # 处理字符串
        return _unescape_string(data)
