#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置检查脚本
检查是否已完成必要配置，返回缺失的配置项
"""

import json
import os
import sys
from pathlib import Path


def check_config():
    """检查配置完整性，返回缺失项列表"""
    skill_dir = Path(__file__).parent.parent
    config_path = skill_dir / "config.json"
    env_path = skill_dir / ".env"

    missing = []

    # 加载 .env 文件（如果存在）
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    # 合并环境变量
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    # 加载配置文件
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            pass

    # 检查必需配置
    checks = [
        ('TIKHUB_API_KEY', 'tikhub.api_key', 'TikHub API 密钥'),
        ('FEISHU_APP_ID', 'feishu.app_id', '飞书应用 ID'),
        ('FEISHU_APP_SECRET', 'feishu.app_secret', '飞书应用密钥'),
        ('DOUYIN_KOL_ID', 'douyin.kol_id', '抖音 KOL ID'),
        ('FEISHU_APP_TOKEN', 'feishu.app_token', '飞书多维表格 ID'),
        ('FEISHU_TABLE_ID', 'feishu.table_id', '飞书表格子表 ID'),
        ('FEISHU_CHAT_ID', 'feishu.chat_id', '飞书消息群组 ID'),
    ]

    for env_key, config_key, desc in checks:
        # 检查环境变量
        env_value = os.environ.get(env_key, '')

        # 检查配置文件
        config_value = ''
        keys = config_key.split('.')
        obj = config
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                obj = ''
                break
        config_value = str(obj) if obj else ''

        # 判断是否有效
        placeholders = ['YOUR_', 'your_', '']
        is_valid = False

        for val in [env_value, config_value]:
            if val and not any(val.startswith(p) for p in placeholders if p):
                is_valid = True
                break

        if not is_valid:
            missing.append({
                'env_key': env_key,
                'config_key': config_key,
                'description': desc
            })

    return missing


def main():
    """主函数"""
    missing = check_config()

    if missing:
        print("MISSING_CONFIG")
        for item in missing:
            print(f"{item['env_key']}|{item['config_key']}|{item['description']}")
        return 1
    else:
        print("CONFIG_OK")
        return 0


if __name__ == '__main__':
    sys.exit(main())
