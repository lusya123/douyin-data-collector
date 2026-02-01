---
name: douyin-data-collector
description: 采集抖音账号粉丝数据并自动填写到飞书表格。使用场景：(1) 用户说"采集抖音数据"或"抖音粉丝数据"，(2) 用户说"采集 YYYY-MM-DD 的抖音数据"，(3) 用户说"采集最近 N 天的抖音数据"。支持数据去重、智能重试和飞书消息通知。首次使用会自动检查环境并引导配置。
---

# 抖音数据采集

采集抖音账号粉丝数据并写入飞书多维表格。

## 执行流程

**严格按顺序执行以下步骤：**

### 步骤 0：检查 Python 环境

```bash
bash {SKILL_DIR}/scripts/check_python.sh
```

**根据输出处理：**

- `PYTHON_OK`：Python 环境正常，继续步骤 1
- `PYTHON_OLD`：Python 版本过低（需要 3.8+），执行步骤 0.1
- `PYTHON_NOT_FOUND`：Python 未安装，执行步骤 0.1

### 步骤 0.1：引导安装 Python（仅当环境异常时）

脚本会输出适合用户操作系统的安装命令，格式如：
```
INSTALL_CMD:brew install python@3.11
```

**处理方式：**

1. 告知用户需要安装 Python 3.8+
2. 提供脚本输出的安装命令
3. 询问用户是否需要帮助执行安装命令
4. 如果用户同意，执行 `INSTALL_CMD` 后面的命令
5. 安装完成后重新执行步骤 0 验证

**各系统安装命令参考：**

| 系统 | 安装命令 |
|-----|---------|
| macOS | `brew install python@3.11` |
| Ubuntu/Debian | `sudo apt update && sudo apt install python3 python3-pip` |
| CentOS/RHEL | `sudo yum install python3 python3-pip` |
| Windows | `winget install Python.Python.3.11` |

### 步骤 1：检查配置

```bash
python3 {SKILL_DIR}/scripts/check_config.py
```

- `CONFIG_OK`：配置完整，继续步骤 2
- `MISSING_CONFIG`：配置缺失，执行步骤 1.1

### 步骤 1.1：引导用户配置（仅当配置缺失时）

使用 AskUserQuestion 工具逐项询问缺失的配置：

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| tikhub.api_key | TikHub API 密钥 | https://tikhub.io 注册 |
| feishu.app_id | 飞书应用 ID | 飞书开放平台创建应用 |
| feishu.app_secret | 飞书应用密钥 | 飞书应用的 App Secret |
| douyin.kol_id | 抖音 KOL ID | 抖音星图平台获取 |
| feishu.app_token | 飞书多维表格 ID | 表格 URL 中的 app_token |
| feishu.table_id | 表格子表 ID | 表格内子表的 ID |
| feishu.chat_id | 消息群组 ID | 接收通知的群组 ID |

用户提供值后保存：
```bash
python3 {SKILL_DIR}/scripts/setup.py "配置项" "值"
```

配置完成后重新执行步骤 1 验证。

### 步骤 2：安装依赖

```bash
pip3 install -r {SKILL_DIR}/requirements.txt
```

### 步骤 3：执行采集

```bash
bash {SKILL_DIR}/scripts/run.sh
```

### 步骤 4：汇报结果

向用户汇报：统计日期、粉丝总数、粉丝净新增、写入状态、通知状态
