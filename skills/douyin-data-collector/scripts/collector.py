#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音数据采集脚本
功能：采集抖音账号粉丝数据并写入飞书表格
支持从环境变量或配置文件读取敏感信息
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
        """
        加载配置文件，敏感信息优先从环境变量读取

        环境变量优先级高于配置文件：
        - TIKHUB_API_KEY: TikHub API 密钥
        - FEISHU_APP_ID: 飞书应用 ID
        - FEISHU_APP_SECRET: 飞书应用密钥
        - DOUYIN_KOL_ID: 抖音 KOL ID（可选）
        - FEISHU_APP_TOKEN: 飞书多维表格 ID（可选）
        - FEISHU_TABLE_ID: 飞书表格子表 ID（可选）
        - FEISHU_CHAT_ID: 飞书消息群组 ID（可选）
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ 错误：配置文件不存在: {config_path}")
            print("请先复制 config.example.json 为 config.json 并填写配置")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 错误：配置文件格式错误: {e}")
            sys.exit(1)

        # 从环境变量覆盖敏感配置
        # TikHub API Key（必需）
        if os.environ.get('TIKHUB_API_KEY'):
            config['tikhub']['api_key'] = os.environ['TIKHUB_API_KEY']

        # 飞书应用凭证（必需）
        if os.environ.get('FEISHU_APP_ID'):
            config['feishu']['app_id'] = os.environ['FEISHU_APP_ID']
        if os.environ.get('FEISHU_APP_SECRET'):
            config['feishu']['app_secret'] = os.environ['FEISHU_APP_SECRET']

        # 可选配置
        if os.environ.get('DOUYIN_KOL_ID'):
            config['douyin']['kol_id'] = os.environ['DOUYIN_KOL_ID']
        if os.environ.get('FEISHU_APP_TOKEN'):
            config['feishu']['app_token'] = os.environ['FEISHU_APP_TOKEN']
        if os.environ.get('FEISHU_TABLE_ID'):
            config['feishu']['table_id'] = os.environ['FEISHU_TABLE_ID']
        if os.environ.get('FEISHU_CHAT_ID'):
            config['feishu']['chat_id'] = os.environ['FEISHU_CHAT_ID']

        # 验证必需的配置
        self._validate_config(config)

        return config

    def _validate_config(self, config):
        """验证配置是否完整"""
        errors = []

        # 检查 TikHub API Key
        api_key = config.get('tikhub', {}).get('api_key', '')
        if not api_key or api_key == 'YOUR_TIKHUB_API_KEY':
            errors.append("缺少 TikHub API Key，请设置环境变量 TIKHUB_API_KEY 或在 config.json 中配置")

        # 检查飞书凭证
        app_id = config.get('feishu', {}).get('app_id', '')
        if not app_id or app_id == 'YOUR_FEISHU_APP_ID':
            errors.append("缺少飞书 App ID，请设置环境变量 FEISHU_APP_ID 或在 config.json 中配置")

        app_secret = config.get('feishu', {}).get('app_secret', '')
        if not app_secret or app_secret == 'YOUR_FEISHU_APP_SECRET':
            errors.append("缺少飞书 App Secret，请设置环境变量 FEISHU_APP_SECRET 或在 config.json 中配置")

        # 检查 KOL ID
        kol_id = config.get('douyin', {}).get('kol_id', '')
        if not kol_id or kol_id == 'YOUR_DOUYIN_KOL_ID':
            errors.append("缺少抖音 KOL ID，请设置环境变量 DOUYIN_KOL_ID 或在 config.json 中配置")

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
            response = requests.post(url, json=payload)
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

    def fetch_douyin_data(self, start_date, end_date):
        """获取抖音粉丝数据（支持备选 API）"""
        # 获取 API 地址列表（支持单个 URL 或 URL 列表）
        api_urls = self.config['tikhub'].get('api_urls', [])
        if not api_urls:
            # 兼容旧配置：如果没有 api_urls，使用 api_url
            api_url = self.config['tikhub'].get('api_url')
            if api_url:
                api_urls = [api_url]
            else:
                print("❌ 配置错误：缺少 API 地址")
                return None

        params = {
            'kolId': self.config['douyin']['kol_id'],
            'startDate': start_date,
            'endDate': end_date
        }
        headers = {
            'Authorization': f"Bearer {self.config['tikhub']['api_key']}",
            'accept': 'application/json'
        }

        # 尝试所有 API 地址
        for idx, url in enumerate(api_urls):
            try:
                api_name = f"API-{idx + 1}" if len(api_urls) > 1 else "API"
                print(f"🔍 正在使用 {api_name} 获取 {start_date} 的数据...")

                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get('data') and \
                   data['data'].get('daily') and len(data['data']['daily']) > 0 and \
                   data['data'].get('delta') and len(data['data']['delta']) > 0:
                    print(f"✅ {api_name} 请求成功")
                    return data
                else:
                    print(f"⚠️  {api_name} 返回数据为空")
                    # 如果数据为空，尝试下一个 API
                    if idx < len(api_urls) - 1:
                        print(f"🔄 尝试备选 API...")
                        continue
                    return None

            except requests.exceptions.Timeout:
                print(f"⚠️  {api_name} 请求超时")
                if idx < len(api_urls) - 1:
                    print(f"🔄 尝试备选 API...")
                    continue
            except requests.exceptions.RequestException as e:
                print(f"⚠️  {api_name} 请求失败: {e}")
                if idx < len(api_urls) - 1:
                    print(f"🔄 尝试备选 API...")
                    continue
            except Exception as e:
                print(f"⚠️  {api_name} 异常: {e}")
                if idx < len(api_urls) - 1:
                    print(f"🔄 尝试备选 API...")
                    continue

        print(f"❌ 所有 API 地址均请求失败")
        return None

    def parse_data(self, raw_data, target_date=None):
        """
        解析抖音 API 返回的数据

        Args:
            raw_data: API 返回的原始数据
            target_date: 目标日期（可选），如果指定则筛选该日期的数据

        Returns:
            dict: 包含日期、粉丝数、净新增的字典，如果找不到目标日期则返回 None
        """
        daily_list = sorted(raw_data['data']['daily'],
                           key=lambda x: x['date'], reverse=True)
        delta_list = sorted(raw_data['data']['delta'],
                           key=lambda x: x['date'], reverse=True)

        # 如果指定了目标日期，尝试筛选该日期的数据
        if target_date:
            target_daily = next((d for d in daily_list if d['date'] == target_date), None)
            target_delta = next((d for d in delta_list if d['date'] == target_date), None)

            if target_daily and target_delta:
                print(f\"✅ 在返回的数据中找到目标日期 {target_date}\")
                return {
                    'date': target_daily['date'],
                    'fans_count': target_daily['fans_cnt'],
                    'fans_delta': target_delta['fans_cnt']
                }
            else:
                print(f\"⚠️  返回的数据中没有目标日期 {target_date}\")
                if daily_list:
                    print(f\"   可用日期: {[d['date'] for d in daily_list]}\")
                return None

        # 如果没有指定目标日期，返回最新的数据
        latest_daily = daily_list[0]
        latest_delta = delta_list[0]

        return {
            'date': latest_daily['date'],
            'fans_count': latest_daily['fans_cnt'],
            'fans_delta': latest_delta['fans_cnt']
        }

    def check_record_exists(self, date_str):
        """检查飞书表格中是否已存在该日期的记录"""
        if not self.feishu_token:
            print("❌ 飞书 token 未获取，无法查询记录")
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
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 0:
                items = data.get('data', {}).get('items', [])
                return len(items) > 0
            else:
                print(f"⚠️  查询记录失败: {data.get('msg')}")
                return False

        except Exception as e:
            print(f"❌ 查询记录异常: {e}")
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
                "抖音粉丝数": data['fans_count'],
                "抖音净新增": data['fans_delta'],
                "统计日期": timestamp
            }
        }

        try:
            print(f"📝 正在写入飞书表格...")
            response = requests.post(url, json=payload, headers=headers)
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
            response = requests.post(url, json=payload, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            if result.get('code') == 0:
                print(f"✅ 通知发送成功！")
            else:
                print(f"⚠️  通知发送失败: {result.get('msg')}")

        except Exception as e:
            print(f"⚠️  发送通知异常: {e}")

    def collect_with_retry(self, target_date=None):
        """
        采集数据（带智能重试机制）

        策略：多维度组合尝试
        1. 调整 start_date（左侧区间）：往前推 1-3 天
        2. 调整 end_date（右侧区间）：尝试 target、target+1、target-1
        3. 从返回的多天数据中筛选出目标日期

        组合示例（target=2026-02-02）：
        - [2026-02-01, 2026-02-02]  标准组合
        - [2026-02-01, 2026-02-03]  右侧+1
        - [2026-02-01, 2026-02-01]  右侧-1
        - [2026-01-31, 2026-02-02]  左侧-1
        - [2026-01-31, 2026-02-03]  左侧-1, 右侧+1
        ...

        这种策略可以处理 API 的开区间/闭区间不确定性
        """
        if not self.get_feishu_tenant_token():
            return {
                'success': False,
                'message': '获取飞书 token 失败'
            }

        # 确定目标日期（默认为昨天）
        if target_date is None:
            yesterday = datetime.now() - timedelta(days=1)
            target_date = yesterday.strftime('%Y-%m-%d')

        print(f"🎯 目标采集日期: {target_date}")

        max_retry = self.config['retry']['max_retry_days']
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        expected_date = (target_date_obj - timedelta(days=1)).strftime('%Y-%m-%d')

        # 定义日期组合策略
        # 格式：(start_offset, end_offset, description)
        date_combinations = [
            # 第一轮：标准组合
            (1, 0, "标准组合"),
            # 第二轮：调整右侧区间
            (1, 1, "右侧+1天"),
            (1, -1, "右侧-1天"),
            # 第三轮：扩大左侧，保持右侧标准
            (2, 0, "左侧-1天"),
            # 第四轮：扩大左侧，调整右侧
            (2, 1, "左侧-1天,右侧+1天"),
            (2, -1, "左侧-1天,右侧-1天"),
            # 第五轮：继续扩大左侧
            (3, 0, "左侧-2天"),
            (3, 1, "左侧-2天,右侧+1天"),
            (3, -1, "左侧-2天,右侧-1天"),
        ]

        # 根据 max_retry 限制尝试次数
        max_attempts = min(len(date_combinations), max_retry + 1)

        for attempt in range(max_attempts):
            start_offset, end_offset, desc = date_combinations[attempt]

            start_date = (target_date_obj - timedelta(days=start_offset)).strftime('%Y-%m-%d')
            end_date = (target_date_obj + timedelta(days=end_offset)).strftime('%Y-%m-%d')

            print(f"\n📅 第 {attempt + 1} 次尝试 ({desc}): 查询范围 [{start_date}, {end_date}]")
            raw_data = self.fetch_douyin_data(start_date, end_date)

            if raw_data:
                # 尝试从返回的数据中筛选目标日期
                parsed_data = self.parse_data(raw_data, expected_date)

                if parsed_data:
                    # 成功获取到目标日期的数据
                    print(f"✅ 成功获取到 {expected_date} 的数据（使用{desc}）")
                    write_success = self.write_to_feishu(parsed_data)

                    if write_success:
                        self.send_feishu_message(parsed_data)
                        return {
                            'success': True,
                            'data': parsed_data,
                            'message': f'成功采集并写入 {parsed_data["date"]} 的数据'
                        }
                    else:
                        return {
                            'success': False,
                            'message': '数据写入失败'
                        }
                else:
                    # 数据中没有目标日期
                    if attempt < max_attempts - 1:
                        print(f"⚠️  未找到目标日期，尝试其他组合...")
            else:
                # API 请求失败
                if attempt < max_attempts - 1:
                    print(f"⚠️  请求失败，尝试其他组合...")

        return {
            'success': False,
            'message': f'尝试了 {max_attempts} 种日期组合后仍未获取到 {expected_date} 的数据'
        }


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 抖音数据采集程序启动")
    print("=" * 50)

    collector = DouyinDataCollector()
    result = collector.collect_with_retry()

    print("\n" + "=" * 50)
    if result['success']:
        print("✅ 采集成功！")
        data = result['data']
        print(f"📅 日期: {data['date']}")
        print(f"👥 粉丝总数: {int(data['fans_count']):,}")
        print(f"📈 净新增: {int(data['fans_delta']):,}")
    else:
        print(f"❌ 采集失败: {result['message']}")
    print("=" * 50)

    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
