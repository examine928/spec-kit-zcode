# ZCode 适配补丁维护指南

> 本文档覆盖四件事：
> 1. **新电脑部署（私有 fork，推荐）**：完全脱离官方，从你自己的 Git 仓库装 → 见「新电脑部署」
> 2. **在项目中初始化**：zcode/codex/claude/qwen/qoder 等 agent 如何装 openspec + spec-kit → 见「在项目中初始化」
> 3. **补丁内容**：openspec / spec-kit 源码具体改了什么 → 见「一、openspec 补丁」起的章节
> 4. **长期维护**：源码更新如何重新打补丁、回滚 → 见第三、四、五章
>
> **补丁背景**：两个源码仓库（OpenSpec / spec-kit）均为 **MIT 协议**，已 fork 并打 zcode 补丁到本地 `zcode-support` 分支，可自由私有部署。

---

## 背景知识

### 为什么需要补丁？

openspec 和 spec-kit 都通过「集成清单」列出支持的 AI agent。ZCode 尚未进入官方清单，所以：

- `openspec init --tools zcode` → 不认识 zcode
- `specify init --integration zcode` → 不认识 zcode

打补丁的本质 = **在两个工具的「集成清单」里各加一条 ZCode 条目**。

### 两者并存无冲突

| 维度 | openspec | spec-kit |
|---|---|---|
| CLI 命令 | `openspec` | `specify` |
| 规格目录 | `openspec/` | `specs/` + `.specify/` |
| Skill 前缀 | `openspec-*` | `speckit-*` |
| Skill 落点 | `.zcode/skills/openspec-*/` | `.zcode/skills/speckit-*/` |

命令前缀不同、数据目录不同，可安全并存。

---

## 在项目中初始化（多 agent）

> 本章回答：「我的项目要用某个 agent，怎么把 openspec / spec-kit 装进去？」
>
> 支持的 agent：**zcode、codex、claude code、qwen code、qoder**（共 5 个）。

### ⚠️ 两个工具的关键差异（先看这个）

| 维度 | openspec | spec-kit |
|---|---|---|
| 多 agent 一次装 | ✅ `--tools a,b,c` 逗号分隔 | ❌ 只能逐个装 |
| 首次装 | `openspec init --tools <...>` | `specify init --integration <one> --here` |
| 叠加装（已有项目） | 重跑 `init --tools <含新agent>` | `specify integration install <key>` |
| 各 agent 落点一致 | ✅ 都是 `.<agent>/skills/` | ⚠️ **不一致**（见下表） |

### 各 agent 的 key 和落点（实测）

| Agent | openspec key | spec-kit key | openspec 落点 | spec-kit 落点 | spec-kit 交付模式 |
|---|---|---|---|---|---|
| **ZCode** | `zcode` | `zcode` | `.zcode/skills/openspec-*` | `.zcode/skills/speckit-*` | skills |
| **Claude Code** | `claude` | `claude` | `.claude/skills/openspec-*` | `.claude/skills/speckit-*` | skills |
| **Codex** | `codex` | `codex` | `.codex/skills/openspec-*` | **`.agents/skills/speckit-*`** ⚠️ | skills |
| **Qwen Code** | `qwen` | `qwen` | `.qwen/skills/openspec-*` | 需本机装 qwen-code CLI | skills |
| **Qoder** | `qoder` | `qodercli` ⚠️ | `.qoder/skills/openspec-*` | `.qoder/commands/speckit.*.md` | **commands**（非 skills） |

> ⚠️ **三个坑**：
> 1. **Qoder 的 key 两边不同**：openspec=`qoder`，spec-kit=`qodercli`
> 2. **spec-kit 的 Codex** 落到 `.agents/skills/`，不是 `.codex/skills/`
> 3. **spec-kit 的 Qwen** 需本机已装 `qwen-code` CLI，否则初始化中断（`requires_cli` 校验）；可用 `--ignore-agent-tools` 跳过

### 方案 A：openspec（一次装全部 5 个 agent）

```bash
cd /your/project

# ✅ 一条命令装 5 个 agent（逗号分隔，无空格）
openspec init --tools zcode,codex,claude,qwen,qoder

# 交互式提示按回车走默认即可
# 完成后输出: "Created: ZCode, Codex, Claude Code, Qwen Code, Qoder"
# 每个 agent 生成 5 个 skill 到 .<agent>/skills/openspec-*/
```

**只装部分 agent**（按需组合）：

```bash
openspec init --tools zcode              # 只 ZCode
openspec init --tools zcode,claude       # ZCode + Claude
openspec init --tools zcode,codex,claude,qwen,qoder   # 全部
```

**已有项目追加 agent**（重跑 init，tools 列表含新 agent 即可，openspec 会合并）：

```bash
# 已装了 zcode，现在加 claude
openspec init --tools zcode,claude
```

### 方案 B：spec-kit（逐个装，注意 key 差异）

```bash
cd /your/project

# 1. 首次初始化（任选一个 agent 作为 default，推荐用你最常用的）
specify init --integration zcode --here --force

# 2. 用 integration install 叠加其余 agent
specify integration install claude
specify integration install codex
specify integration install qwen        # 需本机有 qwen-code CLI
specify integration install qodercli     # ⚠️ key 是 qodercli 不是 qoder
```

**逐个装的对照表**：

| 想装的 agent | 命令 |
|---|---|
| ZCode | `specify init --integration zcode --here --force` |
| Claude Code | `specify integration install claude` |
| Codex | `specify integration install codex` |
| Qwen Code | `specify integration install qwen` |
| Qoder | `specify integration install qodercli` |

> 💡 **spec-kit 不能像 openspec 那样逗号多选**。`--integration` 只接受单个 key，多 agent 必须先 `init` 一个 + 多次 `integration install`。

### 方案 C：两个工具都装（推荐组合）

ZCode 项目里两个工具并存，发挥各自优势：

```bash
cd /your/project

# 先装 openspec（一次搞定 5 个 agent 的 openspec skill）
openspec init --tools zcode,codex,claude,qwen,qoder

# 再装 spec-kit（逐个，给同样 5 个 agent 配 speckit skill）
specify init --integration zcode --here --force
specify integration install claude
specify integration install codex
specify integration install qwen
specify integration install qodercli

# 最终每个 agent 下有两套 skill：
#   .zcode/skills/openspec-*/   (openspec 的)
#   .zcode/skills/speckit-*/    (spec-kit 的)
```

### 一键脚本（装全部 5 agent × 2 工具）

```bash
#!/usr/bin/env bash
# 在当前项目给 zcode/codex/claude/qwen/qoder 装 openspec + spec-kit
set -e
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "=== [1/2] openspec (一次装 5 agent) ==="
openspec init --tools zcode,codex,claude,qwen,qoder

echo ""
echo "=== [2/2] spec-kit (逐个装) ==="
specify init --integration zcode --here --force
for agent in claude codex qwen qodercli; do
  specify integration install "$agent" && echo "✓ $agent" || echo "✗ $agent (跳过)"
done

echo ""
echo "✅ 完成。重启对应 AI agent 会话后生效。"
```

### 初始化后的目录结构示例（装全 5 agent × 2 工具）

```
your-project/
├── openspec/                          ← openspec 数据
├── specs/  +  .specify/               ← spec-kit 数据
├── .zcode/skills/
│   ├── openspec-*/   (5 个)           ← openspec 装的
│   └── speckit-*/    (11 个)          ← spec-kit 装的
├── .claude/skills/
│   ├── openspec-*/   (5 个)
│   └── speckit-*/    (10 个)
├── .codex/skills/openspec-*/          ← openspec 装的
├── .agents/skills/speckit-*/          ← spec-kit 装的（注意不是 .codex）
├── .qwen/skills/openspec-*/
├── .qwen/skills/speckit-*/            ← spec-kit 装（需 qwen-code CLI）
├── .qoder/skills/openspec-*/          ← openspec 装的
└── .qoder/commands/speckit.*.md       ← spec-kit 装的（commands 模式）
```

---

---

## 新电脑部署（从零搭建）

> **核心策略：完全脱离官方，用你自己的私有 Git fork**。
>
> 两个源码仓库（OpenSpec / spec-kit）都是 **MIT 协议**，允许自由 fork、修改、私有部署。补丁已提交到本地 `zcode-support` 分支，push 到你的私有仓库后，新电脑只从你的仓库装，不碰官方。

### 架构对比

| 方式 | 依赖官方 | 新电脑步骤 | 推荐度 |
|---|---|---|---|
| **私有 fork（本方案）** | ❌ 不依赖 | clone 你的仓库 → build/install | ⭐⭐⭐ 推荐 |
| 官方包 + 手动打补丁 | ✅ 依赖 | clone 官方 → 手动改代码 → build | ⭐ fallback |

### 一次性准备：建私有仓库（只做一次，在当前这台电脑）

> 以下命令在**当前电脑**（已有补丁的这台）执行。需要在 Gitee/GitLab/GitHub 私有仓库先手动建两个空仓库。

```bash
# ===== 前提：你已在 Gitee/GitLab 建好两个空仓库，拿到地址 =====
# 示例地址（替换成你自己的）:
#   openspec:  git@github.com:examine928/OpenSpec-zcode.git
#   spec-kit:  git@github.com:examine928/spec-kit-zcode.git

# ===== [1/2] OpenSpec: 推到你的私有仓库 =====
cd ~/Documents/android/OpenSpec
git remote add mine git@github.com:examine928/OpenSpec-zcode.git   # 加你的远程
git push mine zcode-support                                     # 推送带补丁的分支
# 也可同时推 main（官方原版）便于以后同步官方更新:
# git push mine main

# ===== [2/2] spec-kit: 推到你的私有仓库 =====
cd ~/Documents/android/spec-kit
git remote add mine git@github.com:examine928/spec-kit-zcode.git
git push mine zcode-support
```

> 💡 `origin` 仍指向官方，便于以后 `git pull origin main` 同步官方更新（见第三章）。`mine` 指向你的私有仓库。

---

### 新电脑部署（从你的私有 fork 装）

#### 0.1 装基础工具

```bash
# Node.js >= 20.19.0（用 nvm）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 22 && nvm use 22

# pnpm（openspec build 用）
npm install -g pnpm

# Python >= 3.11 + uv（spec-kit 用）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 0.2 clone 你的私有仓库（不碰官方）

```bash
mkdir -p ~/Documents/android && cd ~/Documents/android

# 从你的私有 fork clone，直接 checkout 带补丁的分支
git clone -b zcode-support git@github.com:examine928/OpenSpec-zcode.git OpenSpec
git clone -b zcode-support git@github.com:examine928/spec-kit-zcode.git spec-kit
```

> clone 完即是带 zcode 补丁的代码，**无需手动改任何源码**。

#### 0.3 openspec: build + 覆盖 npm 包

```bash
cd ~/Documents/android/OpenSpec

# 1. 装依赖 + 构建
pnpm install
pnpm run build
# 成功标志: ✅ Build completed successfully!

# 2. 装官方 npm 包（只为拿命令入口和包骨架）
npm install -g @fission-ai/openspec

# 3. 备份官方包 dist，用你的源码 dist 覆盖
NPM_PKG=$(npm root -g)/@fission-ai/openspec
cp -r "$NPM_PKG/dist" "$NPM_PKG/dist.bak.$(date +%s)"
rm -rf "$NPM_PKG/dist" && cp -r dist "$NPM_PKG/dist"

# 4. 验证
openspec init --help | grep -i zcode            # 应有 zcode
```

> 💡 `npm root -g` 跨电脑通用（nvm 装的在 `~/.nvm/.../lib/node_modules`）。
>
> ⚠️ openspec 必须借官方 npm 包做"骨架"——因为它的 `bin/openspec.js` 入口和 `package.json` 在 npm 包里。你覆盖的只是 `dist/`（编译产物，含 zcode 补丁）。

#### 0.4 spec-kit: editable 安装（完全不需要官方包）

```bash
cd ~/Documents/android/spec-kit

# editable 安装，直接从你的源码
uv tool install -e . --force
# 成功标志: + specify-cli==0.11.3.dev0 (from file://.../spec-kit)
#          Installed 1 executable: specify

# 验证
specify integration list | grep -i zcode        # 应输出 zcode 行
```

> spec-kit 比 openspec 干净——editable 安装直接用源码，不依赖任何官方包。

#### 0.5 端到端验证

```bash
TESTDIR=$(mktemp -d) && cd "$TESTDIR"
openspec init --tools zcode                      # 应: 5 skills in .zcode
specify init --integration zcode --here --force  # 应: 11 skills in .zcode
ls .zcode/skills/ | head                          # 应看到 openspec-* 和 speckit-*
cd / && rm -rf "$TESTDIR"
```

#### 0.6 一键部署脚本

将以下存为 `setup-new-machine.sh`，新电脑上执行（前提：0.1 已装基础工具，0.2 已 clone）：

```bash
#!/usr/bin/env bash
# 新电脑部署：从私有 fork 装 openspec + spec-kit 的 ZCode 支持
# 前提: 已装 node/pnpm/python/uv，已 clone 两个私有仓库到 ~/Documents/android/
set -e

SRC_DIR=${SRC_DIR:-$HOME/Documents/android}

echo "=== [1/2] openspec: build + 覆盖 npm 包 ==="
cd "$SRC_DIR/OpenSpec"
pnpm install
pnpm run build
npm install -g @fission-ai/openspec          # 官方包骨架
NPM_PKG=$(npm root -g)/@fission-ai/openspec
cp -r "$NPM_PKG/dist" "$NPM_PKG/dist.bak.$(date +%s)" 2>/dev/null || true
rm -rf "$NPM_PKG/dist" && cp -r dist "$NPM_PKG/dist"
echo "✓ openspec: $(openspec init --help 2>&1 | grep -c zcode) 处 zcode 引用"

echo ""
echo "=== [2/2] spec-kit: editable 安装 ==="
cd "$SRC_DIR/spec-kit"
uv tool install -e . --force
echo "✓ spec-kit: $(specify integration list 2>&1 | grep -c zcode) 处 zcode 引用"

echo ""
echo "✅ 部署完成。新项目里跑:"
echo "   openspec init --tools zcode"
echo "   specify init --integration zcode --here --force"
```

---

### Fallback：官方包 + 手动打补丁（无法访问私有仓库时）

万一新电脑访问不了你的私有 Git，可临时从官方装再手动打补丁：

```bash
mkdir -p ~/Documents/android && cd ~/Documents/android
git clone git@github.com:Fission-AI/OpenSpec.git
git clone git@github.com:github/spec-kit.git

# 然后按【一、openspec 补丁】【二、spec-kit 补丁】手动改源码
# 再按上面 0.3、0.4 的 build/install 步骤部署
```

---

### 私有 fork 的长期维护（同步官方更新）

官方有新版本时，你想把官方更新合并进你的 fork：

```bash
# === openspec ===
cd ~/Documents/android/OpenSpec
git checkout main
git pull origin main              # 拉官方更新到 main
git checkout zcode-support
git rebase main                  # 或 merge，把你的 zcode 补丁重新应用到新版本上
# 若 config.ts 冲突，手动解决（保留官方改动 + 你的 zcode 行）
pnpm run build                   # 重新构建
NPM_PKG=$(npm root -g)/@fission-ai/openspec
rm -rf "$NPM_PKG/dist" && cp -r dist "$NPM_PKG/dist"
git push mine zcode-support      # 推到你的私有仓库

# === spec-kit ===
cd ~/Documents/android/spec-kit
git checkout main
git pull origin main
git checkout zcode-support
git rebase main
uv tool install -e . --force     # editable 模式，重装确认
git push mine zcode-support
```

> 详见「三、源码更新后的重新打补丁流程」。

---

## 环境前提

```bash
# Node.js（openspec 依赖）
node --version    # 需要 >= 20.19.0
npm --version

# Python（spec-kit 依赖）
python3 --version  # 需要 >= 3.11
uv --version       # spec-kit 用 uv tool 安装

# pnpm（openspec 源码 build 用）
pnpm --version     # 没有则: npm install -g pnpm
```

### 源码位置（本文档默认）

```
/home/myron/Documents/android/
├── OpenSpec/      ← openspec 源码
└── spec-kit/      ← spec-kit 源码（GitHub 官方）
```

> 若源码位置变动，下文命令中的路径相应替换即可。

---

## 一、openspec 补丁

### 1.1 改动内容（仅 1 个文件）

**文件**：`OpenSpec/src/core/config.ts`

**改动**：在 `AI_TOOLS` 数组里、`agents` 条目前，加一行 ZCode 条目：

```ts
// 找到这一行（约第 51 行附近）
{ name: 'Windsurf', value: 'windsurf', available: true, successLabel: 'Windsurf', skillsDir: '.windsurf' },

// 在它下面、agents 条目前，加入：
{ name: 'ZCode', value: 'zcode', available: true, successLabel: 'ZCode', skillsDir: '.zcode' },

// agents 条目保持最后
{ name: 'AGENTS.md (works with Amp, VS Code, …)', value: 'agents', available: false, successLabel: 'your AGENTS.md-compatible assistant' }
```

> **无需改其他文件**：`init.ts` 用 `tool.skillsDir` 通用拼接路径（`.zcode` + `/skills`），自动适配。

### 1.2 构建 + 部署

```bash
# 1. 进入源码目录
cd /home/myron/Documents/android/OpenSpec

# 2. 安装依赖（首次或依赖更新时；已有 node_modules 可跳过）
pnpm install

# 3. 构建（生成 dist/）
pnpm run build
# 成功标志: ✅ Build completed successfully!

# 4. 备份当前 npm 全局包的 dist（首次部署时做，升级后重打补丁时 dist.bak 已存在可跳过）
NPM_PKG=/home/myron/.nvm/versions/node/v22.22.0/lib/node_modules/@fission-ai/openspec
cp -r "$NPM_PKG/dist" "$NPM_PKG/dist.bak.$(date +%s)"

# 5. 用源码构建产物覆盖 npm 包
rm -rf "$NPM_PKG/dist" && cp -r dist "$NPM_PKG/dist"
```

### 1.3 验证

```bash
# 应输出包含 zcode 的列表
openspec init --help | grep -i zcode

# 实测生成 skill（在临时目录，不污染项目）
TESTDIR=$(mktemp -d) && cd "$TESTDIR"
printf '\n\n\n\n\n\n\n\n\n\n' | openspec init --tools zcode
# 应看到: "5 skills and 5 commands in .zcode/"
find .zcode/skills -name "SKILL.md"   # 应有 5 个 openspec-*
cd / && rm -rf "$TESTDIR"
```

### 1.4 使用

在任意项目里：

```bash
openspec init --tools zcode
# 生成: .zcode/skills/openspec-{propose,apply-change,archive-change,sync-specs,explore}/SKILL.md
```

---

## 二、spec-kit 补丁

### 2.1 改动内容（3 个文件）

#### 文件 A（新建）：`spec-kit/src/specify_cli/integrations/zcode/__init__.py`

```python
"""ZCode integration — skills-based agent (Z.ai).

ZCode 使用 ``.zcode/skills/speckit-<name>/SKILL.md`` 布局，
调用语法为 ``/speckit-<name>``。与 Claude/Kimi 同属 skills 目录模式，
无 legacy 迁移需求。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import IntegrationOption, SkillsIntegration
from ..manifest import IntegrationManifest


class ZcodeIntegration(SkillsIntegration):
    """Integration for ZCode CLI (Z.ai)."""

    key = "zcode"
    config = {
        "name": "ZCode",
        "folder": ".zcode/",
        "commands_subdir": "skills",
        "install_url": "https://z.ai/",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".zcode/skills",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": "/SKILL.md",
    }
    # ZCode 读 CLAUDE.md 作为上下文文件（项目现状）
    context_file = "CLAUDE.md"
    multi_install_safe = True

    @classmethod
    def options(cls) -> list[IntegrationOption]:
        return [
            IntegrationOption(
                "--skills",
                is_flag=True,
                default=True,
                help="以 agent skills 形式安装（ZCode 默认）",
            ),
        ]

    def setup(
        self,
        project_root: Path,
        manifest: IntegrationManifest,
        parsed_options: dict[str, Any] | None = None,
        **opts: Any,
    ) -> list[Path]:
        """安装 skills 到 .zcode/skills/。"""
        parsed_options = parsed_options or {}
        return super().setup(
            project_root, manifest, parsed_options=parsed_options, **opts
        )
```

#### 文件 B（修改）：`spec-kit/src/specify_cli/integrations/__init__.py`

在 `_register_builtins()` 函数里加 import 和注册（共 2 处）：

```python
# 1. import 段（按字母序，在 windsurf 和 zed 之间）
    from .windsurf import WindsurfIntegration
    from .zcode import ZcodeIntegration      # ← 新增
    from .zed import ZedIntegration

# 2. 注册段（按字母序，在 Windsurf 和 Zed 之间）
    _register(WindsurfIntegration())
    _register(ZcodeIntegration())            # ← 新增
    _register(ZedIntegration())
```

#### 文件 C（修改）：`spec-kit/integrations/catalog.json`

在 `integrations` 对象里、`hermes` 条目后加 zcode 条目：

```json
    "hermes": {
      "id": "hermes",
      "name": "Hermes Agent",
      "version": "1.0.0",
      "description": "Hermes Agent skills-based integration by Nous Research",
      "author": "spec-kit-core",
      "repository": "https://github.com/github/spec-kit",
      "tags": ["cli", "skills"]
    },
    "zcode": {
      "id": "zcode",
      "name": "ZCode",
      "version": "1.0.0",
      "description": "ZCode CLI skills-based integration by Z.ai",
      "author": "spec-kit-core",
      "repository": "https://github.com/github/spec-kit",
      "tags": ["cli", "skills"]
    }
```

### 2.2 安装（editable 模式）

```bash
# 进入源码目录
cd /home/myron/Documents/android/spec-kit

# editable 安装（-e 指向源码，改源码即时生效，无需重装）
uv tool install -e . --force

# 成功标志:
#   + specify-cli==0.11.3.dev0 (from file:///home/myron/Documents/android/spec-kit)
#   Installed 1 executable: specify
```

> **editable 模式的优势**：源码改动即时生效，日常只需改 `.py` 文件，无需重新安装。

### 2.3 验证

```bash
# 1. zcode 应出现在集成清单
specify integration list | grep -i zcode
# 应输出: │ zcode │ ZCode │ ... │ yes │ yes │

# 2. 实测生成 skill（在临时目录）
TESTDIR=$(mktemp -d) && cd "$TESTDIR"
printf '\n\n\n\n\n\n' | specify init --integration zcode --here
find .zcode/skills -name "SKILL.md"   # 应有 11 个 speckit-*
cd / && rm -rf "$TESTDIR"
```

### 2.4 使用

在任意项目里：

```bash
specify init --integration zcode --here
# 生成: .zcode/skills/speckit-{specify,plan,tasks,implement,constitution,...}/SKILL.md
```

---

## 三、源码更新后的重新打补丁流程

### openspec 更新后

```bash
cd /home/myron/Documents/android/OpenSpec

# 1. 拉取官方最新代码（会覆盖你的补丁）
git pull

# 2. 重新打补丁：按【1.1】在 config.ts 加 zcode 条目
#    （手动编辑，或用补丁脚本——见文末附录）

# 3. 装依赖（依赖可能更新）
pnpm install

# 4. 重新构建
pnpm run build

# 5. 覆盖 npm 包（dist.bak 可不重复备份）
NPM_PKG=/home/myron/.nvm/versions/node/v22.22.0/lib/node_modules/@fission-ai/openspec
rm -rf "$NPM_PKG/dist" && cp -r dist "$NPM_PKG/dist"

# 6. 验证
openspec init --help | grep -i zcode
```

> **风险点**：若官方已原生支持 ZCode（加了同名条目），第 2 步会冲突——此时无需打补丁，直接跳到第 3 步。
>
> **检查官方是否已支持**：`grep -i zcode src/core/config.ts`，有输出则说明官方已适配，移除你的本地补丁即可。

### spec-kit 更新后

```bash
cd /home/myron/Documents/android/spec-kit

# 1. 拉取官方最新代码
git pull
# 注意: 新建的 zcode/__init__.py 可能被 git 忽略保留，也可能需重建

# 2. 重新打补丁：按【2.1】
#    - 确认/重建 src/specify_cli/integrations/zcode/__init__.py
#    - 确认 __init__.py 的 import + 注册（git pull 可能合并冲突）
#    - 确认 catalog.json 的 zcode 条目

# 3. editable 模式无需重装（源码改动即时生效）
#    但若拉取后结构大变，建议重装确认:
uv tool install -e . --force

# 4. 验证
specify integration list | grep -i zcode
```

> **检查官方是否已支持**：`ls src/specify_cli/integrations/zcode/ 2>/dev/null`，若官方已新增该目录，删除你的本地补丁文件，用官方版本即可。

---

## 四、回滚（移除 ZCode 支持）

### 回滚 openspec

```bash
NPM_PKG=/home/myron/.nvm/versions/node/v22.22.0/lib/node_modules/@fission-ai/openspec

# 方式 A: 还原备份（推荐）
ls "$NPM_PKG"/dist.bak.*       # 找到最新备份
rm -rf "$NPM_PKG/dist"
cp -r "$NPM_PKG"/dist.bak.<时间戳> "$NPM_PKG/dist"

# 方式 B: 从 npm 重装官方版（彻底）
npm install -g @fission-ai/openspec
```

### 回滚 spec-kit

```bash
# 从 PyPI/官方重装，覆盖 editable 安装
uv tool install specify-cli --force
```

---

## 五、常见问题

### Q1: 改完源码命令还是不认 zcode？

**openspec**：确认改的是**源码**且已 `pnpm run build` + 覆盖 npm 包。检查：
```bash
grep zcode /home/myron/.nvm/versions/node/v22.22.0/lib/node_modules/@fission-ai/openspec/dist/core/config.js
# 必须有输出——命令读的是 npm 包的 dist，不是源码 src
```

**spec-kit**：确认是 editable 安装（`uv-receipt.toml` 里 `editable = ".../spec-kit"`）。检查：
```bash
python3 -c "from specify_cli.integrations import INTEGRATION_REGISTRY; print('zcode' in INTEGRATION_REGISTRY)"
# 应输出 True
```

### Q2: ZCode 会话里 skill 没生效？

改完源码/重装后，需**重启 ZCode 会话**——skill 列表在会话启动时扫描，运行中不刷新。

### Q3: 升级 npm/uv 会丢补丁吗？

- **会**。`npm update -g @fission-ai/openspec` 用官方 dist 覆盖你的改动。
- **不会立刻丢**。spec-kit 的 editable 指向源码，源码在就在；但 `uv tool upgrade specify-cli` 会切回 PyPI 官方版。

### Q4: 如何在多个项目批量启用？

```bash
# 批量给项目装 openspec + spec-kit 的 ZCode 支持
for p in /path/to/project1 /path/to/project2; do
  cd "$p"
  openspec init --tools zcode        # 若要 openspec
  specify init --integration zcode --here  # 若要 spec-kit
done
```

---

## 附录：补丁快速应用脚本

将以下存为 `apply-zcode-patches.sh`，源码更新后一键重打补丁：

```bash
#!/usr/bin/env bash
# 重新应用 ZCode 补丁到 openspec 和 spec-kit 源码
set -e

OPENSPEC_SRC=/home/myron/Documents/android/OpenSpec
SPECKIT_SRC=/home/myron/Documents/android/spec-kit
NVM_LIB=/home/myron/.nvm/versions/node/v22.22.0/lib/node_modules/@fission-ai/openspec

echo "=== [1/2] openspec 补丁 ==="
cd "$OPENSPEC_SRC"
# 检查官方是否已支持
if grep -q "value: 'zcode'" src/core/config.ts 2>/dev/null; then
  echo "openspec 已有 zcode 条目（本地补丁或官方已支持），跳过编辑"
else
  echo "请在 src/core/config.ts 的 Windsurf 条目后手动加入 zcode 条目（见文档 1.1）"
  exit 1
fi
pnpm install && pnpm run build
rm -rf "$NVM_LIB/dist" && cp -r dist "$NVM_LIB/dist"
echo "openspec 补丁完成: $(openspec init --help | grep -c zcode) 处 zcode 引用"

echo ""
echo "=== [2/2] spec-kit 补丁 ==="
cd "$SPECKIT_SRC"
# 检查 zcode 集成文件
if [ ! -f src/specify_cli/integrations/zcode/__init__.py ]; then
  echo "缺少 zcode/__init__.py，请按文档 2.1 文件 A 创建"
  exit 1
fi
uv tool install -e . --force
echo "spec-kit 补丁完成: $(specify integration list 2>/dev/null | grep -c zcode) 处 zcode 引用"

echo ""
echo "✅ 全部完成，重启 ZCode 会话后生效"
```

---

## 改动记录

| 日期 | 工具 | 版本 | 改动 |
|---|---|---|---|
| 2026-06-19 | openspec | 1.4.1 | config.ts 加 zcode 条目，build + 覆盖 npm 包 |
| 2026-06-19 | spec-kit | 0.11.3.dev0 | 新建 zcode 集成子包 + 注册 + catalog，editable 安装 |
| 2026-06-19 | 文档 | - | 新增「在项目中初始化」章节，实测 5 agent（zcode/codex/claude/qwen/qoder）的 key 与落点差异 |

### 实测发现的关键差异（写文档时验证）

- **openspec**：`--tools` 支持逗号多选，5 agent 一条命令搞定，落点统一为 `.<agent>/skills/`
- **spec-kit**：`--integration` 只能单个，多 agent 需 `init` + 多次 `integration install`
- **spec-kit Qoder key** = `qodercli`（openspec 是 `qoder`），两边不一致
- **spec-kit Codex** 落点 = `.agents/skills/`（不是 `.codex/skills/`）
- **spec-kit Qoder** 用 commands 模式（`.qoder/commands/speckit.*.md`），非 skills
- **spec-kit Qwen** 需本机装 `qwen-code` CLI（`requires_cli` 校验），否则 init 中断

> 下次源码更新重新打补丁后，在此追加一行记录。
