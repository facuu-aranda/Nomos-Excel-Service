#!/bin/bash
# Script para probar build localmente antes de deploy

echo "🔍 Testing build locally..."
echo "================================"

# Crear entorno virtual temporal
echo "📦 Creating temporary virtual environment..."
python -m venv .venv_test

# Activar entorno virtual
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv_test/Scripts/activate
else
    source .venv_test/bin/activate
fi

# Actualizar pip
echo "⬆️  Updating pip..."
pip install --upgrade pip

# Intentar instalar dependencias
echo "📥 Installing dependencies from requirements.txt..."
echo "================================"

if pip install -r requirements.txt; then
    echo "================================"
    echo "✅ BUILD SUCCESS!"
    echo "✅ All dependencies installed successfully"
    echo "✅ Ready to deploy to Render"
    echo ""
    echo "Installed packages:"
    pip list | grep -E "(fastapi|pydantic|pandas|supabase)"
    BUILD_STATUS=0
else
    echo "================================"
    echo "❌ BUILD FAILED!"
    echo "❌ Dependencies installation failed"
    echo "❌ DO NOT deploy to Render yet"
    BUILD_STATUS=1
fi

# Limpiar
echo ""
echo "🧹 Cleaning up..."
deactivate
rm -rf .venv_test

echo "================================"
if [ $BUILD_STATUS -eq 0 ]; then
    echo "✅ Test completed successfully"
    exit 0
else
    echo "❌ Test failed - fix errors before deploying"
    exit 1
fi
