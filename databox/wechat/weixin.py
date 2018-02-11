import logging
import random
import re
import time
from urllib.parse import urlencode
from xml.dom import minidom

import qrcode
import requests

from databox.wechat.enums import QRCodeStatus, MsgType


class Wechat:
    logger = logging.getLogger(__name__)

    headers = {
        'Referer': 'https://wx.qq.com/'
    }

    def __init__(self, ):
        self.session = requests.session()
        # 初始化参数
        self.device_id = 'e' + repr(random.random())[2:17]
        self.redirect_uri = ''
        self.base_uri = ''
        self.skey = ''
        self.wxsid = ''
        self.wxuin = ''
        self.pass_ticket = ''
        self.base_request = None
        self.sync_key_list = []
        self.synckey = ''
        self.user = None
        self.special_users = []
        self.builtin_special_users = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage',
                                      'qmessage',
                                      'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend',
                                      'readerapp',
                                      'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp',
                                      'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder',
                                      'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts',
                                      'notification_messages',
                                      'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm',
                                      'notification_messages']

        # 好友
        self.contacts = []
        # 群组
        self.groups = []
        # 群友
        self.group_contacts = []
        # 公众账号
        self.media_platforms = []

        self.sync_host = ''

        # 登录
        status = None
        while status != QRCodeStatus.CONFIRM:
            # 生成uuid
            self.uuid = self.gen_uuid()
            status = QRCodeStatus.WAITING
            # 控制台打印二维码
            self.print_qrcode()
            # 判断用户是否扫码
            while status != QRCodeStatus.EXPIRED and status != QRCodeStatus.SUCCESS:
                status = self.get_qrcode_status()
            # 判断用户是否点击登录
            while status != QRCodeStatus.EXPIRED and status != QRCodeStatus.CONFIRM:
                status = self.get_qrcode_status(0)
        self.logger.info('登录')
        if not self.login():
            self.logger.error('登录失败')
            return
        self.logger.info('初始化')
        if not self.wxinit():
            self.logger.error('初始化失败')
            return
        self.logger.info('开启状态通知')
        if not self.webwxstatusnotify():
            self.logger.error('开启状态通知失败')
            return
        self.logger.info('获取联系人')
        if not self.webwxgetcontact():
            self.logger.error('获取联系人失败')
            return
        self.testsynccheck()

    def gen_uuid(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': 'wx782c26e4c19acffb',
            'fun': 'new',
            'lang': 'zh_CN',
            '_': int(time.time()),
        }

        text = self.session.get(url, params=params).text
        regex = 'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regex, text)
        if pm:
            code = pm.group(1)
            if code == '200':
                return pm.group(2)

    def print_qrcode(self):
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data('https://login.weixin.qq.com/l/' + self.uuid)
        qr.make()
        qr.print_ascii(invert=True)

    def get_qrcode_status(self, tip=1):
        time.sleep(tip)
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
            tip, self.uuid, int(time.time()))
        data = self.session.get(url).text
        code = re.search('window.code=(\d+);', data).group(1)
        if code == '201':
            return QRCodeStatus.SUCCESS
        elif code == '200':
            redirect_uri = re.search('window.redirect_uri="(\S+?)";', data).group(1)
            self.redirect_uri = redirect_uri + '&fun=new'
            self.base_uri = redirect_uri[:redirect_uri.rfind('/')]
            return QRCodeStatus.CONFIRM
        elif code == '408':
            return QRCodeStatus.WAITING
        elif code == '400':
            return QRCodeStatus.EXPIRED
        return None

    def login(self):
        xml = self.session.get(self.redirect_uri, headers=self.headers).text
        doc = minidom.parseString(xml)
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.sid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.uin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

        if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
            return False

        self.base_request = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.device_id,
        }
        return True

    def wxinit(self):
        url = self.base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        data = {
            'BaseRequest': self.base_request
        }
        dic = self.session.post(url, json=data).json()
        if dic['BaseResponse']['Ret'] != 0:
            return False
        self.sync_key_list = dic['SyncKey']
        self.user = dic['User']
        self.synckey = '|'.join(
            [str(kv['Key']) + '_' + str(kv['Val']) for kv in self.sync_key_list['List']])
        return True

    def webwxstatusnotify(self):
        url = self.base_uri + '/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % self.pass_ticket
        data = {
            'BaseRequest': self.base_request,
            "Code": 3,
            "FromUserName": self.user['UserName'],
            "ToUserName": self.user['UserName'],
            "ClientMsgId": int(time.time())
        }
        dic = self.session.post(url, json=data).json()
        return dic != '' and dic['BaseResponse']['Ret'] == 0

    def webwxgetcontact(self):
        url = self.base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        dic = self.session.post(url).json()
        if dic == '':
            return False

        member_list = dic['MemberList'][:]
        for member in reversed(member_list):
            # 公众号/服务号
            if member['VerifyFlag'] & 8 != 0:
                member_list.remove(member)
                self.media_platforms.append(member)
            # 特殊账号
            elif member['UserName'] in self.builtin_special_users:
                member_list.remove(member)
                self.special_users.append(member)
            # 群聊
            elif '@@' in member['UserName']:
                member_list.remove(member)
                self.group_contacts.append(member)
            # 自己
            elif member['UserName'] == self.user['UserName']:
                member_list.remove(member)
        self.contacts = member_list
        return True

    # 批量获取群内联系人
    def webwxbatchgetcontact(self):
        url = self.base_uri + '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
            int(time.time()), self.pass_ticket)
        data = {
            'BaseRequest': self.base_request,
            "Count": len(self.group_contacts),
            "List": [{"UserName": g['UserName'], "EncryChatRoomId": ""} for g in self.group_contacts]
        }
        dic = self.session.post(url, json=data).json()
        if dic == '':
            return False
        for member in reversed(dic['ContactList']):
            self.group_contacts += member['MemberList']
        return True

    def testsynccheck(self):
        sync_hosts = ['wx2.qq.com',
                      'webpush.wx2.qq.com',
                      'wx8.qq.com',
                      'webpush.wx8.qq.com',
                      'qq.com',
                      'webpush.wx.qq.com',
                      'web2.wechat.com',
                      'webpush.web2.wechat.com',
                      'wechat.com',
                      'webpush.web.wechat.com',
                      'webpush.weixin.qq.com',
                      'webpush.wechat.com',
                      'webpush1.wechat.com',
                      'webpush2.wechat.com',
                      'webpush.wx.qq.com',
                      'webpush2.wx.qq.com']
        for host in sync_hosts:
            self.sync_host = host
            retcode, _ = self.synccheck()
            if retcode == '0':
                return True
        return False

    def synccheck(self):
        params = {
            'r': int(time.time()),
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'deviceid': self.device_id,
            'synckey': self.synckey,
            '_': int(time.time()),
        }
        url = 'https://' + self.sync_host + '/cgi-bin/mmwebwx-bin/synccheck?' + urlencode(params)
        data = self.session.get(url, headers=self.headers).text
        if data == '':
            return [-1, -1]

        m = re.search('window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
        return m.group(1), m.group(2)

    def webwxsync(self):
        url = self.base_uri + '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
            self.sid, self.skey, self.pass_ticket)
        data = {
            'BaseRequest': self.base_request,
            'SyncKey': self.sync_key_list,
            'rr': ~int(time.time())
        }
        msg = self.session.post(url, json=data).json()
        self.handle(msg)

    def get_sync_url(self):
        return self.base_uri + '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
            self.sid, self.skey, self.pass_ticket)

    def get_name(self, openid):
        name = '未知群' if openid[:2] == '@@' else '陌生人'
        # 自己
        if openid == self.user['UserName']:
            return self.user['NickName']
        if openid[:2] == '@@':
            name = self.get_group_name(openid)
        else:
            # 特殊账号
            for member in self.special_users:
                if member['UserName'] == openid:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']

            # 公众号或服务号
            for member in self.media_platforms:
                if member['UserName'] == openid:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']

            # 直接联系人
            for member in self.contacts:
                if member['UserName'] == openid:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']
            # 群友
            for member in self.group_contacts:
                if member['UserName'] == openid:
                    name = member['DisplayName'] if member[
                        'DisplayName'] else member['NickName']

        if name == '未知群' or name == '陌生人':
            self.logger.debug(openid)
        return name

    def get_group_name(self, openid):
        name = '未知群'
        for member in self.groups:
            if member['UserName'] == openid:
                name = member['NickName']
        if name == '未知群':
            # 现有群里面查不到
            groups = self.get_name_by_request(openid)
            for group in groups:
                self.groups.append(group)
                if group['UserName'] == openid:
                    name = group['NickName']
                    self.group_contacts += group['MemberList']
        return name

    def get_name_by_request(self, openid):
        url = self.base_uri + \
              '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
                  int(time.time()), self.pass_ticket)
        data = {
            'BaseRequest': self.base_request,
            "Count": 1,
            "List": [{"UserName": openid, "EncryChatRoomId": ""}]
        }
        return self.session.post(url, json=data).json()['ContactList']

    def handle(self, msg):
        if msg['BaseResponse']['Ret'] != 0:
            return
        self.sync_key_list = msg['SyncKey']
        self.synckey = '|'.join(
            [str(kv['Key']) + '_' + str(kv['Val']) for kv in self.sync_key_list['List']])

        # 追加的消息
        for msg in msg['AddMsgList']:
            self.logger.debug('你有新的消息，请注意查收')
            msg_type = int(msg['MsgType'])
            name = self.get_name(msg['FromUserName'])
            content = msg['Content'].replace('&lt;', '<').replace('&gt;', '>')
            msgid = msg['MsgId']
            if msg_type == MsgType.TEXT:
                raw_msg = {'raw_msg': msg}
                self._showMsg(raw_msg)
            # elif msg_type == MsgType.PICTURE:
            #     image = self.webwxgetmsgimg(msgid)
            #     raw_msg = {'raw_msg': msg,
            #                'message': '%s 发送了一张图片: %s' % (name, image)}
            #     self._showMsg(raw_msg)
            #     self._safe_open(image)
            # elif msg_type == MsgType.VOICE:
            #     voice = self.webwxgetvoice(msgid)
            #     raw_msg = {'raw_msg': msg,
            #                'message': '%s 发了一段语音: %s' % (name, voice)}
            #     self._showMsg(raw_msg)
            #     self._safe_open(voice)
            # elif msg_type == MsgType.CARD:
            #     info = msg['RecommendInfo']
            #     print('%s 发送了一张名片:' % name)
            #     print('=========================')
            #     print('= 昵称: %s' % info['NickName'])
            #     print('= 微信号: %s' % info['Alias'])
            #     print('= 地区: %s %s' % (info['Province'], info['City']))
            #     print('= 性别: %s' % ['未知', '男', '女'][info['Sex']])
            #     print('=========================')
            #     raw_msg = {'raw_msg': msg, 'message': '%s 发送了一张名片: %s' % (
            #         name.strip(), json.dumps(info))}
            #     self._showMsg(raw_msg)
            # elif msg_type == MsgType.EMOTION:
            #     url = self._searchContent('cdnurl', content)
            #     raw_msg = {'raw_msg': msg,
            #                'message': '%s 发了一个动画表情，点击下面链接查看: %s' % (name, url)}
            #     self._showMsg(raw_msg)
            #     self._safe_open(url)
            # elif msg_type == MsgType.LINK:
            #     appMsgType = defaultdict(lambda: "")
            #     appMsgType.update({5: '链接', 3: '音乐', 7: '微博'})
            #     print('%s 分享了一个%s:' % (name, appMsgType[msg['AppMsgType']]))
            #     print('=========================')
            #     print('= 标题: %s' % msg['FileName'])
            #     print('= 描述: %s' % self._searchContent('des', content, 'xml'))
            #     print('= 链接: %s' % msg['Url'])
            #     print('= 来自: %s' % self._searchContent('appname', content, 'xml'))
            #     print('=========================')
            #     card = {
            #         'title': msg['FileName'],
            #         'description': self._searchContent('des', content, 'xml'),
            #         'url': msg['Url'],
            #         'appname': self._searchContent('appname', content, 'xml')
            #     }
            #     raw_msg = {'raw_msg': msg, 'message': '%s 分享了一个%s: %s' % (
            #         name, appMsgType[msg['AppMsgType']], json.dumps(card))}
            #     self._showMsg(raw_msg)
            # elif msgType == 51:
            #     raw_msg = {'raw_msg': msg, 'message': '[*] 成功获取联系人信息'}
            #     self._showMsg(raw_msg)
            # elif msgType == 62:
            #     video = self.webwxgetvideo(msgid)
            #     raw_msg = {'raw_msg': msg,
            #                'message': '%s 发了一段小视频: %s' % (name, video)}
            #     self._showMsg(raw_msg)
            #     self._safe_open(video)
            # elif msgType == 10002:
            #     raw_msg = {'raw_msg': msg, 'message': '%s 撤回了一条消息' % name}
            #     self._showMsg(raw_msg)
            # else:
            #     logging.debug('[*] 该消息类型为: %d，可能是表情，图片, 链接或红包: %s' %
            #                   (msg['MsgType'], json.dumps(msg)))
            #     raw_msg = {
            #         'raw_msg': msg, 'message': '[*] 该消息类型为: %d，可能是表情，图片, 链接或红包' % msg['MsgType']}
            #     self._showMsg(raw_msg)
