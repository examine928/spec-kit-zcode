# spec-kit ZCode 支持指南

> 本 fork 给 [spec-kit](https://github.com/github/spec-kit)（GitHub 官方规格驱动工具，CLI 命令 `specify`）加了 **ZCode** agent 支持，让 `specify init --integration zcode` 能识别 ZCode，把 skill 装到 `.zcode/skills/`。
>
> 本文档只讲 **spec-kit** 侧的事（补丁内容、部署、初始化、维护）。openspec 的 ZCode 支持见另一个 fork：`git@github.com:examine928/OpenSpec-zcode.git`。

---

## 补丁内容（本 fork 相对官方改了什么）

**共 3 个文件**：

### 文件 A（新建）：`src/specify_cli/integrations/zcode/__init__.py`

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

### 文件 B（修改）：`src/specify_cli/integrations/__init__.py`

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

### 文件 C（修改）：`integrations/catalog.json`

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

> 对应 commit：`feat: add ZCode integration`

---

## 新电脑部署（从本 fork 装，脱离官方）

### 前提

```bash
# Python >= 3.11
python3 --version

# uv（spec-kit 用 uv tool 安装）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 步骤

```bash
# 1. clone 本 fork（直接带补丁，不碰官方）
mkdir -p ~/Documents/android && cd ~/Documents/android
git clone -b zcode-support git@github.com:examine928/spec-kit-zcode.git spec-kit
cd spec-kit

# 2. editable 安装（-e 指向源码，改源码即时生效，无需重装）
uv tool install -e . --force
# 成功标志:
#   + specify-cli==0.11.3.dev0 (from file://.../spec-kit)
#   Installed 1 executable: specify

# 3. 验证
specify integration list | grep -i zcode
# 应输出: │ zcode │ ZCode │ ... │ yes │ yes │
```

> 💡 spec-kit 用 editable 安装，**完全不需要官方 PyPI 包**，比 openspec 干净。源码改动即时生效。

### 一键部署脚本

```bash
#!/usr/bin/env bash
# 新电脑部署 spec-kit 的 ZCode 支持
# 前提: 已装 python/uv，已 clone 本 fork 到 ~/Documents/android/spec-kit
set -e
cd ~/Documents/android/spec-kit
uv tool install -e . --force
echo "✓ spec-kit: $(specify integration list 2>&1 | grep -c zcode) 处 zcode 引用"
```

---

## 在项目里初始化

### 单 agent（只装 ZCode）

```bash
cd /your/project
specify init --integration zcode --here --force
# 生成: .zcode/skills/speckit-{specify,plan,tasks,implement,constitution,...}/SKILL.md（11 个）
```

### 多 agent（spec-kit 只能逐个装，⚠️ key 有差异）

spec-kit 的 `--integration` 只接受单个 key，多 agent 需 `init` 一个 + 多次 `integration install`：

```bash
cd /your/project

# 1. 首次初始化（任选一个作为 default）
specify init --integration zcode --here --force

# 2. 叠加其余 agent
specify integration install claude
specify integration install codex
specify integration install qwen        # 需本机有 qwen-code CLI
specify integration install qodercli     # ⚠️ key 是 qodercli 不是 qoder
```

### 各 agent 的 key 与落点（⚠️ 与 openspec 不完全一致）

| Agent | spec-kit key | spec-kit 落点 | 交付模式 |
|---|---|---|---|
| ZCode | `zcode` | `.zcode/skills/speckit-*` | skills |
| Claude Code | `claude` | `.claude/skills/speckit-*` | skills |
| Codex | `codex` | **`.agents/skills/speckit-*`** ⚠️ | skills |
| Qwen Code | `qwen` | `.qwen/skills/speckit-*`（需 qwen-code CLI） | skills |
| Qoder | `qodercli` ⚠️ | `.qoder/commands/speckit.*.md` | **commands**（非 skills） |

> ⚠️ **三个坑**：
> 1. **Qoder 的 key 是 `qodercli`**（openspec 里是 `qoder`），两边不一致
> 2. **Codex 的 speckit 落到 `.agents/skills/`**，不是 `.codex/skills/`
> 3. **Qwen 需本机装 `qwen-code` CLI**（`requires_cli` 校验），否则 init 中断

### 逐个装对照表

| 想装的 agent | 命令 |
|---|---|
| ZCode | `specify init --integration zcode --here --force` |
| Claude Code | `specify integration install claude` |
| Codex | `specify integration install codex` |
| Qwen Code | `specify integration install qwen` |
| Qoder | `specify integration install qodercli` |

---

## 长期维护（同步官方更新）

官方有新版本时，把官方更新合并进本 fork：

```bash
cd ~/Documents/android/spec-kit

# 1. 拉官方更新到 main
git checkout main
git pull origin main

# 2. 把 zcode 补丁重新应用到新版本
git checkout zcode-support
git rebase main
# 若 __init__.py 或 catalog.json 冲突，手动解决（保留官方改动 + 你的 zcode 部分）
# 确认 src/specify_cli/integrations/zcode/__init__.py 还在

# 3. editable 模式无需重装（源码改动即时生效）
#    但若拉取后结构大变，建议重装确认:
uv tool install -e . --force

# 4. 推送到本 fork
git push mine zcode-support
```

> 若官方已原生支持 ZCode（`ls src/specify_cli/integrations/zcode/ 2>/dev/null` 有输出），删除你的本地补丁文件，用官方版本即可。

---

## 回滚（移除 ZCode 支持）

```bash
# 从 PyPI/官方重装，覆盖 editable 安装
uv tool install specify-cli --force
```

---

## 常见问题

**Q: `specify integration list` 看不到 zcode？**
确认是 editable 安装且指向本 fork：
```bash
cat ~/.local/share/uv/tools/specify-cli/uv-receipt.toml | grep editable
# 应是: editable = ".../spec-kit"
```

**Q: ZCode 会话里 skill 没生效？**
重启 ZCode 会话——skill 列表在会话启动时扫描，运行中不刷新。

**Q: `uv tool upgrade specify-cli` 会丢补丁吗？**
会，会切回 PyPI 官方版。升级后需重新 `uv tool install -e . --force` 从本 fork 装。

**Q: spec-kit 能像 openspec 那样逗号多选 agent 吗？**
不能。`--integration` 只接受单个 key，多 agent 必须 `init` 一个 + 多次 `integration install`。

---

## 相关

- 官方仓库：https://github.com/github/spec-kit
- 本 fork：`git@github.com:examine928/spec-kit-zcode.git`（`zcode-support` 分支）
- 配套：openspec 的 ZCode 支持（另一工具）→ `git@github.com:examine928/OpenSpec-zcode.git`

## 改动记录

| 日期 | 版本 | 改动 |
|---|---|---|
| 2026-06-19 | 0.11.3.dev0 | 新建 zcode 集成子包 + 注册 + catalog，editable 安装；推送到本 fork |
