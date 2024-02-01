#!python

import os
import sys

os.environ["LAMBDA_ENV"] = "dev"

EXCLUDE_FOLDERS = [
    "tests",
    "venv",
    ".aws-sam",
    "site-packages",
    ".git",
    "cache",
    ".idea",
    ".env",
    "python",
]
GPT = os.environ.get("GPT", os.getcwd())
sys.path.append(GPT)
PATHS = [GPT]
for x in os.walk(GPT):
    if not any(f in x[0] for f in EXCLUDE_FOLDERS):
        print(x[0])
        PATHS.append(x[0])
PATHS.sort()
PATHS = ":".join(PATHS)

os.environ["PYTHONPATH"] = "PYTHONPATH" + PATHS
exit_code = os.system(
    f"pytest --cov-config=.coverage_conf --cov-report term-missing --cov={os.getcwd()} --cov-fail-under=90 "
    "--cov-report html --cov-report xml --html-report=./reports/report.html "
    "--junitxml=./reports/result.xml -s tests/"
)
