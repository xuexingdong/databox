import time

import uiautomation as auto
from uiautomation import Control


class WeChatClient:
    def __init__(self):
        self.wechat_window = auto.WindowControl(searchDepth=1, Name='微信')
        self.wechat_window.SetActive()
        # 获取主布局容器
        main_layout = [i for i in self.wechat_window.GetChildren() if not i.ClassName][0]
        content_layout = main_layout.GetFirstChildControl()
        # 获取三个主要区域
        self.tool_bar = content_layout.GetChildren()[0]  # 左侧工具栏
        self.chat_list = content_layout.GetChildren()[1]  # 中间聊天列表
        self.chat_content = content_layout.GetChildren()[2]

        self.search_bar = self.chat_content.EditControl(Name="搜索")
        self.chat_dict = self.get_chat_dict()

    def get_chat_dict(self) -> dict[str, Control]:
        return {chat.TextControl().Name: chat for chat in
                self.chat_list.ListControl(Name='会话').GetChildren()}

    def send_msg(self, msg: str, to: str, at_users: str | list[str] = None, exact_match: bool = False,
                 typing: bool = False) -> None:
        if to in self.chat_dict:
            self.chat_dict[to].Click(simulateMove=False)
            edit_box = self.chat_content.EditControl(Name=to)
            if typing:
                # 使用打字模式
                self.send_typing_text(msg)
            else:
                # 使用剪贴板模式
                auto.SetClipboardText(msg)
                edit_box.SendKeys('{Ctrl}v')
            edit_box.SendKeys('{Enter}')

    def click_moments(self):
        """点击朋友圈按钮"""
        if not self.wechat_window:
            return False

        moments_button = self.wechat_window.ButtonControl(searchDepth=5, Name='朋友圈')
        if moments_button.Exists():
            moments_button.Click()
            print("已点击朋友圈按钮")
            time.sleep(2)
            return True
        print("朋友圈按钮未找到")
        return False

    def scroll_and_parse_moments(self, scroll_times=5):
        """滚动并解析朋友圈内容"""
        if not self.wechat_window:
            return []

        moments_scroll = self.wechat_window.PaneControl(searchDepth=5, AutomationId='moments_scroll')
        if not moments_scroll.Exists():
            print("朋友圈滚动区域未找到")
            return []

        posts_content = []
        for _ in range(scroll_times):
            posts = moments_scroll.GetChildren()
            for post in posts:
                text_controls = post.GetChildren()
                for text_control in text_controls:
                    if isinstance(text_control, auto.TextControl):
                        posts_content.append(text_control.Name)

            moments_scroll.Swipe(auto.SwipeDirection.Up, 1, 1)
            time.sleep(1)

        return posts_content

    def search_official_account(self, account_name):
        """搜索公众号"""
        if not self.wechat_window:
            return False

        search_edit = self.wechat_window.EditControl(
            ControlType=auto.EditControl.ControlType,
            Name=""
        )

        if search_edit.Exists(3):
            search_edit.Click()
            search_edit.SendKeys(account_name)
            time.sleep(1)
            search_edit.SendKeys("{Enter}")
            return True

        print("未找到搜索框")
        return False

    def init_search(self):
        """点击搜索框并选择搜索网络结果"""
        if not self.wechat_window:
            return False
        self.search_bar.Click(simulateMove=False)
        self.wechat_window.ListItemControl(Name="搜索网络结果").Click(simulateMove=False)
        self.wechat_window.DocumentControl(Name="搜一搜")
        self.wechat_window.EditControl().SendKeys("")

    def send_typing_text(self, text: str, min_interval: float = 0.1, max_interval: float = 0.3) -> bool:
        """模拟人工输入文本
        Args:
            text: 要输入的文本
            min_interval: 最小输入间隔时间（秒）
            max_interval: 最大输入间隔时间（秒）
        """
        import random

        edit_box = self.wechat_window.EditControl(Name="输入")
        if not edit_box.Exists(3):
            return False

        edit_box.Click(simulateMove=False)

        for char in text:
            edit_box.SendKeys(char, waitTime=0)  # waitTime=0 避免内部延迟
            # 随机等待时间，模拟真实输入
            time.sleep(random.uniform(min_interval, max_interval))

        return True


def main():
    client = WeChatClient()
    if client.wechat_window:
        # 示例：浏览朋友圈
        if client.click_moments():
            posts = client.scroll_and_parse_moments(scroll_times=5)
            for post in posts:
                print(post)

        # 示例：搜索公众号
        client.search_official_account("测试公众号")
