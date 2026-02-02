# 抖音数据采集 Skill

自动采集抖音账号粉丝数据并写入飞书表格的 Claude Code Skill。

## 功能说明

- 🎯 **自动采集**：调用 TikHub API 获取抖音粉丝数据
- 🔄 **智能重试**：数据未更新时自动往前推日期重试
- ✅ **去重检查**：自动检测飞书表格中是否已有记录
- 📊 **自动填表**：采集的数据自动写入飞书多维表格
- 📨 **消息通知**：采集完成后发送飞书群组消息

## 快速开始

### 1. 安装依赖

```bash
cd ~/.claude/skills/douyin-data-collector
pip3 install -r requirements.txt
```

### 2. 配置文件

复制示例配置并填写你的信息：

```bash
cp config.example.json config.json
```

编辑 `config.json`，填写以下配置：

- **TikHub API Key**：在 [TikHub](https://tikhub.dev) 获取
- **飞书 App ID & Secret**：创建飞书机器人获取
- **飞书表格 ID**：多维表格的 app_token 和 table_id
- **飞书群组 ID**：消息通知的目标群组

### 3. 使用 Skill

在 Claude Code 中输入：

```
/douyin-data-collector
```

或者直接说：

```
采集抖音数据
```

## 配置说明

### TikHub API

1. 注册 [TikHub](https://tikhub.dev) 账号
2. 获取 API Key
3. 填入 `config.json` 的 `tikhub.api_key`

### 飞书配置

1. **创建飞书应用**
   - 访问 [飞书开放平台](https://open.feishu.cn/)
   - 创建企业自建应用
   - 获取 App ID 和 App Secret

2. **配置权限**
   - 添加多维表格权限：`bitable:app`
   - 添加消息发送权限：`im:message`

3. **获取表格 ID**
   - 打开你的飞书多维表格
   - URL 格式：`https://xxx.feishu.cn/base/{app_token}?table={table_id}`
   - 提取其中的 app_token 和 table_id

4. **获取群组 ID**
   - 将机器人添加到目标群组
   - 在群设置中查看群组 ID

### 表格字段要求

飞书表格需要包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 统计日期 | 日期 | 数据日期（用于去重） |
| 统计日期文本 | 文本 | 日期文本格式（用于查询） |
| 抖音粉丝数 | 数字 | 粉丝总数 |
| 抖音净新增 | 数字 | 粉丝净增长 |

## 工作流程

```
┌─────────────┐
│ 触发采集请求 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 获取飞书Token│
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────┐
│ 调用TikHub  │────▶│ 数据为空? │──Yes──┐
│ API获取数据 │     └──────────┘       │
└──────┬──────┘                        │
       │ No                            │
       ▼                               ▼
┌─────────────┐              ┌─────────────┐
│ 解析数据    │              │ 日期往前推1天│
└──────┬──────┘              └──────┬──────┘
       │                            │
       ▼                            │
┌─────────────┐                     │
│ 检查飞书表格 │◀────────────────────┘
│ 是否已有记录 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 写入飞书表格 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 发送飞书消息 │
└─────────────┘
```

## 高级用法

### 手动运行脚本

```bash
cd ~/.claude/skills/douyin-data-collector
python3 collector.py
```

### 定时任务（可选）

使用 crontab 设置定时采集：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天12:30执行）
30 12 * * * cd ~/.claude/skills/douyin-data-collector && python3 collector.py >> ~/douyin-collector.log 2>&1
```

## 故障排查

### 问题：API 返回 401

- 检查 TikHub API Key 是否正确
- 确认 API Key 是否过期

### 问题：无法写入飞书

- 检查 App ID 和 App Secret 是否正确
- 确认飞书应用权限是否配置完整
- 检查表格 ID 是否正确

### 问题：数据总是为空

- 检查抖音 KOL ID 是否正确
- 尝试手动访问 TikHub API 测试
- 查看是否需要调整日期参数

## 技术支持

如有问题，请检查：

1. Python 版本（建议 3.7+）
2. 网络连接
3. API 配额限制
4. 日志输出信息

## License

MIT
