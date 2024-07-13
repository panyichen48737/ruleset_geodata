#!/bin/bash

# 获取当前时间（调整为东八区时间）
current_time=$(date -d '+8 hours' '+%Y-%m-%d %H:%M:%S')

# 目标目录数组
directories=("../sing-box-ruleset" "../sing-box" "../clash" "../clash-ruleset")

# 遍历每个目标目录
for dir in "${directories[@]}"; do
  echo "正在处理目录: $dir"
  # 遍历目标目录下的所有文件
  for file in "$dir"/*; do
    if [ -f "$file" ]; then
      case "$file" in
        *.json|*.list|*.yaml)
          # 使用 sed 在文件开头插入带有当前时间的注释
          sed -i "1i # 生成时间为 $current_time" "$file"
          echo "已处理文件: $file"
          ;;
      esac
    fi
  done
done

echo "所有符合条件的文件已处理完毕。"
