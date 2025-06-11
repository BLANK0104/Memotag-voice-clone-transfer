#!/usr/bin/env python3
"""
Project Cleanup Script
Cleans temporary files and organizes the project
"""

import os
import shutil
import glob

def cleanup_project():
    """Clean up temporary files and organize project"""
    print("🧹 Cleaning up project...")
    print("=" * 40)
    
    # 1. Clean Python cache
    print("🗑️  Cleaning Python cache files...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"   Removed: {cache_path}")
            except Exception as e:
                print(f"   Failed to remove {cache_path}: {e}")
    
    # 2. Clean temporary files
    print("\n🗑️  Cleaning temporary files...")
    temp_patterns = [
        "temp_speaker_*.wav",
        "*.tmp",
        "*.temp",
        "debug_*.wav"
    ]
    
    for pattern in temp_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"   Removed: {file}")
            except Exception as e:
                print(f"   Failed to remove {file}: {e}")
    
    # 3. Clean old generated files (keep recent ones)
    print("\n🗑️  Cleaning old generated files...")
    if os.path.exists("generated"):
        files = glob.glob("generated/*.wav")
        if len(files) > 20:  # Keep only 20 most recent
            files.sort(key=os.path.getmtime)
            old_files = files[:-20]
            for file in old_files:
                try:
                    os.remove(file)
                    print(f"   Removed old: {file}")
                except Exception as e:
                    print(f"   Failed to remove {file}: {e}")
    
    # 4. Clean logs (keep recent)
    print("\n🗑️  Cleaning old log files...")
    if os.path.exists("logs"):
        log_files = glob.glob("logs/*.log")
        if len(log_files) > 10:
            log_files.sort(key=os.path.getmtime)
            old_logs = log_files[:-10]
            for log_file in old_logs:
                try:
                    os.remove(log_file)
                    print(f"   Removed old log: {log_file}")
                except Exception as e:
                    print(f"   Failed to remove {log_file}: {e}")
    
    print("\n✅ Project cleanup completed!")
    print("\n📊 Current project structure:")
    print("   📁 app/                 - Core application code")
    print("   📁 static/              - Web frontend")
    print("   📁 tests/               - All tests and samples")
    print("   📁 scripts/             - Setup and utility scripts")
    print("   📁 voices/              - Voice profile samples")
    print("   📁 generated/           - Generated audio (cleaned)")
    print("   📁 docs/                - Documentation")
    print("   📁 sql/                 - Database scripts")
    print("   📜 server.py - 🚀 MAIN ENTRY POINT")

def show_project_status():
    """Show current project status"""
    print("\n🎯 Project Status Summary:")
    print("=" * 40)
    
    # Check main files
    critical_files = [
        "server.py",
        "app/websocket_server.py", 
        "app/websocket_fixed_cloner.py",
        "static/index.html",
        "requirements.txt"
    ]
    
    all_good = True
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            all_good = False
    
    # Check folders
    important_folders = [
        "app", "static", "tests", "scripts", 
        "voices", "generated", "docs"
    ]
    
    for folder in important_folders:
        if os.path.exists(folder):
            file_count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
            print(f"📁 {folder}/ ({file_count} files)")
        else:
            print(f"❌ {folder}/ - MISSING!")
            all_good = False
    
    if all_good:
        print("\n🎉 Project is properly organized and ready!")
        print("🚀 Run: python server.py")
    else:
        print("\n⚠️  Some critical files are missing!")

if __name__ == "__main__":
    cleanup_project()
    show_project_status()
