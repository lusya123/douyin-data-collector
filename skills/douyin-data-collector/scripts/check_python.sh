#!/bin/bash
# Python 环境检查脚本
# 检查 Python 3 是否已安装，检测系统架构，返回版本信息或安装指引

# 检测系统架构
detect_arch() {
    local arch=$(uname -m)
    case "$arch" in
        x86_64|amd64)
            echo "x64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l|armv6l)
            echo "arm32"
            ;;
        i386|i686)
            echo "x86"
            ;;
        *)
            echo "$arch"
            ;;
    esac
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            echo "$ID"
        elif command -v apt &> /dev/null; then
            echo "debian"
        elif command -v yum &> /dev/null; then
            echo "centos"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

check_python() {
    local arch=$(detect_arch)
    local os=$(detect_os)

    echo "ARCH:$arch"
    echo "OS:$os"

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
            provide_install_guide "$os" "$arch"
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
    provide_install_guide "$os" "$arch"
    exit 1
}

provide_install_guide() {
    local os=$1
    local arch=$2

    case "$os" in
        macOS)
            if [ "$arch" == "arm64" ]; then
                echo "INSTALL_CMD:brew install python@3.11"
                echo "NOTE:Apple Silicon (M1/M2/M3) 检测到，使用 Homebrew 安装"
            else
                echo "INSTALL_CMD:brew install python@3.11"
                echo "NOTE:Intel Mac 检测到，使用 Homebrew 安装"
            fi
            echo "ALT_INSTALL:从 https://www.python.org/downloads/macos/ 下载安装"
            ;;
        ubuntu|debian|pop|linuxmint)
            echo "INSTALL_CMD:sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
            if [ "$arch" == "arm64" ]; then
                echo "NOTE:ARM64 架构 Debian/Ubuntu 系统"
            elif [ "$arch" == "arm32" ]; then
                echo "NOTE:ARM32 架构（如树莓派）Debian/Ubuntu 系统"
            else
                echo "NOTE:x64 架构 Debian/Ubuntu 系统"
            fi
            ;;
        centos|rhel|rocky|almalinux)
            if [ "$arch" == "arm64" ]; then
                echo "INSTALL_CMD:sudo yum install -y python3 python3-pip"
                echo "NOTE:ARM64 架构 CentOS/RHEL 系统"
            else
                echo "INSTALL_CMD:sudo yum install -y python3 python3-pip"
                echo "NOTE:x64 架构 CentOS/RHEL 系统"
            fi
            ;;
        fedora)
            echo "INSTALL_CMD:sudo dnf install -y python3 python3-pip"
            if [ "$arch" == "arm64" ]; then
                echo "NOTE:ARM64 架构 Fedora 系统"
            else
                echo "NOTE:x64 架构 Fedora 系统"
            fi
            ;;
        arch|manjaro)
            echo "INSTALL_CMD:sudo pacman -S python python-pip"
            echo "NOTE:Arch Linux 系统 ($arch 架构)"
            ;;
        alpine)
            echo "INSTALL_CMD:apk add python3 py3-pip"
            if [ "$arch" == "arm64" ]; then
                echo "NOTE:ARM64 架构 Alpine Linux（常见于 Docker 容器）"
            else
                echo "NOTE:$arch 架构 Alpine Linux"
            fi
            ;;
        amzn)
            # Amazon Linux
            echo "INSTALL_CMD:sudo yum install -y python3 python3-pip"
            if [ "$arch" == "arm64" ]; then
                echo "NOTE:ARM64 架构 Amazon Linux（Graviton 处理器）"
            else
                echo "NOTE:x64 架构 Amazon Linux"
            fi
            ;;
        windows)
            if [ "$arch" == "arm64" ]; then
                echo "INSTALL_CMD:winget install Python.Python.3.11"
                echo "NOTE:Windows ARM64 架构"
                echo "ALT_INSTALL:从 https://www.python.org/downloads/windows/ 下载 ARM64 版本"
            else
                echo "INSTALL_CMD:winget install Python.Python.3.11"
                echo "NOTE:Windows x64 架构"
                echo "ALT_INSTALL:从 https://www.python.org/downloads/windows/ 下载安装"
            fi
            ;;
        *)
            echo "INSTALL_CMD:请从 https://www.python.org/downloads/ 下载适合 $arch 架构的 Python 3.8+"
            echo "NOTE:未识别的操作系统 ($os)，架构: $arch"
            ;;
    esac

    # 提供源码编译选项（适用于特殊架构）
    if [ "$arch" != "x64" ] && [ "$arch" != "arm64" ] && [ "$os" != "macOS" ] && [ "$os" != "windows" ]; then
        echo "SOURCE_BUILD:如果包管理器没有适合的版本，可以从源码编译："
        echo "SOURCE_BUILD_CMD:wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && tar xzf Python-3.11.0.tgz && cd Python-3.11.0 && ./configure --enable-optimizations && make -j\$(nproc) && sudo make altinstall"
    fi
}

check_python
