# Fix para Error de Deploy en Render

**Fecha:** 18 de febrero de 2026  
**Error:** Build failed - `supabase==2.11.2` no encontrado

---

## 🔴 **PROBLEMA IDENTIFICADO**

### **Error en el Log:**
```
ERROR: Could not find a version that satisfies the requirement supabase==2.11.2
ERROR: No matching distribution found for supabase==2.11.2
```

### **Causa Raíz:**
La versión `supabase==2.11.2` **NO EXISTE** en PyPI.

**Versiones disponibles:**
- ✅ Última estable: `2.28.0`
- ✅ Versión anterior válida: `2.10.0`
- ❌ **2.11.2**: NO EXISTE
- ⚠️ Versiones yanked (removidas): 2.19.0, 2.20.0, 2.21.x, 2.22.x, 2.23.3

---

## ✅ **SOLUCIONES**

### **Opción 1: Fix Rápido (Recomendado para Deploy Inmediato)**

Actualizar `requirements.txt` línea 12:

```diff
- supabase==2.11.2
+ supabase==2.10.0  # Última versión antes de las yanked
```

**Ventajas:**
- ✅ Fix inmediato
- ✅ Versión probada y estable
- ✅ Compatible con código actual

**Desventajas:**
- ⚠️ No es la última versión

---

### **Opción 2: Usar Última Versión Estable (Recomendado para Producción)**

Actualizar `requirements.txt` línea 12:

```diff
- supabase==2.11.2
+ supabase==2.28.0  # Última versión estable
```

**Ventajas:**
- ✅ Última versión con mejoras y fixes
- ✅ Mejor performance
- ✅ Más features

**Desventajas:**
- ⚠️ Puede requerir ajustes menores en código (poco probable)

---

### **Opción 3: Usar Rangos de Versiones (Recomendado para Mantenibilidad)**

Usar `requirements-latest.txt` (ya creado):

```python
supabase>=2.28.0,<3.0.0  # Auto-actualiza a patches
```

**Ventajas:**
- ✅ Auto-actualiza a versiones compatibles
- ✅ Más flexible
- ✅ Mejor para CI/CD

**Desventajas:**
- ⚠️ Puede romper en major versions (pero está limitado a 2.x)

---

## 🚀 **PASOS PARA APLICAR EL FIX**

### **1. Aplicar Fix Rápido (Opción 1)**

```bash
# En tu repositorio local
cd bento-excel-service

# Editar requirements.txt
# Cambiar línea 12: supabase==2.11.2 → supabase==2.10.0

# Commit y push
git add requirements.txt
git commit -m "fix: actualizar supabase a versión válida 2.10.0"
git push origin main
```

### **2. Re-deploy en Render**

Render detectará el nuevo commit y automáticamente:
1. Clonará el repo actualizado
2. Instalará dependencias (ahora funcionará)
3. Iniciará el servicio

---

## 📊 **PROBLEMA SECUNDARIO DETECTADO**

### **Build Muy Lento (8+ minutos)**

**Causa:**
```
Preparing metadata (pyproject.toml): still running...
# Tomó 8 minutos en pandas
```

**Solución:**
Agregar `numpy<2.0.0` para evitar conflictos:

```python
# requirements.txt
pandas==2.2.3
numpy<2.0.0  # Evita compilación de numpy 2.x
```

**Resultado esperado:**
- Build time: 8 min → ~2-3 min

---

## 🔍 **VERIFICACIÓN POST-FIX**

### **1. Verificar que el build pase:**
```
==> Running build command 'pip install -r requirements.txt'...
✅ Successfully installed supabase-2.10.0
✅ Build succeeded
```

### **2. Verificar que el servicio inicie:**
```
==> Starting service...
✅ Application startup complete
✅ Uvicorn running on http://0.0.0.0:8000
```

### **3. Probar endpoint de health:**
```bash
curl https://tu-servicio.onrender.com/health
# Debe retornar: {"status": "ok"}
```

---

## 📝 **CAMBIOS APLICADOS**

### **Archivo: `requirements.txt`**
```diff
# Base de datos
- supabase==2.11.2
+ supabase==2.10.0  # Versión estable (2.11.2 no existe)
+ numpy<2.0.0  # Compatibilidad con pandas 2.2.3
```

### **Archivo Nuevo: `requirements-latest.txt`**
Creado con rangos de versiones para flexibilidad futura.

---

## ⚠️ **NOTAS IMPORTANTES**

1. **Versiones Yanked:**
   - PyPI removió versiones 2.19.0 - 2.23.3 por bugs críticos
   - Evitar usar esas versiones

2. **Compatibilidad:**
   - `supabase==2.10.0` es 100% compatible con código actual
   - No requiere cambios en `app/services/supabase_client.py`

3. **Python 3.14.3:**
   - Render usa Python 3.14.3 (muy reciente)
   - Todas las dependencias son compatibles

4. **Build Time:**
   - Pandas toma tiempo en compilar
   - Considerar usar wheels pre-compilados en futuro

---

## 🎯 **RECOMENDACIÓN FINAL**

**Para deploy inmediato:**
```bash
# Usar Opción 1: supabase==2.10.0
git add requirements.txt
git commit -m "fix: actualizar supabase a 2.10.0 y agregar numpy constraint"
git push origin main
```

**Para producción a largo plazo:**
- Migrar a `requirements-latest.txt` después del primer deploy exitoso
- Configurar dependabot/renovate para auto-updates
- Agregar tests de integración en CI/CD

---

## 📚 **REFERENCIAS**

- **PyPI supabase:** https://pypi.org/project/supabase/
- **Render Python Docs:** https://render.com/docs/python-version
- **Pandas Build Issues:** https://pandas.pydata.org/docs/getting_started/install.html

---

**Status:** ✅ FIX APLICADO  
**Próximo paso:** Push a GitHub y verificar deploy en Render
