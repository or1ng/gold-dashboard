import requests
import json
import sys
import io

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Jin10API:
    """金十数据 MCP API 客户端

    使用前请提供你自己的 API Token，申请地址：https://www.jin10.com/

    用法示例：
        api = Jin10API(token="your_token_here")
        api.initialize()
        gold = api.get_quote("XAUUSD")
    """

    def __init__(self, token=None):
        self.base_url = 'https://mcp.jin10.com/mcp'
        if not token:
            raise ValueError(
                "\n"
                "  ⚠️  未提供金十数据 API Token！\n"
                "\n"
                "  请按以下方式配置：\n"
                "    1. 申请Token: https://www.jin10.com/\n"
                "    2. 传入token参数: Jin10API(token='你的Token')\n"
                "    3. 或设置环境变量 JIN10_TOKEN\n"
                "\n"
            )
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        self.session_id = None
        self.request_id = 0

    def _get_next_id(self):
        self.request_id += 1
        return self.request_id

    def _parse_sse_response(self, response_text):
        """解析SSE格式的响应"""
        lines = response_text.strip().split('\n')
        data_lines = []
        for line in lines:
            if line.startswith('data:'):
                data_lines.append(line[5:].strip())

        if data_lines:
            full_data = ''.join(data_lines)
            try:
                return json.loads(full_data)
            except json.JSONDecodeError:
                return None
        return None

    def initialize(self):
        """初始化 MCP 会话并获取 session ID"""
        init_payload = {
            'jsonrpc': '2.0',
            'id': self._get_next_id(),
            'method': 'initialize',
            'params': {
                'protocolVersion': '2025-11-25',
                'capabilities': {},
                'clientInfo': {
                    'name': 'gold-dashboard',
                    'version': '1.0.0'
                }
            }
        }

        response = requests.post(self.base_url, json=init_payload, headers=self.headers)

        # 获取 session ID
        self.session_id = response.headers.get('Mcp-Session-Id')
        if self.session_id:
            self.headers['Mcp-Session-Id'] = self.session_id
            print(f"Session ID: {self.session_id}")

        # 发送 initialized notification
        init_notification = {
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        }
        requests.post(self.base_url, json=init_notification, headers=self.headers)

        return self.session_id is not None

    def call_tool(self, tool_name, arguments=None):
        """调用 MCP 工具"""
        if not self.session_id:
            self.initialize()

        if arguments is None:
            arguments = {}

        payload = {
            'jsonrpc': '2.0',
            'id': self._get_next_id(),
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': arguments
            }
        }

        response = requests.post(self.base_url, json=payload, headers=self.headers)
        response_text = response.content.decode('utf-8')
        return self._parse_sse_response(response_text)

    def get_quote(self, code):
        """获取指定品种实时行情"""
        result = self.call_tool('get_quote', {'code': code})
        if result and 'result' in result:
            content = result['result'].get('content', [])
            for item in content:
                if item.get('type') == 'text':
                    try:
                        data = json.loads(item.get('text', '{}'))
                        return data.get('data', {})
                    except:
                        pass
        return None

    def search_flash(self, keyword):
        """按关键词搜索快讯"""
        result = self.call_tool('search_flash', {'keyword': keyword})
        if result and 'result' in result:
            content = result['result'].get('content', [])
            for item in content:
                if item.get('type') == 'text':
                    try:
                        data = json.loads(item.get('text', '{}'))
                        return data.get('data', {})
                    except:
                        pass
        return None

    def list_calendar(self):
        """获取财经日历数据"""
        result = self.call_tool('list_calendar', {})
        if result and 'result' in result:
            content = result['result'].get('content', [])
            for item in content:
                if item.get('type') == 'text':
                    try:
                        data = json.loads(item.get('text', '{}'))
                        return data.get('data', [])
                    except:
                        pass
        return None


def main():
    api = Jin10API(token="YOUR_JIN10_TOKEN_HERE")

    print('=' * 70)
    print(' ' * 20 + '金十数据 - 黄金投资分析看板')
    print('=' * 70)

    # 初始化
    print('\n[初始化 MCP 会话...]')
    if not api.initialize():
        print('初始化失败！')
        return

    # 获取黄金价格
    print('\n' + '=' * 70)
    print('[1] 现货黄金价格 (XAUUSD)')
    print('=' * 70)
    gold = api.get_quote('XAUUSD')
    if gold:
        print(f"  品种名称: {gold.get('name', 'N/A')}")
        print(f"  最新价格: {gold.get('close', 'N/A')} USD/盎司")
        ups_price = gold.get('ups_price', 'N/A')
        ups_percent = gold.get('ups_percent', 'N/A')
        trend = "上涨" if ups_price and float(ups_price) > 0 else "下跌"
        print(f"  涨跌幅度: {ups_price} ({ups_percent}%) [{trend}]")
        print(f"  今日开盘: {gold.get('open', 'N/A')}")
        print(f"  今日最高: {gold.get('high', 'N/A')}")
        print(f"  今日最低: {gold.get('low', 'N/A')}")
        print(f"  更新时间: {gold.get('time', 'N/A')}")
    else:
        print('  获取失败')

    # 获取原油价格
    print('\n' + '=' * 70)
    print('[2] WTI 原油价格 (USOIL)')
    print('=' * 70)
    oil = api.get_quote('USOIL')
    if oil:
        print(f"  品种名称: {oil.get('name', 'N/A')}")
        print(f"  最新价格: {oil.get('close', 'N/A')} USD/桶")
        ups_price = oil.get('ups_price', 'N/A')
        ups_percent = oil.get('ups_percent', 'N/A')
        trend = "上涨" if ups_price and float(ups_price) > 0 else "下跌"
        print(f"  涨跌幅度: {ups_price} ({ups_percent}%) [{trend}]")
    else:
        print('  获取失败')

    # 获取美元指数
    print('\n' + '=' * 70)
    print('[3] 美元/日元汇率 (USDJPY)')
    print('=' * 70)
    dollar = api.get_quote('USDJPY')
    if dollar:
        print(f"  品种名称: {dollar.get('name', 'N/A')}")
        print(f"  最新价格: {dollar.get('close', 'N/A')}")
        ups_price = dollar.get('ups_price', 'N/A')
        ups_percent = dollar.get('ups_percent', 'N/A')
        trend = "上涨" if ups_price and float(ups_price) > 0 else "下跌"
        print(f"  涨跌幅度: {ups_price} ({ups_percent}%) [{trend}]")
    else:
        print('  获取失败')

    # 获取黄金相关快讯
    print('\n' + '=' * 70)
    print('[4] 黄金相关最新快讯')
    print('=' * 70)
    news = api.search_flash('黄金')
    if news and 'items' in news:
        for i, item in enumerate(news['items'][:5], 1):
            content = item.get('content', 'N/A')
            time_str = item.get('time', 'N/A')
            print(f"  {i}. [{time_str}] {content[:80]}...")
    else:
        print('  获取失败')

    # 获取财经日历
    print('\n' + '=' * 70)
    print('[5] 财经日历 (最近5条)')
    print('=' * 70)
    calendar = api.list_calendar()
    if calendar:
        for i, event in enumerate(calendar[:5], 1):
            pub_time = event.get('pub_time', 'N/A')
            title = event.get('title', 'N/A')
            star = event.get('star', 'N/A')
            previous = event.get('previous', 'N/A')
            consensus = event.get('consensus', 'N/A')
            actual = event.get('actual', 'N/A')
            affect = event.get('affect_txt', 'N/A')

            print(f"  {i}. [{pub_time}] {'★' * int(star) if star else ''} {title}")
            print(f"      前值: {previous} | 预期: {consensus} | 实际: {actual}")
            if affect:
                print(f"      影响: {affect}")
    else:
        print('  获取失败')

    print('\n' + '=' * 70)


if __name__ == '__main__':
    main()
