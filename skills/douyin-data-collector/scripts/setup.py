#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式配置脚本
引导用户完成首次配置
"""

import json
import os
import sys
from pathlib import Path


def setup_config():
    """交互式配置"""
    skill_dir = Path(__file__).parent.parent
    config_path = skill_dir / "config.json"
    config_example_path = skill_dir / "config.example.json"
    env_path = skill_dir / ".env"

    print("=" * 50)
    print("🔧 抖音数据采集器 - 首次配置向导")
    print("=" * 50)
    print()

    # 加载示例配置作为模板
    if config_example_path.exists():
        with open(config_example_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {
            "douyin": {"kol_id": ""},
            "tikhub": {
                "api_url": "https://api.tikhub.dev/api/v1/douyin/xingtu/kol_daily_fans_v1",
                "api_key": ""
            },
            "feishu": {
                "app_id": "",
                "app_secret": "",
                "app_token": "",
                "table_id": "",
                "chat_id": ""
            },
            "retry": {"max_retry_days": 3}
        }

    # 如果已有配置，加载现有值
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                # 合并现有配置
                for section in existing:
                    if section in config and isinstance(config[section], dict):
                        config[section].update(existing[section])
        except:
            pass

    # 配置项定义
    config_items = [
        {
            'key': 'douyin.kol_id',
            'name': '抖音 KOL ID',
            'help': '在抖音星图平台获取，格式如：7339427184844472347',
            'required': True
        },
        {
            'key': 'tikhub.api_key',
            'name': 'TikHub API 密钥',
            'help': '在 https://tikhub.io 注册获取',
            'required': True
        },
        {
            'key': 'feishu.app_id',
            'name': '飞书应用 ID',
            'help': '在飞书开放平台创建应用获取',
            'required': True
        },
        {
            'key': 'feishu.app_secret',
            'name': '飞书应用密钥',
            'help': '飞书应用的 App Secret',
            'required': True
        },
        {
            'key': 'feishu.app_token',
            'name': '飞书多维表格 ID',
            'help': '多维表格 URL 中的 app_token，如：XeYibz7k3aVWr3sYsVqcK81PnMd',
            'required': True
        },
        {
            'key': 'feishu.table_id',
            'name': '飞书表格子表 ID',
            'help': '表格内子表的 ID，如：tbld0HtppiiparM0',
            'required': True
        },
        {
            'key': 'feishu.chat_id',
            'name': '飞书消息群组 ID',
            'help': '接收通知的群组 ID，如：oc_056366d2b007b437802b029eb8b5e679',
            'required': True
        },
    ]

    def get_config_value(key):
        """获取配置值"""
        keys = key.split('.')
        obj = config
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                return ''
        return obj if obj and not str(obj).startswith('YOUR_') else ''

    def set_config_value(key, value):
        """设置配置值"""
        keys = key.split('.')
        obj = config
        for k in keys[:-1]:
            if k not in obj:
                obj[k] = {}
            obj = obj[k]
        obj[keys[-1]] = value

    print("请依次输入以下配置（直接回车跳过保留现有值）：\n")

    for item in config_items:
        current = get_config_value(item['key'])
        current_display = current[:20] + '...' if len(str(current)) > 20 else current

        print(f"📌 {item['name']}")
        print(f"   说明: {item['help']}")
        if current:
            print(f"   当前值: {current_display}")

        value = input(f"   请输入: ").strip()

        if value:
            set_config_value(item['key'], value)
            print(f"   ✅ 已设置\n")
        elif current:
            print(f"   ⏭️  保留现有值\n")
        else:
            print(f"   ⚠️  未设置（必需项）\n")

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"✅ 配置已保存到: {config_path}")
    print("=" * 50)

    return 0


def main():
    """主函数，支持命令行参数"""
    if len(sys.argv) > 1:
        # 非交互模式：直接设置单个配置
        # 用法: setup.py KEY VALUE
        if len(sys.argv) >= 3:
            key = sys.argv[1]
            value = sys.argv[2]

            skill_dir = Path(__file__).parent.parent
            config_path = skill_dir / "config.json"
            config_example_path = skill_dir / "config.example.json"

            # 加载配置
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif config_example_path.exists():
                with open(config_example_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}

            # 设置值
            keys = key.split('.')
            obj = config
            for k in keys[:-1]:
                if k not in obj:
                    obj[k] = {}
                obj = obj[k]
            obj[keys[-1]] = value

            # 保存
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            print(f"OK: {key} = {value}")
            return 0
    else:
        # 交互模式
        return setup_config()


if __name__ == '__main__':
    sys.exit(main())
