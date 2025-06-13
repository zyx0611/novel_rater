# novel_rater
自动测试执行	runner.run_tests()，独立模块
FastAPI 接口	api.py 中用 Mongo 查询
启动控制	main.py 用 argparse 判断启动模式

poetry init

poetry install

启动fastapi命令: poetry run python -m app.main --mode api

启动test_runner命令:  poetry run python -m app.main --mode text