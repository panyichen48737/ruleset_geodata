#!/bin/bash
# 标签清单单一真源。
# 被 .github/workflows/run.yml（source 后使用）和 tools/check_readme.py（解析后比对 README）共同读取。
# 改这里就够了，不要再往 run.yml 里内联数组 —— README 的漂移就是这么来的。

# geodata：两个 arch 分别对应 geosite-all.dat / geosite.dat
# （-lite 变体复用同一 arch，只把 fakeip-filter 换成 fakeip-filter-lite）
GEODATA_ARCH1=(private trackerslist microsoft-cn apple-cn apple-proxy google-cn games-cn games ai networktest netflix disney hbo primevideo appletv youtube tiktok bilibili spotify tld-proxy tld-cn proxy cn)
GEODATA_ARCH2=(private trackerslist microsoft-cn apple-cn google-cn games-cn ai networktest tld-proxy proxy cn)

# rule-set：domain 列表来自 domain-list-custom，ip 列表来自 geoip
RULESET_DOMAINS=(fakeip-filter fakeip-filter-lite private trackerslist microsoft-cn apple-cn apple-proxy google-cn games-cn games netflix disney hbo primevideo appletv youtube tiktok bilibili spotify bing onedrive ai networktest tld-proxy tld-cn proxy cn)
RULESET_IPS=(netflixip gamesip privateip cnip telegramip)
