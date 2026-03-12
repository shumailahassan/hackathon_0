"""
filesystem_watcher.py - Compatibility layer for existing imports
This file now serves as a compatibility layer that imports the actual functionality from skills.
"""
from AI_Employee_Vault.skills.watcher_skill import (
    BaseWatcher,
    DropFolderHandler,
    FilesystemWatcher,
    start_watcher
)

# This allows existing code that imports from filesystem_watcher to continue working
__all__ = ['BaseWatcher', 'DropFolderHandler', 'FilesystemWatcher', 'start_watcher']