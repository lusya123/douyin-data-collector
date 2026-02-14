#!/bin/bash
# 运行抖音数据采集脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查是否存在 .env 文件并加载
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/../.env" | xargs)
fi

# 检查并安装依赖
check_and_install_deps() {
    # 检查 requests 模块是否已安装
    if ! python3 -c "import requests" 2>/dev/null; then
        echo "📦 检测到缺少依赖，正在安装..."

        # 尝试标准安装
        if pip3 install -r "$SCRIPT_DIR/../requirements.txt" 2>/dev/null; then
            echo "✅ 依赖安装成功"
            return 0
        fi

        # 如果标准安装失败，尝试使用 --break-system-packages
        echo "⚠️  标准安装失败，尝试使用 --break-system-packages..."
        if pip3 install --break-system-packages -r "$SCRIPT_DIR/../requirements.txt" 2>/dev/null; then
            echo "✅ 依赖安装成功"
            return 0
        fi

        echo "❌ 依赖安装失败，请手动执行："
        echo "   pip3 install --break-system-packages -r $SCRIPT_DIR/../requirements.txt"
        return 1
    fi
    return 0
}

# 执行依赖检查
check_and_install_deps || exit 1

# 运行采集脚本
python3 "$SCRIPT_DIR/collector.py" "$@"

exit $?
