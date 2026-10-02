#!/bin/bash
# 把 ./rules/<tag>/<tag>.list 转成 sing-box rule_set 的 .json + .srs
#
# 用法: ./convert.sh <ruleset version>
#   version 是 sing-box 规则的 schema 版本（一个整数），从命令行传入。
#   旧实现靠 sed 改自己的源码来注入 version：抓文档失败时 env 为空，会把
#   "version": 1 改成 "version":  并静默产出非法 srs。现在空值直接失败。
set -euo pipefail

version="${1:-}"
case "${version}" in
  ''|*[!0-9]*)
    echo "用法: $0 <ruleset version 整数>；实际拿到 '${version}'" >&2
    exit 1
    ;;
esac

command -v python3 >/dev/null || { echo "需要 python3" >&2; exit 1; }

shopt -s nullglob
count=0

for dir in ./rules/*/; do
  tag="$(basename "${dir}")"
  src="${dir}${tag}.list"
  [ -f "${src}" ] || { echo "缺少 ${src}" >&2; exit 1; }

  # 一次读取按类型分流（旧实现是 7 遍 cat|awk），交给 python 组装 JSON（转义/合法性由 json 模块保证）
  python3 - "${version}" "${src}" "${tag}.json" <<'PY'
import json
import sys

version, src, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]

package, process, exe = [], [], []
domain, suffix, keyword, regex, ipcidr = [], [], [], [], []

with open(src, encoding="utf-8") as f:
    for raw in f:
        line = raw.rstrip("\n")
        if line.startswith("PROCESS-NAME,"):
            v = line[13:]
            if ".exe" in v:
                exe.append(v)
            elif "/" in v:
                continue          # 路径形式的进程名，sing-box 用不了
            elif "." in v:
                package.append(v)  # android 包名
            else:
                process.append(v)
        elif line.startswith("DOMAIN,"):
            domain.append(line[7:])
        elif line.startswith("DOMAIN-SUFFIX,"):
            suffix.append(line[14:])
        elif line.startswith("DOMAIN-KEYWORD,"):
            keyword.append(line[15:])
        elif line.startswith("DOMAIN-REGEX,"):
            regex.append(line[13:])
        elif line.startswith("IP-CIDR") and "," in line:
            # IP-CIDR 与 IP-CIDR6 都要（v6 占 ip 列表的一半以上）
            ipcidr.append(line.split(",")[-1])

# 分组与原产物一致：package_name、process_name 各自一个对象（或语义），
# domain 匹配器系列合并进同一个对象
rules = []
if package:
    rules.append({"package_name": package})
if process or exe:
    rules.append({"process_name": process + exe})
domain_rule = {}
if domain:
    domain_rule["domain"] = domain
if suffix:
    domain_rule["domain_suffix"] = suffix
if keyword:
    domain_rule["domain_keyword"] = keyword
if regex:
    domain_rule["domain_regex"] = regex
if ipcidr:
    domain_rule["ip_cidr"] = ipcidr
if domain_rule:
    rules.append(domain_rule)

with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump({"version": version, "rules": rules}, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

  ./sing-box rule-set compile --output "${tag}.srs" "${tag}.json"

  # 不删 ./rules/<tag>/：run.yml 会用两个内核（兼容 / 最新）把同一份源各跑一遍，
  # 删了第二遍就找不到 tag。收尾由 run.yml 的 `rm -rf ./tools/rules` 负责。
  count=$((count + 1))
done

[ "${count}" -gt 0 ] || { echo "./rules/ 下没有找到任何 tag" >&2; exit 1; }
echo "已转换 ${count} 个 rule_set"
