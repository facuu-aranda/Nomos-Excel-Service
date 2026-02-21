@echo off
python -m pytest tests/test_excel_processor.py tests/test_routes.py -v --tb=short > test_output.txt 2>&1
echo Exit code: %ERRORLEVEL%
type test_output.txt
