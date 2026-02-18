@echo off
REM Script para probar build localmente en Windows antes de deploy

echo 🔍 Testing build locally...
echo ================================

REM Crear entorno virtual temporal
echo 📦 Creating temporary virtual environment...
python -m venv .venv_test

REM Activar entorno virtual
call .venv_test\Scripts\activate.bat

REM Actualizar pip
echo ⬆️  Updating pip...
python -m pip install --upgrade pip

REM Intentar instalar dependencias
echo 📥 Installing dependencies from requirements.txt...
echo ================================

pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo ================================
    echo ✅ BUILD SUCCESS!
    echo ✅ All dependencies installed successfully
    echo ✅ Ready to deploy to Render
    echo.
    echo Installed packages:
    pip list | findstr /I "fastapi pydantic pandas supabase"
    set BUILD_STATUS=0
) else (
    echo ================================
    echo ❌ BUILD FAILED!
    echo ❌ Dependencies installation failed
    echo ❌ DO NOT deploy to Render yet
    set BUILD_STATUS=1
)

REM Limpiar
echo.
echo 🧹 Cleaning up...
call deactivate
rmdir /s /q .venv_test

echo ================================
if %BUILD_STATUS% EQU 0 (
    echo ✅ Test completed successfully
    exit /b 0
) else (
    echo ❌ Test failed - fix errors before deploying
    exit /b 1
)
