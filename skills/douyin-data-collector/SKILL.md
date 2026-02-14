---
name: douyin-data-collector
description: 采集抖音账号粉丝数据并自动填写到飞书表格。使用场景：(1) 用户说"采集抖音数据"或"抖音粉丝数据"，(2) 用户说"采集 YYYY-MM-DD 的抖音数据"，(3) 用户说"采集最近 N 天的抖音数据"。支持数据去重、智能重试和飞书消息通知。首次使用会自动检查环境并引导配置。v2.0 优先使用实时接口，数据更准确。
---

# 抖音数据采集 v2.0

采集抖音账号粉丝数据并写入飞书多维表格。

## 🆕 v2.0 更新

**新采集策略（更准确、更稳定）：**

1. **多接口冗余**：使用 3 个实时接口 + 2 个历史接口，5 层保障
   - 实时接口 1: handler_user_profile (v1)
   - 实时接口 2: handler_user_profile_v4 (详细版)
   - 实时接口 3: app_user_profile (APP 端)
   - 历史接口 1: kol_daily_fans_v1 (主)
   - 历史接口 2: kol_daily_fans_v1 (备用域名)

2. **智能降级策略**：按顺序尝试，第一个成功即返回
   ```
   实时接口-1 → 失败 → 实时接口-2 → 失败 → 实时接口-3 → 失败 → 历史接口-1 → 失败 → 历史接口-2
   ```

3. **智能计算净增**：从飞书查询前一天数据，自动计算粉丝净增

4. **日期准确性**：
   - 实时接口：数据日期为采集当天（今天）
   - 历史接口：数据日期为 API 返回的日期（通常是昨天）

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

| 配置项 | 说明 | 必需性 |
|-------|------|--------|
| tikhub.api_key | TikHub API 密钥 | 必需 |
| douyin.sec_user_id | 抖音 sec_user_id（用于实时接口） | 必需 |
| douyin.kol_id | 抖音 KOL ID（用于历史接口备用） | 可选 |
| feishu.app_id | 飞书应用 ID | 必需 |
| feishu.app_secret | 飞书应用密钥 | 必需 |
| feishu.app_token | 飞书多维表格 ID | 必需 |
| feishu.table_id | 表格子表 ID | 必需 |
| feishu.chat_id | 消息群组 ID | 必需 |

保存配置：
```bash
python3 {SKILL_DIR}/scripts/setup.py "配置项" "值"
```

### 步骤 2：执行采集

```bash
bash {SKILL_DIR}/scripts/run.sh
```

**说明：**
- run.sh 会自动检查并安装依赖（requests、python-dateutil）
- 如果遇到 `externally-managed-environment` 错误，脚本会自动使用 `--break-system-packages` 标志重试
- 无需手动安装依赖

**采集策略（5 层保障）：**
1. 尝试 3 个实时接口（按顺序，第一个成功即返回）
2. 从飞书查询前一天的粉丝数，计算净增
3. 如果所有实时接口失败，降级到 2 个历史接口
4. 历史接口也按顺序尝试，第一个成功即返回

### 步骤 3：汇报结果

向用户汇报：
- 统计日期（实时接口为今天，历史接口为 API 返回日期）
- 粉丝总数
- 粉丝净新增
- 数据来源（realtime 或 history）
- 写入状态
- 通知状态

## 配置说明

### 新增配置项

```json
{
  "douyin": {
    "sec_user_id": "MS4wLjABAAAA...",  // 用于实时接口
    "kol_id": "7339427184844472347"     // 用于历史接口备用
  },
  "tikhub": {
    "realtime_api_urls": [  // v2.0: 3 个实时接口备选
      "https://api.tikhub.io/api/v1/douyin/web/handler_user_profile",
      "https://api.tikhub.io/api/v1/douyin/web/handler_user_profile_v4",
      "https://api.tikhub.io/api/v1/douyin/app/v3/handler_user_profile"
    ],
    "history_api_urls": [  // 2 个历史接口备选
      "https://api.tikhub.io/api/v1/douyin/xingtu/kol_daily_fans_v1",
      "https://api.tikhub.dev/api/v1/douyin/xingtu/kol_daily_fans_v1"
    ]
  }
}
```

## 日期处理说明

**重要：不同接口返回的日期含义不同**

1. **实时接口**（优先）：
   - 返回当前时刻的粉丝数
   - 数据日期 = 采集日期（今天）
   - 净增 = 当前粉丝数 - 飞书中前一天的粉丝数

2. **历史接口**（备用）：
   - 返回历史某天的粉丝数和净增
   - 数据日期 = API 返回的日期（通常是昨天）
   - 净增 = API 直接返回

**示例：**
- 2026-02-14 运行采集
- 实时接口：插入 2026-02-14 的数据（今天）
- 历史接口：插入 2026-02-13 的数据（昨天）

## 故障排查

### 所有接口都失败
- 检查 API Token 是否有效
- 检查网络连接
- 查看错误日志确定具体原因

### 实时接口全部失败（降级到历史接口）
- 检查 sec_user_id 是否正确
- TikHub 实时接口可能临时故障
- 历史接口会自动接管

### 历史接口也失败
- 检查 kol_id 是否正确
- 该账号可能未入驻星图平台
- 联系 TikHub 支持

### 净增计算为 0
- 飞书中没有前一天的数据
- 这是正常情况，首次采集时会出现

## 稳定性保障

**5 层冗余设计：**
- 第 1-3 层：3 个实时接口（不同端点，相同数据源）
- 第 4-5 层：2 个历史接口（不同域名）
- 理论可用性：99.999%+（假设单接口 99% 可用）
