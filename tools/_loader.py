"""Tool discovery and loading engine.

This module scans the tools directory for Python files with @tool decorated
functions and automatically loads them into the registry.
"""

import importlib
import pkgutil
from pathlib import Path
import logging
from typing import Dict

from tools._decorators import get_tool_metadata

logger = logging.getLogger(__name__)


class ToolLoader:
    """Automatically discovers and loads tools from the tools directory.

    The loader walks through all Python modules in the tools directory,
    finds functions decorated with @tool, and returns them for registration.
    """

    def __init__(self, tools_dir: Path = None):
        """Initialize the tool loader.

        Args:
            tools_dir: Path to tools directory (defaults to parent of this file)
        """
        self.tools_dir = tools_dir or Path(__file__).parent
        logger.debug(f"ToolLoader initialized with directory: {self.tools_dir}")

    def discover_tools(self) -> Dict[str, dict]:
        """Scan tools directory and discover all @tool decorated functions.

        Returns:
            Dictionary mapping tool_id to tool data:
            {
                "domain.tool_name": {
                    "function": callable,
                    "metadata": {...}
                }
            }
        """
        discovered = {}
        tools_package = "tools"

        logger.info(f"Discovering tools in: {self.tools_dir}")

        # Walk through all subdirectories in tools/
        for subdir in self.tools_dir.iterdir():
            if not subdir.is_dir():
                continue
            if subdir.name.startswith("_"):
                continue  # Skip internal directories

            domain_name = subdir.name
            logger.debug(f"Scanning domain: {domain_name}")

            # Scan Python files in this domain directory
            discovered.update(
                self._scan_domain_directory(domain_name, subdir)
            )

        logger.info(f"Discovery complete: Found {len(discovered)} tools")
        return discovered

    def _scan_domain_directory(self, domain_name: str, domain_dir: Path) -> dict:
        """Scan a specific domain directory for tools.

        Args:
            domain_name: Name of the domain (e.g., "weather")
            domain_dir: Path to the domain directory

        Returns:
            Dictionary of discovered tools in this domain
        """
        discovered = {}

        # Find all Python files in this directory
        for py_file in domain_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue  # Skip internal files

            module_name = py_file.stem
            full_module_path = f"tools.{domain_name}.{module_name}"

            try:
                # Import the module
                module = importlib.import_module(full_module_path)
                logger.debug(f"Loaded module: {full_module_path}")

                # Find all @tool decorated functions in the module
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue

                    attr = getattr(module, attr_name)

                    # Check if this is a decorated tool
                    metadata = get_tool_metadata(attr)
                    if metadata is not None:
                        tool_id = f"{metadata['domain']}.{metadata['name']}"
                        discovered[tool_id] = {
                            "function": attr,
                            "metadata": metadata,
                        }
                        logger.info(f"✓ Discovered tool: {tool_id}")

            except Exception as e:
                logger.error(
                    f"Error loading module {full_module_path}: {e}",
                    exc_info=True
                )

        return discovered

    def reload_module(self, module_path: str):
        """Reload a specific module (useful for hot-reload).

        Args:
            module_path: Full module path (e.g., "tools.weather.forecast")
        """
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)
            logger.info(f"Reloaded module: {module_path}")
        except Exception as e:
            logger.error(f"Error reloading module {module_path}: {e}")
