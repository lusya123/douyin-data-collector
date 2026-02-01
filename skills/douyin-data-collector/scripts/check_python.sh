#!/bin/bash
# Python 环境检查脚本
# 检查 Python 3 是否已安装，返回版本信息或安装指引

check_python() {
    # 检查 python3
    if command -v python3 &> /dev/null; then
        version=$(python3 --version 2>&1 | cut -d' ' -f2)
        major=$(echo "$version" | cut -d'.' -f1)
        minor=$(echo "$version" | cut -d'.' -f2)

        # 检查版本是否 >= 3.8
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            echo "PYTHON_OK"
            echo "VERSION:$version"
            echo "PATH:$(which python3)"
            exit 0
        else
            echo "PYTHON_OLD"
            echo "VERSION:$version"
            echo "REQUIRED:3.8+"
            exit 1
        fi
    fi

    # 检查 python (可能是 python3 的别名)
    if command -v python &> /dev/null; then
        version=$(python --version 2>&1 | cut -d' ' -f2)
        major=$(echo "$version" | cut -d'.' -f1)

        if [ "$major" -ge 3 ]; then
            minor=$(echo "$version" | cut -d'.' -f2)
            if [ "$minor" -ge 8 ]; then
                echo "PYTHON_OK"
                echo "VERSION:$version"
                echo "PATH:$(which python)"
                echo "NOTE:python3 not found, using python"
                exit 0
            fi
        fi
    fi

    # Python 未安装
    echo "PYTHON_NOT_FOUND"

    # 检测操作系统并提供安装指引
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "OS:macOS"
        echo "INSTALL_CMD:brew install python@3.11"
        echo "ALT_INSTALL:从 https://www.python.org/downloads/ 下载安装"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            echo "OS:Ubuntu/Debian"
            echo "INSTALL_CMD:sudo apt update && sudo apt install python3 python3-pip"
        elif command -v yum &> /dev/null; then
            echo "OS:CentOS/RHEL"
            echo "INSTALL_CMD:sudo yum install python3 python3-pip"
        elif command -v dnf &> /dev/null; then
            echo "OS:Fedora"
            echo "INSTALL_CMD:sudo dnf install python3 python3-pip"
        else
            echo "OS:Linux"
            echo "INSTALL_CMD:请使用系统包管理器安装 python3"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "OS:Windows"
        echo "INSTALL_CMD:winget install Python.Python.3.11"
        echo "ALT_INSTALL:从 https://www.python.org/downloads/ 下载安装"
    else
        echo "OS:Unknown"
        echo "INSTALL_CMD:请从 https://www.python.org/downloads/ 下载安装 Python 3.8+"
    fi

    exit 1
}

check_python
