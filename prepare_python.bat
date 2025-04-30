@echo off
echo Dang chuan bi moi truong Python cho dong goi...

:: Tao thu muc python trong thu muc electron neu chua co
if not exist "electron\python" mkdir "electron\python"

:: Xac dinh phien ban Python dang dung
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.prefix)"') do set PYTHON_PREFIX=%%i

echo Python path: %PYTHON_PATH%
echo Python prefix: %PYTHON_PREFIX%

:: Sao chep cac file can thiet tu Python da cai dat vao thu muc electron\python
copy "%PYTHON_PATH%" "electron\python\"
copy "%PYTHON_PREFIX%\pythonw.exe" "electron\python\"
copy "%PYTHON_PREFIX%\python*.dll" "electron\python\"

:: Tao thu muc cho cac thu vien can thiet
if not exist "electron\python\Lib" mkdir "electron\python\Lib"
if not exist "electron\python\DLLs" mkdir "electron\python\DLLs"

:: Sao chep cac thu vien co ban
xcopy "%PYTHON_PREFIX%\Lib\site-packages" "electron\python\Lib\site-packages\" /E /I /Y
xcopy "%PYTHON_PREFIX%\DLLs" "electron\python\DLLs\" /E /I /Y

:: Cai dat cac thu vien can thiet vao thu muc python
echo Dang cai dat cac thu vien Python can thiet...
python -m pip install eel bottle multiprocessing --target="electron\python\Lib\site-packages"

echo Da hoan thanh viec chuan bi moi truong Python.
pause