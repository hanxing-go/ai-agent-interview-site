#!/bin/bash
# AI Agent 面经每日自动抓取脚本
# 每天 9:00 运行，拉取牛客网最新 AI Agent 面经，追加到网站
# 由小 Miku 维护 ♪

set -e
WORKDIR="${WORKDIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
LOGFILE="${LOGFILE:-$WORKDIR/crawl.log}"
DATA_DIR="${DATA_DIR:-$WORKDIR/data}"
mkdir -p "$DATA_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"; }

log "========== 开始每日抓取 =========="

# 1. 抓取牛客网 AI Agent 相关面经
URLS=(
  "https://www.nowcoder.com/search?type=post&query=AI+Agent+%E9%9D%A2%E7%BB%8F+MCP"
  "https://www.nowcoder.com/search?type=post&query=AI+Agent+%E9%9D%A2%E8%AF%95+RAG"
  "https://www.nowcoder.com/search?type=post&query=Agent+%E5%BC%80%E5%8F%91+%E9%9D%A2%E8%AF%95+2026"
)

TODAY=$(date +%Y-%m-%d)
RAW_FILE="$DATA_DIR/raw-$TODAY.txt"
> "$RAW_FILE"

for url in "${URLS[@]}"; do
  log "正在抓取: $url"
  curl -s -L --max-time 30 \
    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
    "$url" 2>/dev/null | \
    python3 -c "
import sys, re, html
text = sys.stdin.read()
# 提取标题和时间
titles = re.findall(r'<a[^>]*href=\"(/discuss/\d+[^\"]*)\"[^>]*>(.*?)</a>', text, re.DOTALL)
for link, title in titles:
    t = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
    if t and len(t) > 10:
        print(f'https://www.nowcoder.com{link} | {t[:100]}')
" >> "$RAW_FILE" 2>/dev/null || true
done

# 2. 统计
NEW_COUNT=$(wc -l < "$RAW_FILE")
log "抓取到 $NEW_COUNT 条潜在新面经链接"

# 3. 去重，和昨天对比
YESTERDAY=$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "unknown")
YESTERDAY_FILE="$DATA_DIR/raw-$YESTERDAY.txt"
if [ -f "$YESTERDAY_FILE" ] && [ "$NEW_COUNT" -gt 0 ]; then
  NEW_LIST="$DATA_DIR/new-$TODAY.txt"
  comm -23 <(sort "$RAW_FILE") <(sort "$YESTERDAY_FILE") > "$NEW_LIST" 2>/dev/null || true
  ACTUAL_NEW=$(wc -l < "$NEW_LIST")
  log "相比昨天新增: $ACTUAL_NEW 条"
else
  cp "$RAW_FILE" "$DATA_DIR/new-$TODAY.txt" 2>/dev/null || true
  ACTUAL_NEW=$NEW_COUNT
fi

# 4. 更新网站时间戳
sed -i "s|<span class=\"stat-num\" id=\"update-date\">.*</span>|<span class=\"stat-num\" id=\"update-date\">$(date +%m-%d)</span>|" "$WORKDIR/index.html"
if [ -n "${PUBLIC_HTML_DIR:-}" ]; then
  mkdir -p "$PUBLIC_HTML_DIR"
  cp "$WORKDIR/index.html" "$PUBLIC_HTML_DIR/index.html"
fi

log "网站已更新，面经数: $ACTUAL_NEW 条新增"
log "========== 抓取完成 =========="

echo "$ACTUAL_NEW"
