# Guía para Probar Build Localmente

**Objetivo:** Verificar que `requirements.txt` funciona antes de hacer push a GitHub/Render

---

## 🚀 **OPCIÓN 1: Script Automático (Recomendado)**

### **Windows:**
```bash
# Ejecutar script de test
.\test_build.bat
```

### **Linux/Mac:**
```bash
# Dar permisos de ejecución
chmod +x test_build.sh

# Ejecutar script de test
./test_build.sh
```

**Resultado:**
- ✅ Si pasa: "BUILD SUCCESS" → Listo para deploy
- ❌ Si falla: "BUILD FAILED" → Revisar errores antes de push

---

## 🔧 **OPCIÓN 2: Manual (Paso a Paso)**

### **1. Crear entorno virtual limpio:**
```bash
# Crear venv temporal
python -m venv .venv_test

# Activar (Windows)
.venv_test\Scripts\activate

# Activar (Linux/Mac)
source .venv_test/bin/activate
```

### **2. Actualizar pip:**
```bash
pip install --upgrade pip
```

### **3. Intentar instalar dependencias:**
```bash
pip install -r requirements.txt
```

**Observar:**
- ✅ Si todas se instalan sin errores → BUILD OK
- ❌ Si hay errores de compilación → BUILD FAIL

### **4. Verificar versiones instaladas:**
```bash
pip list | grep -E "(fastapi|pydantic|pandas|supabase)"
```

**Debe mostrar:**
```
fastapi         0.109.2
pydantic        2.5.3
pydantic-core   2.16.x  # NO debe ser 2.27.x
pandas          2.1.4
supabase        2.10.0
```

### **5. Limpiar:**
```bash
deactivate
rm -rf .venv_test  # Linux/Mac
rmdir /s /q .venv_test  # Windows
```

---

## 🐳 **OPCIÓN 3: Docker (Simula Render Exactamente)**

### **Crear `Dockerfile.test`:**
```dockerfile
FROM python:3.14.3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["echo", "Build test successful!"]
```

### **Ejecutar test:**
```bash
# Build imagen
docker build -f Dockerfile.test -t excel-service-test .

# Si build pasa → ✅ Listo para deploy
# Si build falla → ❌ Revisar errores
```

**Ventaja:** Usa exactamente Python 3.14.3 como Render

---

## 🔍 **OPCIÓN 4: Verificar Wheels Disponibles (Rápido)**

Sin instalar nada, verificar si existen wheels:

```bash
# Verificar pydantic
pip index versions pydantic

# Verificar si 2.5.3 tiene wheels para Python 3.14
# Buscar: "py3-none-any.whl" o "cp314-cp314-*.whl"
```

**Online:**
- https://pypi.org/project/pydantic/2.5.3/#files
- Buscar archivos `.whl` (wheels pre-compilados)
- Si solo hay `.tar.gz` → Requiere compilación

---

## ⚡ **OPCIÓN 5: Test Rápido con pip-compile**

```bash
# Instalar pip-tools
pip install pip-tools

# Verificar dependencias
pip-compile requirements.txt --dry-run

# Si pasa sin errores → ✅ OK
```

---

## 📊 **COMPARACIÓN DE OPCIONES**

| Opción | Velocidad | Precisión | Complejidad |
|--------|-----------|-----------|-------------|
| Script automático | ⚡⚡⚡ Rápido | ✅ Alta | 🟢 Fácil |
| Manual | ⚡⚡ Medio | ✅ Alta | 🟡 Media |
| Docker | ⚡ Lento | ✅✅ Exacta | 🔴 Alta |
| Verificar wheels | ⚡⚡⚡⚡ Muy rápido | ⚠️ Media | 🟢 Fácil |
| pip-compile | ⚡⚡⚡ Rápido | ✅ Alta | 🟢 Fácil |

---

## 🎯 **RECOMENDACIÓN**

### **Para test rápido antes de commit:**
```bash
# Windows
.\test_build.bat

# Linux/Mac
./test_build.sh
```

### **Para test exhaustivo (primera vez):**
```bash
# Usar Docker para simular Render exactamente
docker build -f Dockerfile.test -t excel-service-test .
```

---

## ✅ **CHECKLIST PRE-DEPLOY**

Antes de hacer `git push`:

- [ ] Ejecutar `test_build.bat` o `test_build.sh`
- [ ] Verificar que NO aparezca "maturin" o "Rust" en output
- [ ] Verificar que NO aparezca "Preparing metadata (pyproject.toml)" por más de 10 segundos
- [ ] Confirmar versiones instaladas:
  - [ ] pydantic 2.5.3 (NO 2.10.6)
  - [ ] fastapi 0.109.2
  - [ ] pandas 2.1.4
  - [ ] supabase 2.10.0
- [ ] Build completo en menos de 3 minutos

**Si todos los checks pasan → ✅ Seguro hacer push**

---

## 🚨 **SEÑALES DE ALERTA**

### **❌ NO hacer push si ves:**
```
Preparing metadata (pyproject.toml): still running...
# Más de 1 minuto

error: failed to create directory
💥 maturin failed
Rust toolchain
cargo metadata
```

### **✅ OK hacer push si ves:**
```
Successfully installed fastapi-0.109.2 pydantic-2.5.3 ...
# Sin errores de compilación
# Build en menos de 3 minutos
```

---

## 📝 **EJEMPLO DE OUTPUT EXITOSO**

```
🔍 Testing build locally...
================================
📦 Creating temporary virtual environment...
⬆️  Updating pip...
📥 Installing dependencies from requirements.txt...
================================
Collecting fastapi==0.109.2
  Using cached fastapi-0.109.2-py3-none-any.whl
Collecting pydantic==2.5.3
  Using cached pydantic-2.5.3-py3-none-any.whl
...
Successfully installed fastapi-0.109.2 pydantic-2.5.3 ...
================================
✅ BUILD SUCCESS!
✅ All dependencies installed successfully
✅ Ready to deploy to Render

Installed packages:
fastapi         0.109.2
pydantic        2.5.3
pandas          2.1.4
supabase        2.10.0
================================
✅ Test completed successfully
```

---

## 🔄 **WORKFLOW RECOMENDADO**

```bash
# 1. Modificar requirements.txt
nano requirements.txt

# 2. Probar build localmente
.\test_build.bat  # Windows
./test_build.sh   # Linux/Mac

# 3. Si pasa → Commit y push
git add requirements.txt
git commit -m "fix: actualizar dependencias"
git push origin main

# 4. Render auto-deploya
# 5. Verificar en logs de Render que build pasa
```

---

## 📚 **RECURSOS**

- **PyPI Files:** https://pypi.org/project/PACKAGE/#files
- **Render Build Logs:** Dashboard → Service → Logs
- **Python Wheels:** https://pythonwheels.com/

---

**TIP:** Guarda el output del test local para comparar con logs de Render si algo falla.
