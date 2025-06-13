# app/runner.py
import pytest

def run_tests():
    print("Running tests...")
    pytest.main([
        "-s", "./tests/test_novel.py", "--alluredir=allure-results"
    ])
