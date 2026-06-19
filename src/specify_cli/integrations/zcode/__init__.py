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
