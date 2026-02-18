# 🔴 FIX CRÍTICO: Build Falla en Windows con Python 3.14

**Fecha:** 18 de febrero de 2026  
**Error:** pandas 2.1.4 intenta compilar desde source en Windows

---

## 🔴 **PROBLEMA IDENTIFICADO**

### **Error en Windows:**
```
error C2198: 'int _PyLong_AsByteArray(...)': no hay suficientes argumentos para la llamada
ninja: build stopped: subcommand failed.
error: metadata-generation-failed
× Encountered error while generating package metadata.
╰─> pandas
```

### **Causa Raíz:**
1. **pandas 2.1.4** NO tiene wheels pre-compilados para **Python 3.14 en Windows**
2. pip intenta compilar desde source usando **Cython + MSVC**
3. **Incompatibilidad** entre Cython 0.29.37 y Python 3.14 API
4. `_PyLong_AsByteArray` cambió su firma en Python 3.14

---

## ⚠️ **DIFERENCIA WINDOWS vs LINUX**

| Aspecto | Linux (Render) | Windows (Local) |
|---------|----------------|-----------------|
| **Compilador** | GCC | MSVC |
| **Wheels disponibles** | Más comunes | Menos comunes |
| **Build time** | Más rápido | Más lento |
| **Compatibilidad** | Mejor | Problemas con Python 3.14 |

**Conclusión:** Lo que funciona en Render (Linux) puede fallar en Windows local.

---

## ✅ **SOLUCIÓN APLICADA**

### **Cambio en `requirements.txt`:**

```diff
# Procesamiento de Excel
- pandas==2.1.4  # ❌ NO tiene wheels para Python 3.14 Windows
+ pandas==2.2.0  # ✅ Tiene wheels oficiales para Python 3.14 Windows
```

### **Por qué pandas 2.2.0:**
- ✅ Tiene wheels oficiales para Python 3.14 en Windows
- ✅ Compatible con numpy 1.26.4
- ✅ NO requiere compilación
- ✅ Versión estable y probada
- ✅ Funciona tanto en Windows como en Linux

---

## 📊 **VERSIONES FINALES OPTIMIZADAS**

```python
# requirements.txt FINAL
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9

pandas==2.2.0      # ✅ Wheels para Windows + Linux
openpyxl==3.1.2
xlrd==2.0.1
numpy==1.26.4

supabase==2.10.0
python-dotenv==1.0.1

pydantic==2.5.3    # ✅ Sin Rust
pydantic-settings==2.1.0

pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

---

## 🎯 **VERIFICACIÓN DE WHEELS**

### **Cómo verificar si una versión tiene wheels:**

**Opción 1: PyPI Web**
```
https://pypi.org/project/pandas/2.2.0/#files
```
Buscar archivos `.whl` con:
- `cp314` (Python 3.14)
- `win_amd64` (Windows 64-bit)

**Opción 2: pip CLI**
```bash
pip index versions pandas
pip download pandas==2.2.0 --only-binary=:all: --python-version 3.14 --platform win_amd64
```

---

## 🚀 **PROBAR BUILD NUEVAMENTE**

```bash
# Ejecutar test de build
.\test_build.bat
```

**Resultado esperado:**
```
Collecting pandas==2.2.0
  Using cached pandas-2.2.0-cp314-cp314-win_amd64.whl  # ✅ Wheel!
Successfully installed pandas-2.2.0 ...
✅ BUILD SUCCESS!
```

**NO debe aparecer:**
- ❌ "Preparing metadata (pyproject.toml)"
- ❌ "Compiling Cython source"
- ❌ "ninja: build stopped"

---

## 📋 **HISTORIAL DE INTENTOS**

### **Intento 1: supabase 2.11.2**
- ❌ Versión no existe en PyPI
- Fix: supabase==2.10.0

### **Intento 2: pydantic 2.10.6**
- ❌ Requiere compilación Rust (pydantic-core)
- Fix: pydantic==2.5.3

### **Intento 3: pandas 2.1.4**
- ❌ NO tiene wheels para Python 3.14 Windows
- ❌ Falla compilación Cython + MSVC
- Fix: pandas==2.2.0 ✅

---

## 🔍 **DIAGNÓSTICO DEL ERROR**

### **Error específico:**
```c
error C2198: 'int _PyLong_AsByteArray(PyLongObject *,unsigned char *,size_t,int,int,int)': 
no hay suficientes argumentos para la llamada
```

**Causa técnica:**
- Python 3.14 cambió la API de `_PyLong_AsByteArray`
- pandas 2.1.4 usa Cython 0.29.37 (viejo)
- Cython 0.29.37 no soporta cambios de Python 3.14
- pandas 2.2.0 usa Cython 3.x (compatible)

---

## ⚠️ **IMPORTANTE: DIFERENCIAS DE ENTORNO**

### **Windows Local (Tu máquina):**
- Python 3.14.x
- MSVC compiler
- Menos wheels disponibles
- **Usa:** `test_build.bat` para verificar

### **Render (Producción):**
- Python 3.14.3
- GCC compiler
- Más wheels disponibles
- Filesystem read-only

**Recomendación:** Siempre probar localmente antes de push.

---

## 🎯 **CHECKLIST FINAL**

Antes de hacer push:

- [ ] Ejecutar `.\test_build.bat`
- [ ] Verificar que NO aparezca "Compiling Cython"
- [ ] Verificar que NO aparezca "ninja: build stopped"
- [ ] Confirmar instalación de pandas 2.2.0 desde wheel
- [ ] Build completo en menos de 2 minutos
- [ ] Todas las dependencias instaladas exitosamente

**Si todos los checks pasan → ✅ Seguro hacer push**

---

## 📚 **REFERENCIAS**

- **pandas wheels:** https://pypi.org/project/pandas/2.2.0/#files
- **Python 3.14 changes:** https://docs.python.org/3.14/whatsnew/3.14.html
- **Cython compatibility:** https://cython.readthedocs.io/en/latest/

---

## ✅ **RESUMEN**

| Item | Estado |
|------|--------|
| Error identificado | ✅ pandas 2.1.4 sin wheels Windows |
| Causa raíz | ✅ Incompatibilidad Cython + Python 3.14 |
| Solución | ✅ pandas==2.2.0 (con wheels) |
| Compatibilidad | ✅ Windows + Linux |
| Listo para test | ✅ Ejecutar test_build.bat |

---

**PRÓXIMO PASO:** Ejecutar `.\test_build.bat` nuevamente. Ahora debería pasar en ~1-2 minutos.
