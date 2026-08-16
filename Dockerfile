# investment-support-kun 実行コンテナ。
#
# 目的: Claude Code を隔離された Ubuntu コンテナ内で `--dangerously-skip-permissions`
#       (auto approve) で安全に動かす。安全性は次の2点で担保する。
#   1. コンテナによるホストからの隔離（ファイルシステム/プロセス）
#   2. entrypoint で初期化する外向き通信の blocklist（docker/init-firewall.sh）
#
# `webapp` サービス（scripts/serve.py + webapp/）も同じイメージを使う。
# ダッシュボードから起動する Claude Code マルチセッションパネルが `claude` CLI を
# サブプロセスとして spawn するため、webapp 側にも Node.js / claude CLI が必要。
#
# Claude Code は root では --dangerously-skip-permissions を拒否するため、
# 非 root ユーザ `claude` を作成して実行する。
FROM ubuntu:24.04

ARG NODE_MAJOR=22
ARG USERNAME=claude
ARG USER_UID=1000
ARG USER_GID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Asia/Tokyo

# 基本ツール + ファイアウォール用パッケージ
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg sudo git openssh-client less \
        jq ripgrep fd-find build-essential python3 python3-venv \
        iptables ipset dnsutils iproute2 dnsmasq \
        locales tzdata gosu \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Node.js (NodeSource) — Claude Code CLI (npm 配布) 実行用。
# investment-support-kun 自体のアプリコードは Python (uv) のみで Node は使わない。
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g npm@latest

# uv (Python パッケージマネージャ) を /usr/local/bin に配置。
# pyproject.toml / uv.lock で管理されているため `uv run` / `uv sync` で使う。
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

# Claude Code CLI を最新版に上げたい場合はこの値を変えてビルドし直す
# （コマンド例は docker-compose.yml の使い方コメント参照）:
#   docker compose build --build-arg CACHEBUST=$(date +%s) claude
ARG CACHEBUST=1

# Claude Code 本体。
# npm 12 の allow-scripts 機構によりデフォルトで postinstall がブロックされ、
# ネイティブバイナリが正しくセットアップされない（`exec format error` になる）ため、
# 明示的にこのパッケージの install scripts を許可する。
RUN npm install -g --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code

# 非 root ユーザ。ubuntu:24.04 には UID 1000 の ubuntu ユーザが既にいるため、
# 衝突する場合は既存ユーザをリネームして再利用する。
RUN if getent passwd ${USER_UID} >/dev/null; then \
        existing=$(getent passwd ${USER_UID} | cut -d: -f1); \
        usermod -l ${USERNAME} -d /home/${USERNAME} -m ${existing} 2>/dev/null || true; \
        groupmod -n ${USERNAME} $(getent group ${USER_GID} | cut -d: -f1) 2>/dev/null || true; \
    else \
        groupadd --gid ${USER_GID} ${USERNAME}; \
        useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME}; \
    fi \
    && mkdir -p /home/${USERNAME}/.claude /workspace /workspace/.venv \
    && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME} /workspace \
    # entrypoint が firewall 初期化のためだけに root 権限を使えるよう限定的に許可
    && printf '%s\n' \
        "${USERNAME} ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" \
        > /etc/sudoers.d/claude-privileged \
    && chmod 0440 /etc/sudoers.d/claude-privileged

# fd-find は Ubuntu では fdfind という名前になるため別名を張る
RUN ln -sf "$(command -v fdfind)" /usr/local/bin/fd

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod 0755 /usr/local/bin/entrypoint.sh /usr/local/bin/init-firewall.sh

# 以降はデフォルトで非 root ユーザ claude として動作する。
# entrypoint は sudoers で許可された init-firewall.sh のみ root 権限で実行する。
USER ${USERNAME}

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# `docker compose up` でコンテナを起動したまま待機させる。
# 実作業は `docker compose exec claude bash` で入り、
# その中で `claude --dangerously-skip-permissions` を実行する想定。
CMD ["sleep", "infinity"]
