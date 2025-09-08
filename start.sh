#!/bin/bash

# 检查必要的工具是否安装
check_dependencies() {
    local missing=()

    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        missing+=("curl或wget")
    fi

    if ! command -v unzip &> /dev/null; then
        missing+=("unzip")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        echo "错误: 缺少必要的工具: ${missing[*]}"
        echo "请安装这些工具后重试"
        exit 1
    fi
}

# 下载文件
download_file() {
    local url="$1"
    local filename

    # 从URL提取文件名
    filename=$(basename "$url")

    echo "正在下载: $url"

    # 优先使用curl，如果没有则使用wget
    if command -v curl &> /dev/null; then
        curl -L -o "$filename" "$url"
    elif command -v wget &> /dev/null; then
        wget -O "$filename" "$url"
    fi

    # 检查下载是否成功
    if [ $? -ne 0 ] || [ ! -f "$filename" ]; then
        echo "下载失败!"
        exit 1
    fi

    echo "下载完成: $filename"
    echo "$filename"  # 返回文件名
}

# 解压文件
extract_file() {
    local file="$1"

    # 检查文件是否存在
    if [ ! -f "$file" ]; then
        echo "文件不存在: $file"
        exit 1
    fi

    # 根据文件类型选择解压方式
    case "$file" in
        *.zip)
            # 提示用户输入密码
            read -s -p "请输入压缩包密码: " password
            echo
            unzip -P "$password" "$file"
            ;;
        *.tar.gz|*.tgz)
            read -s -p "请输入压缩包密码: " password
            echo
            # tar本身不支持密码，使用gpg加密的tar需要先解密
            echo "注意: tar格式通常不直接支持密码，可能需要其他工具"
            ;;
        *.7z)
            if command -v 7z &> /dev/null; then
                read -s -p "请输入压缩包密码: " password
                echo
                7z x -p"$password" "$file"
            else
                echo "需要安装7z工具来解压.7z文件"
                exit 1
            fi
            ;;
        *)
            echo "不支持的压缩格式: $file"
            exit 1
            ;;
    esac

    # 检查解压是否成功
    if [ $? -ne 0 ]; then
        echo "解压失败! 可能是密码错误或文件损坏"
        exit 1
    fi

    echo "解压成功!"
}

# 主函数
main() {
    local url="https://11.g2022cyk.top:8081/wp-content/cdn/ca.zip"  # 替换为实际URL
    local filename

    # 检查依赖
    check_dependencies

    # 下载文件
    filename=$(download_file "$url")

    # 解压文件
    extract_file "$filename"
}

# 运行主函数
main "$@"