#!/usr/bin/env python3
"""
Test runner script for the Political-Economic Society Simulacrum project.
"""
import os
import sys
import subprocess
import argparse
import pytest

def run_all_tests():
    """Run all test files in the tests directory using pytest."""
    # Get the directory of this script
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to sys.path to allow importing from the project
    parent_dir = os.path.dirname(tests_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Run pytest directly
    print("Running all tests with pytest...\n")
    return pytest.main(["-v", tests_dir])

def run_specific_test(test_name):
    """Run a specific test file using pytest."""
    # Get the directory of this script
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to sys.path to allow importing from the project
    parent_dir = os.path.dirname(tests_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Construct the test file path
    if not test_name.startswith('test_'):
        test_name = f'test_{test_name}'
    if not test_name.endswith('.py'):
        test_name = f'{test_name}.py'
    
    test_file_path = os.path.join(tests_dir, test_name)
    
    # Check if the test file exists
    if not os.path.exists(test_file_path):
        print(f"Error: Test file '{test_name}' not found in the tests directory.")
        return 1
    
    # Run pytest on the specific test file
    print(f"Running test {test_name} with pytest...\n")
    return pytest.main(["-v", test_file_path])

def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run tests for the Political-Economic Society Simulacrum project.')
    parser.add_argument('test', nargs='?', help='Specific test to run (without the test_ prefix)')
    args = parser.parse_args()
    
    if args.test:
        exit_code = run_specific_test(args.test)
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 