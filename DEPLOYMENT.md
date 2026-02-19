# Deployment Guide - Bento Excel Service

## 🚀 Deployment en Render.com

### Paso 1: Preparar el Repositorio

1. Crear repositorio en GitHub:
```bash
cd bento-excel-service
git init
git add .
git commit -m "Initial commit: FastAPI Excel microservice"
git branch -M main
git remote add origin https://github.com/your-org/bento-excel-service.git
git push -u origin main
```

### Paso 2: Configurar Render

1. Ir a [render.com](https://render.com) y crear cuenta
2. Click en "New +" → "Web Service"
3. Conectar repositorio de GitHub
4. Configurar servicio:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Paso 3: Variables de Entorno

Configurar en Render Dashboard → Environment:

```
SUPABASE_URL=https://your-workspace-project.supabase.co
SUPABASE_KEY=your-workspace-anon-key
ALLOWED_ORIGINS=https://your-nextjs-app.vercel.app,http://localhost:3000
MAX_FILE_SIZE=10485760
DEBUG=False
```

### Paso 4: Deploy

1. Click en "Create Web Service"
2. Render automáticamente:
   - Instala dependencias
   - Ejecuta el servidor
   - Asigna una URL pública

### URL del Servicio

Render asignará una URL como:
```
https://nomos-excel-service.onrender.com
```

## 🔧 Configuración Post-Deploy

### 1. Verificar Health Check

```bash
curl https://nomos-excel-service.onrender.com/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "service": "bento-excel-service",
  "version": "1.0.0",
  "supabase_configured": true
}
```

### 2. Probar Endpoints

**Validar Excel:**
```bash
curl -X POST https://nomos-excel-service.onrender.com/api/excel/validate \
  -F "file=@sample.xlsx"
```

**Procesar Excel (endpoint canónico):**
```bash
curl -X POST https://nomos-excel-service.onrender.com/api/excel/process \
  -F "file=@sample.xlsx" \
  -F "workspace_id=workspace-123" \
  -F "user_id=user-456" \
  -F "dashboard_name=My Dashboard"
```

**Upload Excel (compatibilidad):**
```bash
curl -X POST https://nomos-excel-service.onrender.com/api/excel/upload \
  -F "file=@sample.xlsx" \
  -F "workspace_id=workspace-123" \
  -F "user_id=user-456" \
  -F "dashboard_name=My Dashboard"
```

### 3. Verificar wake-up en free tier

Si el servicio está dormido, ejecutar un ping de wake-up y esperar 30-60s:

```bash
curl --max-time 30 https://nomos-excel-service.onrender.com/health
```

Opcional: revisar contrato desplegado

```bash
curl https://nomos-excel-service.onrender.com/openapi.json
```

## 🔐 Seguridad

### CORS Configuration

Actualizar `ALLOWED_ORIGINS` con las URLs de producción:
```
ALLOWED_ORIGINS=https://app.bentoadmin.com,https://staging.bentoadmin.com
```

### Rate Limiting (Opcional)

Agregar middleware de rate limiting en `app/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/excel/upload")
@limiter.limit("5/minute")
async def upload_excel(...):
    ...
```

## 📊 Monitoreo

### Logs en Render

1. Ir a Dashboard → Tu servicio → Logs
2. Ver logs en tiempo real
3. Filtrar por nivel (INFO, ERROR, etc.)

### Métricas

Render proporciona:
- CPU usage
- Memory usage
- Request count
- Response times

### Alertas

Configurar alertas en Render:
1. Settings → Notifications
2. Agregar webhook o email
3. Configurar condiciones (CPU > 80%, errores, etc.)

## 🔄 CI/CD

### Auto-Deploy

Render automáticamente hace deploy en cada push a `main`:

```bash
git add .
git commit -m "feat: add new feature"
git push origin main
# Render detecta el push y hace deploy automático
```

### Deploy Manual

En Render Dashboard:
1. Click en "Manual Deploy"
2. Seleccionar branch
3. Click en "Deploy"

## 🐛 Troubleshooting

### Error: Module not found

**Solución:** Verificar que todas las dependencias estén en `requirements.txt`

```bash
pip freeze > requirements.txt
```

### Error: Port already in use

**Solución:** Render asigna el puerto automáticamente vía `$PORT`

Asegurar que el start command use:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Error: Supabase connection failed

**Solución:** Verificar variables de entorno en Render Dashboard

### Slow cold starts

**Solución:** Render free tier tiene cold starts. Considerar:
- Upgrade a plan pago
- Implementar health check ping cada 10 minutos

## 📈 Escalabilidad

### Horizontal Scaling

En Render Dashboard:
1. Settings → Scaling
2. Aumentar número de instancias
3. Configurar auto-scaling basado en CPU/memoria

### Optimizaciones

1. **Async Processing:**
   - Usar Celery + Redis para procesamiento asíncrono
   - Retornar job_id inmediatamente
   - Cliente consulta status con polling

2. **Caching:**
   - Implementar Redis para cachear resultados
   - Cachear análisis de archivos frecuentes

3. **Database Connection Pooling:**
   - Configurar pool de conexiones a Supabase
   - Reutilizar conexiones

## 🔄 Rollback

Si un deploy falla:

1. En Render Dashboard → Deploys
2. Click en deploy anterior exitoso
3. Click en "Redeploy"

## 📝 Checklist Pre-Deploy

- [ ] Todas las variables de entorno configuradas
- [ ] Tests pasando (`pytest`)
- [ ] Dependencias actualizadas en `requirements.txt`
- [ ] CORS configurado correctamente
- [ ] Health check funcionando
- [ ] Logs configurados
- [ ] Documentación actualizada

## 🎯 Next Steps

1. Implementar autenticación JWT
2. Agregar rate limiting
3. Implementar procesamiento asíncrono
4. Configurar monitoring avanzado (Sentry, DataDog)
5. Agregar más tipos de widgets automáticos
6. Implementar cache con Redis

---

**Última actualización:** Febrero 2026
