#!/usr/bin/env bash
# investment-support-kun 実行コンテナの entrypoint。
#   1. (任意) 外向き通信の blocklist ファイアウォールを初期化
#   2. 非 root ユーザ claude に降格してコマンドを実行
#
# 環境変数:
#   ENABLE_FIREWALL=1  ... ファイアウォールを有効化（デフォルト1。NET_ADMIN が必要）
#   RUN_AS_USER=claude ... 実行ユーザ（デフォルト claude）
set -euo pipefail

ENABLE_FIREWALL="${ENABLE_FIREWALL:-1}"
RUN_AS_USER="${RUN_AS_USER:-claude}"

current_uid="$(id -u)"

run_firewall() {
    if [ "${ENABLE_FIREWALL}" != "1" ]; then
        echo "[entrypoint] ファイアウォールは無効化されています (ENABLE_FIREWALL=${ENABLE_FIREWALL})" >&2
        return 0
    fi
    echo "[entrypoint] 外向き通信 blocklist を初期化します..." >&2
    if [ "${current_uid}" -eq 0 ]; then
        /usr/local/bin/init-firewall.sh || {
            echo "[entrypoint] ファイアウォール初期化に失敗しました。NET_ADMIN 権限を確認してください。" >&2
            exit 1
        }
    else
        sudo -n /usr/local/bin/init-firewall.sh || {
            echo "[entrypoint] ファイアウォール初期化に失敗しました。NET_ADMIN 権限を確認してください。" >&2
            exit 1
        }
    fi
}

run_firewall

if [ "${current_uid}" -eq 0 ]; then
    # root で起動した場合は claude ユーザへ降格して実行
    exec gosu "${RUN_AS_USER}" "$@"
else
    exec "$@"
fi
