# ruleset_geodata

面向 [mihomo（Clash.Meta）](https://github.com/MetaCubeX/mihomo) 与 [sing-box](https://github.com/SagerNet/sing-box) 的规则集 / geodata 自动构建仓库。

本仓库是 [DustinWin/ruleset_geodata](https://github.com/DustinWin/ruleset_geodata) 的 fork，与上游的差别在于**数据源换成自建管线**：

| 数据 | 来源仓库 | 分支 / release |
| --- | --- | --- |
| 域名列表 `.list` | [panyichen48737/domain-list-custom](https://github.com/panyichen48737/domain-list-custom) | 分支 `domains` / release `domains` |
| IP 列表 `.list` | [panyichen48737/geoip](https://github.com/panyichen48737/geoip) | 分支 `ips` / release `ips` |
| geoip geodata | [panyichen48737/geoip](https://github.com/panyichen48737/geoip) | release `mihomo-geodata` |
| 域名来源 | [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) | `master` |
| sing-box 内核 | [reF1nd/sing-box](https://github.com/reF1nd/sing-box) | 兼容版 + 最新版各一套 |

产物按类别推送到四个分支，并同步创建同名 release（release 资产可直接下载，分支适合 jsDelivr 引用）：

| 分支 / release | 内容 |
| --- | --- |
| `mihomo-geodata` | mihomo geodata：`geosite*.dat`、`geoip*`、`Country*.mmdb` |
| `mihomo-ruleset` | mihomo rule-set：`<tag>.mrs` + `<tag>.list` |
| `sing-box-ruleset` | sing-box rule_set（最新内核）：`<tag>.srs` + `<tag>.json` |
| `sing-box-ruleset-compatible` | sing-box rule_set（兼容旧内核）：`<tag>.srs` + `<tag>.json` |

---

## 一、geodata 文件

### geosite（域名库）

| 文件 | 包含的规则 |
| --- | --- |
| `geosite-all.dat` | `fakeip-filter`、`private`、`trackerslist`、`microsoft-cn`、`apple-cn`、`apple-proxy`、`google-cn`、`games-cn`、`games`、`ai`、`networktest`、`netflix`、`disney`、`hbo`、`primevideo`、`appletv`、`youtube`、`tiktok`、`bilibili`、`spotify`、`tld-proxy`、`tld-cn`、`proxy`、`cn` |
| `geosite-all-lite.dat` | 与 `geosite-all.dat` 相同的 tag，仅 `fakeip-filter` 换成精简内容 |
| `geosite.dat` | `fakeip-filter`、`private`、`trackerslist`、`microsoft-cn`、`apple-cn`、`google-cn`、`games-cn`、`ai`、`networktest`、`tld-proxy`、`proxy`、`cn` |
| `geosite-lite.dat` | 与 `geosite.dat` 相同的 tag，仅 `fakeip-filter` 换成精简内容 |

- `-lite` 不是「整体精简版」：tag 数量与体量几乎相同，差异**只在 `fakeip-filter` 这一个 tag**（正则部分不同，几 KB 量级）。
- 各 tag 的域名来源见 [第 二 节](#二rule-set-文件)。

### geoip（IP 库）

| 文件 | 包含的规则 |
| --- | --- |
| `geoip.dat` / `geoip.metadb` | `private`、`cn`、`games`、`telegram`、`netflix`、`media` |
| `Country.mmdb` | `private`、`cn`、`games`、`telegram`、`netflix`、`media` |
| `geoip-lite.dat` / `geoip-lite.metadb` / `Country-lite.mmdb` | `private`、`cn`、`telegram` |
| `Country-ASN.mmdb` | `netflix`、`telegram` |
| `geoip-all.dat`、`Country-all.mmdb`、`Country-ASN-all.mmdb` | 全量版：由源仓库镜像 [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip) 的 release 分支，tag 以源侧为准 |

> geoip 文件直接由 [panyichen48737/geoip](https://github.com/panyichen48737/geoip) 的 `mihomo-geodata` release 透传，本仓库不重新生成。
> `-all` 三个文件是**刻意的全量镜像**（不是残留），体积最大（合计数十 MB），只在确实需要 Loyalsoldier 全量数据时才用。

`geosite` 的每个 tag 对应 `geosite,<tag>`；`geoip` 的每个 tag 对应 `GEOIP,<tag>`（mihomo）/ `geoip` 规则（sing-box）。

---

## 二、rule-set 文件

`mihomo-ruleset`、`sing-box-ruleset`、`sing-box-ruleset-compatible` 三个分支包含相同的 32 个 tag，每个 tag 两份文件（mihomo 为 `.mrs` + `.list`，sing-box 为 `.srs` + `.json`）。

### 域名规则集

来源：[panyichen48737/domain-list-custom](https://github.com/panyichen48737/domain-list-custom) 的 `domains` 分支。

| tag | 说明 |
| --- | --- |
| `fakeip-filter` | fake-ip 过滤，含内置 `keyword:ntp` / `stun` / `time` |
| `fakeip-filter-lite` | fake-ip 过滤精简版（不含正则项） |
| `private` | 私有域名 |
| `trackerslist` | BT Tracker |
| `microsoft-cn` | 微软中国 |
| `apple-cn` | 苹果中国（直连） |
| `apple-proxy` | 苹果服务（走代理） |
| `google-cn` | 谷歌中国 |
| `games-cn` | 游戏中国 |
| `games` | 游戏平台 |
| `netflix` | Netflix |
| `disney` | Disney+ |
| `hbo` | HBO / Max |
| `primevideo` | Prime Video |
| `appletv` | Apple TV+ |
| `youtube` | YouTube |
| `tiktok` | TikTok |
| `bilibili` | 哔哩哔哩 |
| `spotify` | Spotify |
| `bing` | 必应搜索 |
| `onedrive` | OneDrive |
| `ai` | AI 服务 |
| `networktest` | 网络测试 |
| `tld-proxy` | 走代理的国际顶级域名 |
| `tld-cn` | 国内顶级域名 |
| `proxy` | 需要代理的域名汇总 |
| `cn` | 国内域名汇总 |

### IP 规则集

来源：[panyichen48737/geoip](https://github.com/panyichen48737/geoip) 的 `ips` 分支。

| tag | 说明 |
| --- | --- |
| `netflixip` | Netflix IP |
| `gamesip` | 游戏平台 IP |
| `privateip` | 私有 IP |
| `cnip` | 国内 IP |
| `telegramip` | Telegram IP |

---

## 三、下载地址

以 `geoip.dat` 为例，三种等价写法：

```text
# jsDelivr（推荐，走 CDN）
https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@mihomo-geodata/geoip.dat

# GitHub Raw
https://raw.githubusercontent.com/panyichen48737/ruleset_geodata/mihomo-geodata/geoip.dat

# Release 资产
https://github.com/panyichen48737/ruleset_geodata/releases/download/mihomo-geodata/geoip.dat
```

分支名对应第 二 节的四个：`mihomo-geodata`、`mihomo-ruleset`、`sing-box-ruleset`、`sing-box-ruleset-compatible`。

- mihomo rule-set：`@mihomo-ruleset/<tag>.mrs`
- sing-box rule_set：`@sing-box-ruleset/<tag>.srs`（旧内核用 `sing-box-ruleset-compatible`）

> jsDelivr 对分支路径有缓存，构建脚本在推送后会主动 purge；若刚更新完仍拿到旧文件，稍等几分钟或改用 Release / Raw。

---

## 四、在 mihomo 中使用

```yaml
geodata-mode: true
geox-url:
  geoip: "https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@mihomo-geodata/geoip.dat"
  geosite: "https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@mihomo-geodata/geosite.dat"
  mmdb: "https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@mihomo-geodata/Country.mmdb"

rules:
  - GEOIP,cn,DIRECT
  - GEOSITE,cn,DIRECT
  - GEOSITE,proxy,PROXY
```

使用 rule-set：

```yaml
rule-providers:
  proxy:
    type: http
    behavior: domain
    format: mrs
    interval: 86400
    url: "https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@mihomo-ruleset/proxy.mrs"
  cnip:
    type: http
    behavior: ipcidr
    format: mrs
    interval: 86400
    url: "https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@mihomo-ruleset/cnip.mrs"

rules:
  - RULE-SET,proxy,PROXY
  - RULE-SET,cnip,DIRECT
```

---

## 五、在 sing-box 中使用

```json
{
  "route": {
    "rule_set": [
      {
        "type": "remote",
        "tag": "proxy",
        "format": "binary",
        "url": "https://cdn.jsdelivr.net/gh/panyichen48737/ruleset_geodata@sing-box-ruleset/proxy.srs",
        "update_interval": "1d"
      }
    ],
    "rules": [
      { "rule_set": "proxy", "outbound": "proxy" }
    ]
  }
}
```

旧版内核请把分支换成 `sing-box-ruleset-compatible`。

---

## 六、自动构建

`.github/workflows/run.yml` 由三种方式触发：

- **数据仓库构建成功后主动触发**（`repository_dispatch: data-updated`）：首选路径。两个数据仓库的定时是 02:00 CST，只有它们跑完，本仓才拿到新数据。
- **定时兜底**：每天北京时间 03:00。dispatch 没到达时（例如未配置跨仓库 token）由它接管。
- **手动 / push**：手动 `workflow_dispatch`，或 `master` 上代码、`config/**` 变更。

三路并发会同时 force push 同一批分支，因此用 `concurrency` 串行化；内容与上次一致的分支/ release 会跳过推送，重复触发基本只损失一轮构建时间。

流程：

1. 从数据仓库下载域名 / IP 列表；
2. 用 v2fly 生成器产出 4 个 `geosite*.dat`；
3. 从 geoip release 取回 `geoip*` / `Country*.mmdb`；
4. 用 mihomo / sing-box 转换出 `.mrs` / `.srs`；
5. 校验产物完整性后推送到四个分支并更新 release，最后 purge jsDelivr 缓存。

tag 清单的唯一真源是 [`config/tags.sh`](config/tags.sh)。与它的一致性有两道 CI 校验：

- [`tools/check_readme.py`](tools/check_readme.py)：README 里的清单（`.github/workflows/readme-check.yml`）；
- [`tools/check_dat.py`](tools/check_dat.py)：构建产出的 4 个 `geosite*.dat` 里**实际**的 tag 集合（在 `Assert artifacts` 一步内）。

任一处漂移都会让 CI 失败，而不是悄悄上线。

---

## 七、注意事项

**同名 tag 在不同产物里的覆盖面不同。**

mihomo 的 `behavior: domain` 规则集（`.mrs` 和 text 格式的 `.list`）只能表达裸域名、`+.后缀` 和通配符，**装不下 `DOMAIN-KEYWORD` 和 `DOMAIN-REGEX`**；`geosite*.dat` 和 sing-box 的 rule_set 则保留这两类。因此同一个 tag：

- 要完整的 keyword / regex 语义 → 用 `geosite*.dat` 或 sing-box 的 rule_set；
- 只想按域名 / 后缀匹配、更省内存 → 用 mihomo 的 `.mrs`。

README 里的 tag 清单以 `config/tags.sh` 为准，人工改文档前请先改该文件。

---

## 八、来源与许可

- 域名数据：[v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)、[panyichen48737/domain-list-custom](https://github.com/panyichen48737/domain-list-custom)
- IP 数据：[panyichen48737/geoip](https://github.com/panyichen48737/geoip)（基于 MaxMind GeoLite2 等）
- 构建脚本与工作流：fork 自 [DustinWin/ruleset_geodata](https://github.com/DustinWin/ruleset_geodata)
- sing-box 内核：[SagerNet/sing-box](https://github.com/SagerNet/sing-box) / [reF1nd/sing-box](https://github.com/reF1nd/sing-box)

许可见 [LICENSE](LICENSE)。
