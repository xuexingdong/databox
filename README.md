## 关于该项目

- 自娱自乐，无证书，想用就拿走吧。
- 有爬取需求可以提issue，有空会去踩坑（如果涉及到一些需要登录的冷门网站，请自行提供测试账号）。
- 欢迎pr，采用git-flow推荐的命名方式。
- 任何对代码的建议都欢迎提出。

## 更新列表

1. 2017.05.13 掘金网站-标签搜索
2. 2017.05.15 百度-带验证码登录（接口登录，非浏览器模拟）
3. 2017.05.16 百度股票每日指标爬取
4. 2017.06.13 谷歌翻译爬取

- baidu

登录错误码大全：http://www.mamicode.com/info-detail-1088804.html

## 依赖

- zbar

```text
sudo yum install zbar zbar-devel

```

qq

```shell
mitmproxy --mode upstream:http://127.0.0.1:7890 -p 8000 -s mitmproxy_script.py```