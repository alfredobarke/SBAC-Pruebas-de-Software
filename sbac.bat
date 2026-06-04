@echo off
docker run --rm -it -v %CD%:/app sbac-tests python main.py %*
