---
name: douyin-data-collector
description: 采集抖音账号粉丝数据并自动填写到飞书表格。使用场景：(1) 用户说"采集抖音数据"或"抖音粉丝数据"，(2) 用户说"采集 YYYY-MM-DD 的抖音数据"，(3) 用户说"采集最近 N 天的抖音数据"。支持数据去重、智能重试和飞书消息通知。
---

# 抖音数据采集

采集抖音账号粉丝数据并写入飞书多维表格。

## 首次配置

1. 安装依赖：
```bash
pip3 install -r {SKILL_DIR}/requirements.txt
```

2. 配置敏感信息（二选一）：

**方式一：环境变量（推荐）**
```bash
cp {SKILL_DIR}/.env.example {SKILL_DIR}/.env
# 编辑 .env 填入密钥
```

**方式二：配置文件**
```bash
cp {SKILL_DIR}/config.example.json {SKILL_DIR}/config.json
# 编辑 config.json 填入配置
```

环境变量优先级高于配置文件。

## 必需的环境变量/配置

| 环境变量 | 配置字段 | 说明 |
|---------|---------|------|
| TIKHUB_API_KEY | tikhub.api_key | TikHub API 密钥 |
| FEISHU_APP_ID | feishu.app_id | 飞书应用 ID |
| FEISHU_APP_SECRET | feishu.app_secret | 飞书应用密钥 |
| DOUYIN_KOL_ID | douyin.kol_id | 抖音 KOL ID |
| FEISHU_APP_TOKEN | feishu.app_token | 飞书多维表格 ID |
| FEISHU_TABLE_ID | feishu.table_id | 表格子表 ID |
| FEISHU_CHAT_ID | feishu.chat_id | 消息群组 ID |

## 执行采集

```bash
{SKILL_DIR}/scripts/run.sh
```

## 采集结果

脚本输出包含：
- 统计日期
- 粉丝总数
- 粉丝净新增
- 写入状态
- 通知状态
