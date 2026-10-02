#!/usr/bin/env python3
"""校验 README 里的 tag 清单与 config/tags.sh（单一真源）一致。

README 的表格和数据源清单曾经是手写的，和工作流里的数组各写一份，漂移过
（README 写着 ads/max/media/gfw，实际产出的是 hbo/bing/onedrive/tld-cn/gamesip）。
这个脚本让漂移在 CI 里失败，而不是悄悄上线。

用法: python3 tools/check_readme.py   （在仓库根目录执行）
退出码 0 = 一致，1 = 有漂移。
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "tags.sh"
README = ROOT / "README.md"

errors: list[str] = []
warnings: list[str] = []


def parse_config(path: Path) -> dict[str, list[str]]:
    """从 tags.sh 里取 NAME=(a b c) 形式的数组。"""
    arrays: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z0-9_]+)=\((.*)\)\s*$", line.strip())
        if m:
            arrays[m.group(1)] = m.group(2).split()
    required = {"GEODATA_ARCH1", "GEODATA_ARCH2", "GEODATA_ARCH3", "RULESET_DOMAINS", "RULESET_IPS"}
    missing = required - arrays.keys()
    if missing:
        sys.exit(f"config/tags.sh 缺少数组: {', '.join(sorted(missing))}")
    return arrays


def split_sections(text: str) -> tuple[str, str]:
    """按 '## 一、' / '## 二、' 两个二级标题切片。"""
    parts = re.split(r"^##\s+[一二]、", text, flags=re.MULTILINE)
    if len(parts) < 3:
        sys.exit("README 里找不到「## 一、」「## 二、」两个二级标题")
    return parts[1], parts[2]


ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|(.*)\|\s*$", re.MULTILINE)


def table_rows(section: str) -> dict[str, str]:
    """取 markdown 表格里第一列是 `name` 的行，返回 name -> 该行剩余单元格。"""
    return {m.group(1): m.group(2) for m in ROW.finditer(section)}


def tags_in(cell: str) -> set[str]:
    """取单元格里所有 `tag` 形式的引用。"""
    return set(re.findall(r"`([A-Za-z0-9!_-]+)`", cell))


def compare_rows(rows: dict[str, str], expected: dict[str, set[str]]) -> None:
    for name, want in expected.items():
        if name not in rows:
            errors.append(f"README 表格缺少 {name} 这一行")
            continue
        for tag in sorted(tags_in(rows[name]) - want):
            errors.append(f"{name} 的「包含的规则」写了 {tag}，但工作流不产出它")
        for tag in sorted(want - tags_in(rows[name])):
            errors.append(f"{name} 的「包含的规则」漏了 {tag}")


def main() -> int:
    arrays = parse_config(CONFIG)
    section_one, section_two = split_sections(README.read_text(encoding="utf-8"))

    arch1, arch2, arch3 = (
        arrays["GEODATA_ARCH1"],
        arrays["GEODATA_ARCH2"],
        arrays["GEODATA_ARCH3"],
    )
    # geodata 侧：-lite 变体只是把 fakeip-filter 换成精简内容，tag 名不变；
    # mini 用 cn-lite 的内容生成，但 tag 名被改回 cn（见 run.yml）。
    rows_one = table_rows(section_one)
    compare_rows(
        rows_one,
        {
            "geosite-all.dat": {"fakeip-filter"} | set(arch1),
            "geosite.dat": {"fakeip-filter"} | set(arch2),
            "geosite-mini.dat": (set(arch3) - {"cn-lite"}) | {"cn"},
        },
    )
    # -lite 两行内容与基名相同，README 里用文字说明，只校验存在
    for name in ("geosite-all-lite.dat", "geosite-lite.dat"):
        if name not in rows_one:
            errors.append(f"README 表格缺少 {name} 这一行")

    # rule-set 侧：第二节两个表格的第一列即为全部 tag
    ruleset_tags = set(arrays["RULESET_DOMAINS"]) | set(arrays["RULESET_IPS"])
    documented = set(table_rows(section_two))
    for tag in sorted(documented - ruleset_tags):
        errors.append(f"README 第二节列了 {tag}，但它不是本仓库产出的 tag")
    for tag in sorted(ruleset_tags - documented):
        warnings.append(f"README 第二节没提到 {tag}")

    for w in warnings:
        print(f"警告: {w}")
    for e in errors:
        print(f"错误: {e}")

    if errors:
        print(f"\n{len(errors)} 处漂移。改 config/tags.sh 后同步更新 README，或反过来。")
        return 1
    print("README 与 config/tags.sh 一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
