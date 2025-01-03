import random
import struct

import arrow
import httpx
from playwright.async_api import async_playwright

from databox.danmu import stt
from databox.danmu.danmu_client import DanmuClient
from databox.danmu.model import TypeEnum, LoginRes, Chatmsg


class DouyuDanmuClient(DanmuClient):

    async def _get_danmu_url(self):
        async with async_playwright() as playwright:
            args = ['--disable-web-security', '--disable-extensions', '--start-maximized']
            browser = await playwright.chromium.launch(headless=True, args=args)
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            context = await browser.new_context(no_viewport=True, user_agent=user_agent)
            await context.add_init_script("""
                                if (window.chrome && window.chrome.runtime) {
                                    window.chrome.runtime = {};
                                }
                                """)
            await context.route("**/*.{png,jpg,jpeg,webp,gif,mp4,css}", lambda route: route.abort())
            page = await context.new_page()
            await page.goto(f'https://www.douyu.com/{self.room_id}')
            await page.wait_for_load_state('load')
            await page.wait_for_function('window.socketProxy?.socket?.BS?.socket?.serverInfo')
            bs_server_info = await page.evaluate('window.socketProxy?.socket?.BS?.socket?.serverInfo')
            await browser.close()
            danmu_proxy_url = f"wss://{bs_server_info['host']}:{bs_server_info['port']}/"
            return danmu_proxy_url

    async def _login(self):
        login_data = {
            "type": "loginreq",
            "roomid": self.room_id,
            "time": arrow.utcnow().timestamp()
        }
        await self.ws.send_bytes(self._encode(login_data))
        await self.ws.receive_bytes()
        group_data = {
            "type": "joingroup",
            "rid": self.room_id,
            "gid": '-9999',
            "time": arrow.utcnow().timestamp()
        }
        await self.ws.send_bytes(self._encode(group_data))

    @staticmethod
    def _build_heartbeat_packet():
        return DouyuDanmuClient._encode({
            'type': 'mrkl'
        })

    @staticmethod
    def _next_frame_len(buffer) -> (int, int):
        data_len, = struct.unpack('<I', buffer[:4])
        return data_len + 4

    @staticmethod
    def _frame_to_msg(frame):
        return frame[12:-1].decode()

    @staticmethod
    def _parse_msg(msg):
        msg_dict = DouyuDanmuClient._decode(msg)
        match msg_dict.get('type'):
            case TypeEnum.loginres.value:
                login_res = LoginRes(**msg_dict)
                print(msg_dict)
            case TypeEnum.chatmsg.value:
                print(msg_dict)
                chatmsg = Chatmsg(**msg_dict)
            case TypeEnum.mrkl.value:
                pass
            case _:
                pass

    @staticmethod
    async def _get_wss_url(room_id):
        url = f'https://www.douyu.com/lapi/live/gateway/web/{room_id}?isH5=1'
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            data = response.json()
            wss_list = data['data']['wss']
            wss = random.choice(wss_list)
            return f"wss://{wss['domain']}:{wss['port']}/"

    @staticmethod
    def _encode(data_dict):
        data_str = stt.dumps(data_dict)
        data_len = len(data_str) + 9
        msg_byte = data_str.encode()
        header = struct.pack('<2IH2B', data_len, data_len, 689, 0, 0)
        data = header + msg_byte + b'\x00'
        return data

    @staticmethod
    def _decode(msg):
        return stt.loads(msg)
