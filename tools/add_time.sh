#!/bin/bash

# 获取当前时间
current_time=$(date -d '+8 hours' '+%Y-%m-%d %H:%M:%S')

# 目标目录数组
directories=("../sing-box-ruleset" "../sing-box" "../clash" "../clash-ruleset")

# 遍历每个目标目录
for dir in "${directories[@]}"; do
  # 遍历目标目录下的所有文件
  for file in "$dir"/*; do
    [ -f "$file" ] && sed -i "1s/^/# 生成时间为 "$current_time"\n/" "$file"
  done
done

echo "时间已添加到所有文件开头。"
