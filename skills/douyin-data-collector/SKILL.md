---
name: douyin-data-collector
description: 采集抖音账号粉丝数据并自动填写到飞书表格。使用场景：(1) 用户说"采集抖音数据"或"抖音粉丝数据"，(2) 用户说"采集 YYYY-MM-DD 的抖音数据"，(3) 用户说"采集最近 N 天的抖音数据"。支持数据去重、智能重试和飞书消息通知。首次使用会自动引导配置。
---

# 抖音数据采集

采集抖音账号粉丝数据并写入飞书多维表格。

## 执行流程

**每次执行前必须先检查配置：**

### 步骤 1：检查配置

```bash
python3 {SKILL_DIR}/scripts/check_config.py
```

- 如果输出 `CONFIG_OK`：配置完整，继续步骤 2
- 如果输出 `MISSING_CONFIG`：配置缺失，执行步骤 1.1

### 步骤 1.1：引导用户配置（仅当配置缺失时）

当检测到缺失配置时，使用 AskUserQuestion 工具逐项询问用户：

**缺失项说明：**

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| TIKHUB_API_KEY | TikHub API 密钥 | 在 https://tikhub.io 注册获取 |
| FEISHU_APP_ID | 飞书应用 ID | 飞书开放平台创建应用 |
| FEISHU_APP_SECRET | 飞书应用密钥 | 飞书应用的 App Secret |
| DOUYIN_KOL_ID | 抖音 KOL ID | 抖音星图平台获取 |
| FEISHU_APP_TOKEN | 飞书多维表格 ID | 表格 URL 中的 app_token |
| FEISHU_TABLE_ID | 表格子表 ID | 表格内子表的 ID |
| FEISHU_CHAT_ID | 消息群组 ID | 接收通知的群组 ID |

**配置方式：** 用户提供值后，执行：

```bash
python3 {SKILL_DIR}/scripts/setup.py "配置项" "用户提供的值"
```

例如：
```bash
python3 {SKILL_DIR}/scripts/setup.py "tikhub.api_key" "用户的API密钥"
python3 {SKILL_DIR}/scripts/setup.py "douyin.kol_id" "7339427184844472347"
```

配置完所有缺失项后，重新执行步骤 1 验证。

### 步骤 2：安装依赖（首次）

```bash
pip3 install -r {SKILL_DIR}/requirements.txt
```

### 步骤 3：执行采集

```bash
{SKILL_DIR}/scripts/run.sh
```

### 步骤 4：汇报结果

向用户汇报：
- 统计日期
- 粉丝总数
- 粉丝净新增
- 写入状态
- 通知状态
