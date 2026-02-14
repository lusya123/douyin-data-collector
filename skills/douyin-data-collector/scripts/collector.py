#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音数据采集脚本 v2.0
功能：采集抖音账号粉丝数据并写入飞书表格
策略：优先使用实时接口，降级到历史接口
"""

import json
import os
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path


class DouyinDataCollector:
    """抖音数据采集器"""

    def __init__(self, config_path=None):
        """初始化采集器"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"

        self.config = self.load_config(config_path)
        self.feishu_token = None

    def load_config(self, config_path):
        """加载配置文件，敏感信息优先从环境变量读取"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ 错误：配置文件不存在: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 错误：配置文件格式错误: {e}")
            sys.exit(1)

        # 从环境变量覆盖敏感配置
        if os.environ.get('TIKHUB_API_KEY'):
            config['tikhub']['api_key'] = os.environ['TIKHUB_API_KEY']
        if os.environ.get('FEISHU_APP_ID'):
            config['feishu']['app_id'] = os.environ['FEISHU_APP_ID']
        if os.environ.get('FEISHU_APP_SECRET'):
            config['feishu']['app_secret'] = os.environ['FEISHU_APP_SECRET']
        if os.environ.get('DOUYIN_SEC_USER_ID'):
            config['douyin']['sec_user_id'] = os.environ['DOUYIN_SEC_USER_ID']
        if os.environ.get('DOUYIN_KOL_ID'):
            config['douyin']['kol_id'] = os.environ['DOUYIN_KOL_ID']

        self._validate_config(config)
        return config

    def _validate_config(self, config):
        """验证配置是否完整"""
        errors = []

        api_key = config.get('tikhub', {}).get('api_key', '')
        if not api_key or api_key == 'YOUR_TIKHUB_API_KEY':
            errors.append("缺少 TikHub API Key")

        app_id = config.get('feishu', {}).get('app_id', '')
        if not app_id or app_id == 'YOUR_FEISHU_APP_ID':
            errors.append("缺少飞书 App ID")

        app_secret = config.get('feishu', {}).get('app_secret', '')
        if not app_secret or app_secret == 'YOUR_FEISHU_APP_SECRET':
            errors.append("缺少飞书 App Secret")

        sec_user_id = config.get('douyin', {}).get('sec_user_id', '')
        if not sec_user_id:
            errors.append("缺少抖音 sec_user_id")

        if errors:
            print("❌ 配置错误：")
            for err in errors:
                print(f"   - {err}")
            sys.exit(1)

    def get_feishu_tenant_token(self):
        """获取飞书 tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.config['feishu']['app_id'],
            "app_secret": self.config['feishu']['app_secret']
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 0:
                self.feishu_token = data['tenant_access_token']
                return self.feishu_token
            else:
                print(f"❌ 获取飞书 token 失败: {data.get('msg')}")
                return None
        except Exception as e:
            print(f"❌ 获取飞书 token 异常: {e}")
            return None

    def fetch_realtime_data(self):
        """
        获取实时粉丝数据（优先使用，支持多个备选接口）

        Returns:
            dict: {
                'date': '2026-02-14',  # 采集日期（今天）
                'fans_count': 16133,    # 当前粉丝总数
                'source': 'realtime'    # 数据来源
            }
        """
        # 支持单个 URL 或 URL 列表
        api_urls = self.config['tikhub'].get('realtime_api_urls', [])
        if not api_urls:
            # 兼容旧配置：如果没有 realtime_api_urls，使用 realtime_api_url
            api_url = self.config['tikhub'].get('realtime_api_url')
            if api_url:
                api_urls = [api_url]
            else:
                print("❌ 配置错误：缺少实时接口地址")
                return None

        params = {'sec_user_id': self.config['douyin']['sec_user_id']}
        headers = {
            'Authorization': f"Bearer {self.config['tikhub']['api_key']}",
            'accept': 'application/json'
        }

        # 尝试所有实时接口
        for idx, url in enumerate(api_urls):
            try:
                api_name = f"实时接口-{idx + 1}" if len(api_urls) > 1 else "实时接口"
                print(f"🔍 正在使用{api_name}获取数据...")

                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get('code') == 200 and 'data' in data:
                    user = data['data'].get('user', {})
                    fans_count = user.get('follower_count')

                    if fans_count is not None:
                        # 实时接口返回的是当前数据，日期为今天
                        today = datetime.now().strftime('%Y-%m-%d')
                        api_time = data.get('time', 'N/A')

                        print(f"✅ {api_name}请求成功")
                        print(f"   API 时间: {api_time}")
                        print(f"   当前粉丝数: {fans_count:,}")

                        return {
                            'date': today,
                            'fans_count': fans_count,
                            'source': 'realtime',
                            'api_time': api_time
                        }
                    else:
                        print(f"⚠️  {api_name}返回数据格式异常")
                        if idx < len(api_urls) - 1:
                            print(f"🔄 尝试备选接口...")
                            continue
                        return None
                else:
                    print(f"⚠️  {api_name}返回错误: {data.get('message', 'Unknown error')}")
                    if idx < len(api_urls) - 1:
                        print(f"🔄 尝试备选接口...")
                        continue
                    return None

            except requests.exceptions.Timeout:
                print(f"⚠️  {api_name}请求超时")
                if idx < len(api_urls) - 1:
                    print(f"🔄 尝试备选接口...")
                    continue
            except Exception as e:
                print(f"⚠️  {api_name}异常: {e}")
                if idx < len(api_urls) - 1:
                    print(f"🔄 尝试备选接口...")
                    continue

        print(f"❌ 所有实时接口均请求失败")
        return None

    def fetch_history_data(self, start_date, end_date):
        """
        获取历史粉丝数据（备用）

        Returns:
            dict: {
                'date': '2026-02-13',   # API 返回的数据日期
                'fans_count': 16100,    # 该日期的粉丝总数
                'fans_delta': 50,       # 该日期的粉丝净增
                'source': 'history'     # 数据来源
            }
        """
        api_urls = self.config['tikhub'].get('history_api_urls', [])
        if not api_urls:
            print("❌ 配置错误：缺少历史接口地址")
            return None

        params = {
            'kolId': self.config['douyin'].get('kol_id', ''),
            'startDate': start_date,
            'endDate': end_date
        }
        headers = {
            'Authorization': f"Bearer {self.config['tikhub']['api_key']}",
            'accept': 'application/json'
        }

        for idx, url in enumerate(api_urls):
            try:
                api_name = f"历史接口-{idx + 1}" if len(api_urls) > 1 else "历史接口"
                print(f"🔍 正在使用{api_name}获取 {start_date} 至 {end_date} 的数据...")

                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get('data') and \
                   data['data'].get('daily') and len(data['data']['daily']) > 0:

                    daily_list = sorted(data['data']['daily'],
                                      key=lambda x: x['date'], reverse=True)
                    delta_list = sorted(data['data'].get('delta', []),
                                      key=lambda x: x['date'], reverse=True)

                    latest_daily = daily_list[0]
                    latest_delta = next((d for d in delta_list if d['date'] == latest_daily['date']), None)

                    print(f"✅ {api_name}请求成功")
                    print(f"   数据日期: {latest_daily['date']}")
                    print(f"   粉丝总数: {latest_daily['fans_cnt']:,}")

                    return {
                        'date': latest_daily['date'],
                        'fans_count': latest_daily['fans_cnt'],
                        'fans_delta': latest_delta['fans_cnt'] if latest_delta else 0,
                        'source': 'history'
                    }
                else:
                    print(f"⚠️  {api_name}返回数据为空")
                    if idx < len(api_urls) - 1:
                        print(f"🔄 尝试备选接口...")
                        continue
                    return None

            except Exception as e:
                print(f"⚠️  {api_name}异常: {e}")
                if idx < len(api_urls) - 1:
                    print(f"🔄 尝试备选接口...")
                    continue

        return None

    def get_previous_day_fans(self, date_str):
        """
        从飞书表格查询前一天的粉丝数

        Args:
            date_str: 当前日期，格式 YYYY-MM-DD

        Returns:
            int: 前一天的粉丝数，如果查询失败返回 None
        """
        if not self.feishu_token:
            return None

        # 计算前一天日期
        current_date = datetime.strptime(date_str, '%Y-%m-%d')
        previous_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.config['feishu']['app_token']}/tables/{self.config['feishu']['table_id']}/records/search"

        headers = {
            'Authorization': f'Bearer {self.feishu_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "filter": {
                "conjunction": "and",
                "conditions": [{
                    "field_name": "统计日期文本",
                    "operator": "is",
                    "value": [previous_date]
                }]
            },
            "automatic_fields": False
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 0:
                items = data.get('data', {}).get('items', [])
                if items:
                    previous_fans = items[0].get('fields', {}).get('抖音粉丝数')
                    if previous_fans is not None:
                        print(f"   前一天 ({previous_date}) 粉丝数: {previous_fans:,}")
                        return int(previous_fans)

            print(f"   未找到前一天 ({previous_date}) 的数据")
            return None

        except Exception as e:
            print(f"   查询前一天数据异常: {e}")
            return None

    def check_record_exists(self, date_str):
        """检查飞书表格中是否已存在该日期的记录"""
        if not self.feishu_token:
            return False

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.config['feishu']['app_token']}/tables/{self.config['feishu']['table_id']}/records/search"

        headers = {
            'Authorization': f'Bearer {self.feishu_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "filter": {
                "conjunction": "and",
                "conditions": [{
                    "field_name": "统计日期文本",
                    "operator": "is",
                    "value": [date_str]
                }]
            },
            "automatic_fields": False
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 0:
                items = data.get('data', {}).get('items', [])
                return len(items) > 0

        except Exception as e:
            print(f"❌ 查询记录异常: {e}")
            return False

        return False

    def write_to_feishu(self, data):
        """将数据写入飞书表格"""
        if not self.feishu_token:
            print("❌ 飞书 token 未获取，无法写入数据")
            return False

        if self.check_record_exists(data['date']):
            print(f"⚠️  {data['date']} 的记录已存在，跳过写入")
            return True

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.config['feishu']['app_token']}/tables/{self.config['feishu']['table_id']}/records"

        headers = {
            'Authorization': f'Bearer {self.feishu_token}',
            'Content-Type': 'application/json'
        }

        date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        timestamp = int(date_obj.timestamp() * 1000)

        payload = {
            "fields": {
                "抖音粉丝数": int(data['fans_count']),
                "抖音净新增": int(data['fans_delta']),
                "统计日期": timestamp
            }
        }

        try:
            print(f"📝 正在写入飞书表格...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == 0:
                print(f"✅ 数据写入成功！")
                return True
            else:
                print(f"❌ 数据写入失败: {result.get('msg')}")
                return False

        except Exception as e:
            print(f"❌ 写入数据异常: {e}")
            return False

    def send_feishu_message(self, data):
        """发送飞书消息通知"""
        if not self.feishu_token:
            return

        url = "https://open.feishu.cn/open-apis/im/v1/messages"

        headers = {
            'Authorization': f'Bearer {self.feishu_token}',
            'Content-Type': 'application/json'
        }

        message_text = f"{data['date']}数据为,粉丝新增{data['fans_delta']},抖音总粉丝数{data['fans_count']}"

        payload = {
            "receive_id": self.config['feishu']['chat_id'],
            "msg_type": "text",
            "content": json.dumps({"text": message_text})
        }

        params = {
            "receive_id_type": "chat_id"
        }

        try:
            print(f"📨 正在发送飞书通知...")
            response = requests.post(url, json=payload, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == 0:
                print(f"✅ 通知发送成功！")
            else:
                print(f"⚠️  通知发送失败: {result.get('msg')}")

        except Exception as e:
            print(f"⚠️  发送通知异常: {e}")

    def collect(self, target_date=None):
        """
        采集数据（新策略）

        策略：
        1. 优先使用实时接口获取当前粉丝数
        2. 从飞书查询前一天的粉丝数，计算净增
        3. 如果实时接口失败，降级到历史接口

        Args:
            target_date: 目标日期（可选），默认为今天
        """
        if not self.get_feishu_tenant_token():
            return {
                'success': False,
                'message': '获取飞书 token 失败'
            }

        # 确定目标日期（默认为今天）
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')

        print(f"🎯 目标采集日期: {target_date}")

        # 策略1: 尝试实时接口
        realtime_data = self.fetch_realtime_data()

        if realtime_data:
            # 实时接口成功，计算净增
            print(f"\n📊 计算粉丝净增...")
            previous_fans = self.get_previous_day_fans(realtime_data['date'])

            if previous_fans is not None:
                fans_delta = realtime_data['fans_count'] - previous_fans
                print(f"   净增: {fans_delta:+,}")
            else:
                fans_delta = 0
                print(f"   无法计算净增（前一天数据不存在），设为 0")

            final_data = {
                'date': realtime_data['date'],
                'fans_count': realtime_data['fans_count'],
                'fans_delta': fans_delta,
                'source': 'realtime'
            }

            write_success = self.write_to_feishu(final_data)

            if write_success:
                self.send_feishu_message(final_data)
                return {
                    'success': True,
                    'data': final_data,
                    'message': f'成功采集并写入 {final_data["date"]} 的数据（实时接口）'
                }
            else:
                return {
                    'success': False,
                    'message': '数据写入失败'
                }

        # 策略2: 实时接口失败，降级到历史接口
        print(f"\n🔄 实时接口失败，尝试历史接口...")

        # 历史接口通常返回 T-1 的数据
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        history_data = self.fetch_history_data(start_date, end_date)

        if history_data:
            write_success = self.write_to_feishu(history_data)

            if write_success:
                self.send_feishu_message(history_data)
                return {
                    'success': True,
                    'data': history_data,
                    'message': f'成功采集并写入 {history_data["date"]} 的数据（历史接口）'
                }
            else:
                return {
                    'success': False,
                    'message': '数据写入失败'
                }

        return {
            'success': False,
            'message': '所有接口均失败'
        }


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 抖音数据采集程序启动 v2.0")
    print("=" * 50)

    collector = DouyinDataCollector()
    result = collector.collect()

    print("\n" + "=" * 50)
    if result['success']:
        print("✅ 采集成功！")
        data = result['data']
        print(f"📅 统计日期: {data['date']}")
        print(f"👥 粉丝总数: {int(data['fans_count']):,}")
        print(f"📈 粉丝净增: {int(data['fans_delta']):+,}")
        print(f"🔍 数据来源: {data['source']}")
    else:
        print(f"❌ 采集失败: {result['message']}")
    print("=" * 50)

    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
