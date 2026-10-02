#!/bin/bash
# prune_release <tag> <dir>
#
# 删除 release <tag> 里文件名不在 <dir> 中的资产。
# svenstaro/upload-release-action 只覆盖同名文件，源侧改名或删除后，旧资产会永远留在
# release 里（现状：Country.mmdb.1、Country-ASN*.mmdb、geoip-all.* 等 13 个残留）——
# 它们既不会被 purged，也不会被覆盖。分支是 force push，不会累积，只有 release 会。
#
# 调用方需提供 GH_TOKEN（GITHUB_REPOSITORY 是 Actions 默认变量）。
prune_release() {
  local tag="$1" dir="$2"
  local api="https://api.github.com/repos/${GITHUB_REPOSITORY}"
  local auth="Authorization: Bearer ${GH_TOKEN}"

  [ -n "${GH_TOKEN}" ] || { echo "::error::GH_TOKEN 未设置"; exit 1; }

  local rel_id
  rel_id=$(curl -fsSL --retry 3 --retry-delay 5 -H "${auth}" "${api}/releases/tags/${tag}" \
    | jq -r '.id // empty')
  [ -n "${rel_id}" ] || { echo "::warning::找不到 release ${tag}，跳过清理"; return 0; }

  local keep
  keep=$(mktemp)
  (cd "$dir" && printf '%s\n' *) > "${keep}"

  local removed=0 aid aname
  while IFS=$'\t' read -r aid aname; do
    [ -n "${aid}" ] || continue
    if ! grep -Fxq "${aname}" "${keep}"; then
      curl -fsSL --retry 3 --retry-delay 5 -X DELETE -H "${auth}" \
        "${api}/releases/assets/${aid}" > /dev/null
      echo "  - 删除残留资产 ${tag}/${aname}"
      removed=$((removed + 1))
    fi
  done < <(curl -fsSL --retry 3 --retry-delay 5 -H "${auth}" \
    "${api}/releases/${rel_id}/assets?per_page=100" | jq -r '.[] | "\(.id)\t\(.name)"')

  rm -f "${keep}"
  echo "${tag}: 清理了 ${removed} 个残留资产"
}
