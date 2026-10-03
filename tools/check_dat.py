#!/usr/bin/env python3
"""校验 geosite*.dat 里的 tag 集合与 config/tags.sh（单一真源）一致。

`Assert artifacts` 只查文件存在且非空；tag 名字对不对、有没有静默丢一个 tag，从来没被校验过。
历史上这个项目正是被"清单漂移"坑过，所以把 tag 级校验也放进 CI。

档结构：GeoSiteList{ repeated GeoSite entry = 1 }，
GeoSite{ string country_code = 1; repeated Domain domain = 2 }。
这里只解出每个 geosite 的 country_code 和 domain 条数，不做完整 protobuf 实现。

用法: python3 tools/check_dat.py <geodata 目录>   （目录里应有 geosite*.dat）
退出码 0 = 一致，1 = 有漂移。
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "tags.sh"

errors: list[str] = []
warnings: list[str] = []


def varint(data: bytes, i: int) -> tuple[int, int]:
    result = shift = 0
    while True:
        b = data[i]
        i += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, i
        shift += 7


def parse_geosites(data: bytes) -> dict[str, int]:
    """返回 {tag: domain 条数}。"""
    out: dict[str, int] = {}
    i, n = 0, len(data)
    while i < n:
        if data[i] != 0x0A:
            raise ValueError(f"offset {i}: 期望 GeoSiteList.entry(0x0a)，实际 {data[i]:#x}")
        ln, i = varint(data, i + 1)
        msg, i = data[i:i + ln], i + ln

        j, tag, count = 0, None, 0
        while j < len(msg):
            key = msg[j]
            field, wire = key >> 3, key & 0x07
            j += 1
            if wire == 2:
                ln2, j = varint(msg, j)
                val, j = msg[j:j + ln2], j + ln2
            elif wire == 0:
                _, j = varint(msg, j)
                val = b""
            elif wire == 5:
                val, j = b"", j + 4
            elif wire == 1:
                val, j = b"", j + 8
            else:
                raise ValueError(f"GeoSite 里出现未知 wire type {wire}")
            if field == 1:
                tag = val.decode("utf-8")
            elif field == 2:
                count += 1
        if tag is None:
            raise ValueError("GeoSite 里没有 country_code")
        out[tag.upper()] = count
    return out


def parse_config(path: Path) -> dict[str, list[str]]:
    arrays: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z0-9_]+)=\((.*)\)\s*$", line.strip())
        if m:
            arrays[m.group(1)] = m.group(2).split()
    required = {"GEODATA_ARCH1", "GEODATA_ARCH2", "GEODATA_ARCH3"}
    missing = required - arrays.keys()
    if missing:
        sys.exit(f"config/tags.sh 缺少数组: {', '.join(sorted(missing))}")
    return arrays


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(f"用法: {sys.argv[0]} <geodata 目录>")
    geodata = Path(sys.argv[1])
    arrays = parse_config(CONFIG)
    a1 = {t.upper() for t in arrays["GEODATA_ARCH1"]}
    a2 = {t.upper() for t in arrays["GEODATA_ARCH2"]}
    a3 = {t.upper() for t in arrays["GEODATA_ARCH3"]}

    fp = {"FAKEIP-FILTER"}
    expected = {
        "geosite-all.dat": fp | a1,
        "geosite-all-lite.dat": fp | a1,
        "geosite.dat": fp | a2,
        "geosite-lite.dat": fp | a2,
        # mini 用 cn-lite 的内容，但 tag 名被改回 cn（见 run.yml）
        "geosite-mini.dat": (a3 - {"CN-LITE"}) | {"CN"},
    }

    parsed: dict[str, dict[str, int]] = {}
    for name, want in expected.items():
        path = geodata / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"{name} 缺失或为空")
            continue
        try:
            got = parse_geosites(path.read_bytes())
        except ValueError as e:
            errors.append(f"{name} 解析失败（格式可能已变）: {e}")
            continue
        parsed[name] = got
        for tag in sorted(got.keys() - want):
            errors.append(f"{name} 多出 tag {tag}")
        for tag in sorted(want - got.keys()):
            errors.append(f"{name} 缺少 tag {tag}")
        if not got:
            errors.append(f"{name} 里没有任何 tag")

    # mini 的 CN 应当是 cn-lite 的精简内容，条目数必须明显少于完整 cn
    # （这条防止有人"顺手修正"那个 mv cn-lite cn 的改名）
    mini, full = parsed.get("geosite-mini.dat", {}), parsed.get("geosite.dat", {})
    if "CN" in mini and "CN" in full and mini["CN"] >= full["CN"]:
        errors.append(f"geosite-mini.dat 的 CN 有 {mini['CN']} 条，不少于 geosite.dat 的 {full['CN']} 条，"
                      "cn-lite 改名可能被改坏了")

    for name, got in parsed.items():
        print(f"{name}: {len(got)} 个 tag")
    for w in warnings:
        print(f"警告: {w}")
    for e in errors:
        print(f"错误: {e}")
    if errors:
        return 1
    print("geosite tag 与 config/tags.sh 一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
