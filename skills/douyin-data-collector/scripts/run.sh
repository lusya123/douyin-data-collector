#!/bin/bash
# 运行抖音数据采集脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查是否存在 .env 文件并加载
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/../.env" | xargs)
fi

# 运行采集脚本
python3 "$SCRIPT_DIR/collector.py" "$@"

exit $?
