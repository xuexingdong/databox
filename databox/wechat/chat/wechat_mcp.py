from fastmcp import FastMCP

from databox.wechat.chat.wx_client import WeChatClient

mcp = FastMCP("WeChat MCP Service 🤖")
client = WeChatClient()


@mcp.tool()
def get_official_account_history(account_name: str, page_count: int = 1) -> dict:
    """获取指定公众号的历史消息
    Args:
        account_name: 公众号名称
        page_count: 要获取的页数
    """
    # 先搜索并进入公众号
    success = client.search_official_account(account_name)
    if not success:
        return {"success": False, "message": f"未找到公众号: {account_name}"}

    # 获取历史消息
    messages = client.get_official_account_messages(page_count)
    return {
        "success": True,
        "data": {
            "account": account_name,
            "messages": messages
        }
    }
