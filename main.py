import pytest

if __name__ == "__main__":
    pytest.main([
        "-s","./tests/test_novel.py","--alluredir=allure-results"
    ])