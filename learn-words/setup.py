#!/usr/bin/env python3
"""Setup script for Learn Words Telegram Bot."""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def check_uv():
    """Check if uv is installed"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ uv is not installed")
    print("Install it with: pip install uv")
    return False


def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL is available: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("⚠️  PostgreSQL not found in PATH")
    print("Make sure PostgreSQL is installed and accessible")
    return False


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your credentials:")
        print("   - TELEGRAM_BOT_TOKEN (get from @BotFather)")
        print("   - OPENAI_API_KEY (get from OpenAI)")
        print("   - DATABASE_URL (PostgreSQL connection string)")
        return True
    else:
        print("❌ .env.example not found")
        return False


def install_dependencies():
    """Install Python dependencies using uv"""
    try:
        print("📦 Installing dependencies...")
        result = subprocess.run(["uv", "sync"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_database():
    """Create database if it doesn't exist"""
    db_name = "learn_words"
    try:
        # Try to connect to the database
        result = subprocess.run(["psql", "-d", db_name, "-c", "SELECT 1;"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Database '{db_name}' already exists")
            return True
    except FileNotFoundError:
        print("⚠️  psql command not found, skipping database creation")
        return False

    # Try to create the database
    try:
        result = subprocess.run(["createdb", db_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created database '{db_name}'")
            return True
        else:
            print(f"⚠️  Could not create database: {result.stderr}")
            print("You may need to create it manually or check your PostgreSQL setup")
            return False
    except FileNotFoundError:
        print("⚠️  createdb command not found")
        return False


def main():
    """Main setup function"""
    print("🎓 Learn Words Telegram Bot Setup")
    print("=" * 40)

    success = True

    # Check requirements
    success &= check_python_version()
    success &= check_uv()
    check_postgresql()  # Not critical for setup

    if not success:
        print("\n❌ Setup failed due to missing requirements")
        sys.exit(1)

    # Setup steps
    success &= create_env_file()
    success &= install_dependencies()
    create_database()  # Not critical for setup

    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your credentials")
        print("2. Ensure PostgreSQL is running")
        print("3. Run: python main.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("Please check the messages above and resolve any issues")


if __name__ == "__main__":
    main()
