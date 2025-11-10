#!/usr/bin/env python3
"""Test runner script for Learn Words project with Docker database support."""

import subprocess
import sys
import time
import os
from pathlib import Path


def run_command(cmd, check=True, capture_output=False):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if capture_output and e.stdout:
            print(f"stdout: {e.stdout}")
        if capture_output and e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def check_docker():
    """Check if Docker is available."""
    return run_command(["docker", "--version"], check=False, capture_output=True)


def start_test_database():
    """Start the test database container."""
    print("Starting test database...")

    # Stop any existing container
    run_command(["docker", "stop", "learn-words-test-db"], check=False)
    run_command(["docker", "rm", "learn-words-test-db"], check=False)

    # Start new container
    success = run_command(
        [
            "docker",
            "run",
            "-d",
            "--name",
            "learn-words-test-db",
            "-e",
            "POSTGRES_DB=learn_words_test",
            "-e",
            "POSTGRES_USER=test_user",
            "-e",
            "POSTGRES_PASSWORD=test_password",
            "-e",
            "POSTGRES_HOST_AUTH_METHOD=trust",
            "-p",
            "5433:5432",
            "-v",
            f"{Path.cwd()}/migrations:/docker-entrypoint-initdb.d",
            "postgres:15-alpine",
        ]
    )

    if not success:
        return False

    # Wait for database to be ready
    print("Waiting for database to be ready...")
    for i in range(30):
        if run_command(
            [
                "docker",
                "exec",
                "learn-words-test-db",
                "pg_isready",
                "-U",
                "test_user",
                "-d",
                "learn_words_test",
            ],
            check=False,
        ):
            print("Database is ready!")
            return True
        time.sleep(1)

    print("Database failed to start within 30 seconds")
    return False


def stop_test_database():
    """Stop the test database container."""
    print("Stopping test database...")
    run_command(["docker", "stop", "learn-words-test-db"], check=False)
    run_command(["docker", "rm", "learn-words-test-db"], check=False)


def run_tests(test_type="all", verbose=False):
    """Run tests with the specified type."""
    # Set environment variables
    env = os.environ.copy()
    env["TEST_DATABASE_URL"] = "postgresql://test_user:test_password@localhost:5433/learn_words_test"

    # Build pytest command
    cmd = ["uv", "run", "pytest"]

    if verbose:
        cmd.append("-v")

    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "all":
        cmd.append("tests/")
    else:
        print(f"Unknown test type: {test_type}")
        return False

    # Add coverage if running all tests
    if test_type == "all":
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])

    # Run tests
    return subprocess.run(cmd, env=env).returncode == 0


def main():
    """Main test runner function."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Learn Words tests")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Skip Docker database setup (unit tests only)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Check if we need Docker
    needs_docker = args.type in ["integration", "performance", "all"] and not args.no_docker

    if needs_docker:
        if not check_docker():
            print("Docker is not available. Use --no-docker to run unit tests only.")
            return 1

        if not start_test_database():
            print("Failed to start test database")
            return 1

    try:
        # Run tests
        success = run_tests(args.type, args.verbose)
        return 0 if success else 1

    finally:
        if needs_docker:
            stop_test_database()


if __name__ == "__main__":
    sys.exit(main())
