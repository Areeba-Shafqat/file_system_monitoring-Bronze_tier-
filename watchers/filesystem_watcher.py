"""
Bronze Tier - Filesystem Watcher
Monitors /Inbox folder and processes new files automatically

INSTALLATION:
    pip install watchdog

USAGE:
    python watchers/filesystem_watcher.py

TESTING:
    1. Run this script
    2. Drop any file into the /Inbox folder
    3. Check /Needs_Action folder for:
       - File_[original_filename] (copied file)
       - File_[original_filename].md (metadata)
"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class InboxFileHandler(FileSystemEventHandler):
    """Handles file creation events in the Inbox folder"""

    def __init__(self, inbox_path, needs_action_path):
        self.inbox_path = Path(inbox_path)
        self.needs_action_path = Path(needs_action_path)

        # Ensure directories exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

        print(f"[WATCHER] Monitoring: {self.inbox_path}")
        print(f"[WATCHER] Output to: {self.needs_action_path}")
        print("-" * 60)

    def on_created(self, event):
        """Called when a file is created in the monitored folder"""
        if event.is_directory:
            return

        source_path = Path(event.src_path)

        # Skip temporary files and hidden files
        if source_path.name.startswith('.') or source_path.name.startswith('~'):
            return

        # Wait a moment to ensure file is fully written
        time.sleep(0.5)

        try:
            self.process_file(source_path)
        except Exception as e:
            print(f"[ERROR] Failed to process {source_path.name}: {e}")

    def process_file(self, source_path):
        """Process a new file: copy it and create metadata"""
        original_name = source_path.name
        new_filename = f"File_{original_name}"
        destination_path = self.needs_action_path / new_filename
        metadata_path = self.needs_action_path / f"{new_filename}.md"

        # Get file size
        try:
            file_size = source_path.stat().st_size
        except Exception as e:
            print(f"[ERROR] Cannot read file size for {original_name}: {e}")
            return

        # Copy the file
        try:
            shutil.copy2(source_path, destination_path)
            print(f"[COPIED] {original_name} -> {new_filename}")
        except Exception as e:
            print(f"[ERROR] Failed to copy {original_name}: {e}")
            return

        # Create metadata file
        try:
            metadata_content = self.create_metadata(original_name, file_size)
            metadata_path.write_text(metadata_content, encoding='utf-8')
            print(f"[METADATA] Created {new_filename}.md")
        except Exception as e:
            print(f"[ERROR] Failed to create metadata for {original_name}: {e}")

        print("-" * 60)

    def create_metadata(self, original_name, file_size):
        """Generate YAML front matter metadata"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metadata = f"""---
type: file_drop
original_name: {original_name}
size: {file_size}
status: pending
timestamp: {timestamp}
---

# File Drop: {original_name}

This file was automatically detected and processed by the Bronze Tier filesystem watcher.

**Original Name:** {original_name}
**Size:** {file_size} bytes
**Status:** Pending review
**Processed:** {timestamp}
"""
        return metadata


def main():
    """Main function to start the filesystem watcher"""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    inbox_path = project_root / "Inbox"
    needs_action_path = project_root / "Needs_Action"

    # Ensure Inbox exists
    if not inbox_path.exists():
        inbox_path.mkdir(parents=True, exist_ok=True)
        print(f"[SETUP] Created Inbox folder: {inbox_path}")

    # Create event handler and observer
    event_handler = InboxFileHandler(inbox_path, needs_action_path)
    observer = Observer()
    observer.schedule(event_handler, str(inbox_path), recursive=False)

    # Start watching
    observer.start()
    print(f"[STARTED] Filesystem watcher is running...")
    print(f"[INFO] Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(5)  # Check interval: 5 seconds
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down filesystem watcher...")
        observer.stop()

    observer.join()
    print("[STOPPED] Filesystem watcher stopped.")


if __name__ == "__main__":
    main()
