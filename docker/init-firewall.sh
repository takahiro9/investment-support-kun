#!/usr/bin/env bash
# 外向き通信の blocklist(denylist) ファイアウォール。
# Claude Code を auto approve (--dangerously-skip-permissions) で動かす際、
# 想定外の宛先への通信を遮断して被害範囲をコンテナ内に閉じ込める。
#
# 方針:
#   - OUTPUT のデフォルトを ACCEPT（一旦全許可）
#   - loopback / 確立済みコネクション / DNS は許可
#   - 下記 BLOCKED_DOMAINS への通信のみ拒否
#   - BLOCKED_DOMAINS への名前解決は dnsmasq が担い、問い合わせ結果のIPを
#     都度 ipset(blocked-domains) に動的追加する（IPローテーションに対応するため）
#
# 注意:
#   allowlist 方式と比べて安全性は大きく下がる（未知の攻撃者ドメインへの通信は
#   デフォルトで通ってしまう）。BLOCKED_DOMAINS は「明らかに悪用されやすい」
#   既知カテゴリを塞ぐだけで、網羅的な防御にはならない。
#   - BLOCKED_DOMAINS（このファイルを直接編集）
#   - ADDITIONAL_BLOCKED_DOMAINS（docker-compose.yml の environment、カンマ区切り）
# で少しずつ育てていくこと。
set -euo pipefail

BLOCKED_DOMAINS=(
    # --- ペーストサイト（機密情報の持ち出し先として使われやすい） ---
    "pastebin.com"
    "paste.ee"
    "hastebin.com"
    "ghostbin.com"
    "dpaste.com"
    "0x0.st"

    # --- 匿名/無認証のファイルアップロード（持ち出し先） ---
    "transfer.sh"
    "file.io"
    "anonfiles.com"
    "gofile.io"
    "catbox.moe"

    # --- webhook / request bin・OOB interaction（SSRF・持ち出し検証用途） ---
    "webhook.site"
    "requestbin.com"
    "requestcatcher.com"
    "burpcollaborator.net"
    "interact.sh"
    "oastify.com"
    "canarytokens.com"

    # --- URL短縮（宛先を隠すのに使われやすい） ---
    "bit.ly"
    "tinyurl.com"
    "is.gd"
    "t.co"
    "ow.ly"

    # --- IPロガー / トラッカー ---
    "grabify.link"
    "iplogger.org"
    "2no.co"

    # --- トンネリング（コンテナ内サービスの外部公開・リバースシェル経路になりうる） ---
    "ngrok.io"
    "ngrok-free.app"
    "ngrok.app"
    "localtunnel.me"
    "serveo.net"
    "localhost.run"
    "tunnelto.dev"
    "pagekite.me"
)

# 環境変数からの追加拒否ドメイン（カンマ区切り）
if [ -n "${ADDITIONAL_BLOCKED_DOMAINS:-}" ]; then
    IFS=',' read -ra _extra <<< "${ADDITIONAL_BLOCKED_DOMAINS}"
    for d in "${_extra[@]}"; do
        d="$(echo "$d" | xargs)"  # trim
        [ -n "$d" ] && BLOCKED_DOMAINS+=("$d")
    done
fi

echo "[firewall] 既存ルール(filterのみ)をリセットします"
iptables -F
iptables -X
# 重要: nat / mangle は flush しない。
#   Docker の組み込み DNS リゾルバ (127.0.0.11) は nat テーブルの DNAT ルールで
#   成立しているため、ここを消すとコンテナ内の名前解決が全て壊れる。
ipset destroy blocked-domains 2>/dev/null || true

# loopback
iptables -A INPUT  -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# DNS（名前解決に必要）
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# 確立済み / 関連コネクションの戻り
iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 拒否 IP を格納する ipset
ipset create blocked-domains hash:net

# 拒否ドメインは dnsmasq + ipset の動的連携で管理する。
# 起動時に一度だけ dig で解決してIPを固定登録する方式だと、
#   - 解決した瞬間のIPしか登録されず、ロードバランサ配下でIPが
#     入れ替わると新しいIPをすり抜けてしまう
# という問題があるため、dnsmasq に拒否ドメインへの問い合わせ結果を都度 ipset へ
# 追加させる方式にしている。以降、コンテナ内の名前解決はすべて dnsmasq(127.0.0.1)
# 経由になり、常駐プロセスなので稼働中ずっと反映され続ける。

# 再実行時に自分自身(127.0.0.1)を上流として参照してしまわないよう、
# オリジナルの resolv.conf は初回のみ退避しておく
if [ ! -f /etc/resolv.conf.orig ]; then
    cp /etc/resolv.conf /etc/resolv.conf.orig
fi
upstream_servers="$(awk '/^nameserver/{print $2}' /etc/resolv.conf.orig)"
if [ -z "$upstream_servers" ]; then
    echo "[firewall] 警告: 上流DNSサーバを resolv.conf.orig から取得できませんでした" >&2
fi

echo "[firewall] dnsmasq を設定します (拒否ドメイン数: ${#BLOCKED_DOMAINS[@]})"
DNSMASQ_CONF=/etc/dnsmasq.d/blocked-domains.conf
mkdir -p /etc/dnsmasq.d
{
    echo "listen-address=127.0.0.1"
    echo "bind-interfaces"
    echo "no-resolv"
    echo "no-hosts"
    echo "cache-size=1000"
    for s in $upstream_servers; do
        echo "server=${s}"
    done
    # 元の上流が不調な場合のフォールバック
    echo "server=1.1.1.1"
    echo "server=8.8.8.8"
    for domain in "${BLOCKED_DOMAINS[@]}"; do
        # このドメインへの問い合わせで返ってきたIPを都度 blocked-domains に追加する
        echo "ipset=/${domain}/blocked-domains"
    done
} > "$DNSMASQ_CONF"

# 既存の dnsmasq があれば止めてから起動し直す（再実行時の安全策）
if [ -f /run/dnsmasq.pid ] && kill -0 "$(cat /run/dnsmasq.pid)" 2>/dev/null; then
    kill "$(cat /run/dnsmasq.pid)"
    sleep 1
fi
if dnsmasq --conf-file="$DNSMASQ_CONF" --pid-file=/run/dnsmasq.pid; then
    # dnsmasq が起動できた場合のみ、コンテナ内の名前解決を dnsmasq 経由に切り替える。
    # 失敗時に切り替えると 127.0.0.1 に誰も listen していない状態になり、
    # 名前解決が全滅してしまうため元の resolv.conf のままにしておく。
    cat > /etc/resolv.conf <<'EOF'
nameserver 127.0.0.1
EOF
else
    echo "[firewall] 警告: dnsmasq の起動に失敗しました。ipsetへの動的追加は無効なままresolv.confは変更しません。" >&2
fi

# blocklist にマッチする宛先のみ拒否
iptables -A OUTPUT -m set --match-set blocked-domains dst -j DROP

# デフォルトポリシー: 受信/転送は DROP、送信は一旦全許可(ACCEPT)
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

echo "[firewall] 完了。拒否ドメイン数: ${#BLOCKED_DOMAINS[@]}（デフォルトポリシー: OUTPUT ACCEPT）"
