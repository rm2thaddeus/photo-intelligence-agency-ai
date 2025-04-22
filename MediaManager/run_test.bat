@echo off
:: MediaManager Test Runner
:: Executes test scripts using the venv313 environment

echo Running tests with venv313...
call ..\venv313\Scripts\activate

echo.
echo Testing processing_utils...
python test_utils.py

echo.
echo Running isolated test...
python isolated_test.py

echo.
echo Tests completed.
pause 