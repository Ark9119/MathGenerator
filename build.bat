@echo off
chcp 65001 >nul
echo ==========================================
echo   Сборка MathGenerator в EXE
echo ==========================================
echo.

set APP_NAME=MathGenerator
set MAIN_FILE=interface_for_main.py
set HIDDEN_IMPORTS=--hidden-import=customtkinter --hidden-import=customtkinter.theme_manager --hidden-import=customtkinter.windows.widgets --hidden-import=docx --hidden-import=PIL --hidden-import=packaging --hidden-import=tkinter.messagebox

python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller не найден. Устанавливаю...
    python -m pip install pyinstaller
)

echo [*] Проверка зависимостей...
python -m pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo [!] customtkinter не найден. Устанавливаю...
    python -m pip install customtkinter
)
python -m pip show python-docx >nul 2>&1
if errorlevel 1 (
    echo [!] python-docx не найден. Устанавливаю...
    python -m pip install python-docx
)
python -m pip show pillow >nul 2>&1
if errorlevel 1 (
    echo [!] pillow не найден. Устанавливаю...
    python -m pip install pillow
)

echo [*] Очистка старых файлов сборки...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo [*] Запуск сборки...
python -m PyInstaller --onefile --windowed --name "%APP_NAME%" --clean %HIDDEN_IMPORTS% %MAIN_FILE%

if exist "dist\%APP_NAME%.exe" (
    echo.
    echo ==========================================
    echo   [OK] Сборка завершена успешно!
    echo   Файл: dist\%APP_NAME%.exe
    echo ==========================================
    explorer "dist"
) else (
    echo.
    echo ==========================================
    echo   [ERROR] Ошибка сборки!
    echo ==========================================
)

echo.
pause