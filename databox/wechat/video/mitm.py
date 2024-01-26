from mitmproxy import http
from mitmproxy.tools.main import mitmdump


class UpstreamProxy:
    def __init__(self):
        with open("inject.js", "r") as file:
            self.custom_script = file.read()

    def response(self, flow: http.HTTPFlow) -> None:
        if ('channels.weixin.qq.com' in flow.request.pretty_url
                and "Content-Type" in flow.response.headers
                and "text/html" in flow.response.headers["Content-Type"]):
            print('注入成功')
            flow.response.text = flow.response.text.replace(
                '</head>',
                f'<script>{self.custom_script}</script></head>',
                1
            )


if __name__ == "__main__":
    addons = [
        UpstreamProxy()
    ]
    # 配置 mitmproxy 的选项
    # 服务发布时不使用代理的话，直接使用下面这行
    mitmdump(['-s', __file__])
    # mitmdump(['-s', __file__, '--mode', 'upstream:localhost:33210'])
