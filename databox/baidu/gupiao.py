import arrow
import requests

GUPIAO_HOST = 'https://gupiao.baidu.com'
URL_GET_DAY_INFO = GUPIAO_HOST + '/api/stocks/stockdaybar'
# 最早
EARLEST = -1
# 小数精度
PRECISION = 2


def get_day_info_by_code(code, start=None, end=None, fq_type=1):
    """
    根据股票代码查询每日信息，返回信息解释如下
    date: 20170516 日期
    open: 15.270000457764 开盘价
    high: 15.430000305176 最高价
    low: 15.159999847412, 最低价
    close: 15.210000038147, 收盘价
    volume: 18552953 成交量
    netChangeRatio: 1.3943111523986 涨跌幅
    :param code: 股票代码
    :param start: 开始日期，YYYYMMDD格式
    :param end: 开始日期，YYYYMMDD格式
    :param fq_type: 是否使用前复权指标，默认使用
    :return: generator，每个元素是个字典
    """
    if not start:
        start = arrow.now().format('YYYYMMDD')
    if start == EARLEST:
        start = arrow.get(0).format('YYYYMMDD')
        print(start)
    if not end:
        end = arrow.now().format('YYYYMMDD')
    params = {
        'from': 'pc',
        'os_ver': 1,
        'cuid': 'xxx',
        'vv': '100',
        'format': 'json',
        'stock_code': 'sh' + code,
        'step': 3,
        'start': end,
        'count': 160,
        'fq_type': 'front' if fq_type else 'no'
    }
    # 停止标志
    stop = 0
    while not stop:
        params['start'] = end
        res = requests.get(URL_GET_DAY_INFO, params=params).json()
        # 无数据返回
        if 'mashData' not in res:
            stop = 1
        else:
            data = res['mashData']
            if len(data) < 160:
                stop = 1
            for day_info in data:
                end = day_info['date']
                # 日期超出范围
                if day_info['date'] < int(start):
                    stop = 1
                    break
                return_dict = {
                    'date': day_info['date'],
                    'open': round(day_info['kline']['open'], PRECISION),
                    'high': round(day_info['kline']['high'], PRECISION),
                    'low': round(day_info['kline']['low'], PRECISION),
                    'close': round(day_info['kline']['close'], PRECISION),
                    'volume': day_info['kline']['volume'],
                    'netChangeRatio': round(day_info['kline']['netChangeRatio'], PRECISION)}
                yield return_dict
