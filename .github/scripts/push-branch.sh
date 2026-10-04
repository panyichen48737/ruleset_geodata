#!/bin/bash
# push_branch <branch> <dir> <commit message>
#
# 把 <dir> 的内容推到 <branch>。先浅拉上次的分支再在其上提交，这样 git 有 delta base，
# 日间只有少量变化的 .dat/.mrs 不需要全量重传（旧写法每次 git init 都是全新根提交）。
# 内容与上次完全一致时跳过推送，并把 changed=true/false 写进 $GITHUB_OUTPUT 供后续步骤门控。
#
# 调用方需提供 GH_TOKEN 环境变量（GITHUB_ACTOR / GITHUB_REPOSITORY 是 Actions 默认变量）。
push_branch() {
  local branch="$1" dir="$2" message="$3"
  local changed=false

  [ -n "${GH_TOKEN}" ] || { echo "::error::GH_TOKEN 未设置"; exit 1; }

  cd "$dir" || exit 1
  git init -q
  git config --local user.email "github-actions[bot]@users.noreply.github.com"
  git config --local user.name "github-actions[bot]"
  git remote add origin "https://${GITHUB_ACTOR}:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}"

  # 分支还不存在（首次运行）时 fetch 会失败，此时直接建根提交。
  # refspec 必须写成 refs/heads/：本仓每条产物分支都有一个同名 tag（就是它 release 的 tag），
  # 而 git 解析短名时 refs/tags/ 优先于 refs/heads/ —— 不限定就会一直拉到那个冻结在两年前的
  # tag 当基准，"内容无变化"永远不成立，delta base 也形同虚设。
  if git fetch -q --depth=1 origin "refs/heads/${branch}" 2>/dev/null; then
    git reset -q --soft FETCH_HEAD
  fi

  git add -A
  if git diff --cached --quiet; then
    echo "${branch}: 内容无变化，跳过推送"
  else
    git commit -q -m "${message}"
    git push -q -f origin "HEAD:refs/heads/${branch}"
    changed=true
    echo "${branch}: 已推送"
  fi

  echo "changed=${changed}" >> "${GITHUB_OUTPUT}"
}
