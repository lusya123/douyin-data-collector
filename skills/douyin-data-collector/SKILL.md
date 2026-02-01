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

脚本会自动检测：
- 系统架构（x64/arm64/arm32）
- 操作系统类型
- Python 版本

**根据输出处理：**

- `PYTHON_OK`：环境正常，继续步骤 1
- `PYTHON_OLD` 或 `PYTHON_NOT_FOUND`：执行步骤 0.1

### 步骤 0.1：引导安装 Python（仅当环境异常时）

脚本输出包含：
- `ARCH:` - 系统架构（x64/arm64/arm32）
- `OS:` - 操作系统
- `INSTALL_CMD:` - 推荐的安装命令
- `NOTE:` - 架构说明

**各系统/架构安装命令：**

| 系统 | 架构 | 安装命令 |
|-----|------|---------|
| macOS | arm64 (M1/M2/M3) | `brew install python@3.11` |
| macOS | x64 (Intel) | `brew install python@3.11` |
| Ubuntu/Debian | x64 | `sudo apt update && sudo apt install -y python3 python3-pip python3-venv` |
| Ubuntu/Debian | arm64 | `sudo apt update && sudo apt install -y python3 python3-pip python3-venv` |
| Ubuntu/Debian | arm32 (树莓派) | `sudo apt update && sudo apt install -y python3 python3-pip python3-venv` |
| CentOS/RHEL | x64 | `sudo yum install -y python3 python3-pip` |
| CentOS/RHEL | arm64 | `sudo yum install -y python3 python3-pip` |
| Amazon Linux | arm64 (Graviton) | `sudo yum install -y python3 python3-pip` |
| Alpine | 任意 | `apk add python3 py3-pip` |
| Windows | x64 | `winget install Python.Python.3.11` |
| Windows | arm64 | `winget install Python.Python.3.11` |

**处理方式：**
1. 告知用户检测到的架构和操作系统
2. 提供脚本输出的安装命令
3. 询问用户是否需要帮助执行
4. 执行后重新运行步骤 0 验证

### 步骤 1：检查配置

```bash
python3 {SKILL_DIR}/scripts/check_config.py
```

- `CONFIG_OK`：继续步骤 2
- `MISSING_CONFIG`：执行步骤 1.1

### 步骤 1.1：引导用户配置

使用 AskUserQuestion 询问缺失配置：

| 配置项 | 说明 |
|-------|------|
| tikhub.api_key | TikHub API 密钥 |
| feishu.app_id | 飞书应用 ID |
| feishu.app_secret | 飞书应用密钥 |
| douyin.kol_id | 抖音 KOL ID |
| feishu.app_token | 飞书多维表格 ID |
| feishu.table_id | 表格子表 ID |
| feishu.chat_id | 消息群组 ID |

保存配置：
```bash
python3 {SKILL_DIR}/scripts/setup.py "配置项" "值"
```

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
