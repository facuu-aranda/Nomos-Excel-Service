# Guía: Render Free Tier - Manejo de Sleep

## 🚨 Problema

Render Free Tier pone los servicios a **dormir después de 15 minutos de inactividad**. El primer request después del sleep puede tardar **30-60 segundos** en responder mientras el servicio despierta.

## ✅ Soluciones Implementadas

### 1. Health Check Mejorado (`/health`)

**Ubicación:** `app/main.py`

```python
@app.get("/health")
async def health_check():
    """Health check detallado con información de uptime"""
    uptime_seconds = time.time() - startup_time
    return {
        "status": "healthy",
        "service": "bento-excel-service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "supabase_configured": bool(settings.supabase_url),
        "environment": settings.app_env if hasattr(settings, 'app_env') else "unknown",
    }
```

**Beneficios:**
- Timestamp para verificar cuándo respondió
- Uptime para saber si acaba de despertar
- Información de configuración

### 2. Cliente con Retry Logic + Wake-Up

**Ubicación:** `src/features/saas/services/excel-upload.service.ts`

**Características:**
- ✅ **Wake-up automático**: Ping a `/health` antes de cada operación
- ✅ **Retry con exponential backoff**: 3 intentos con delays de 2s, 4s, 8s
- ✅ **Timeout de 30s**: Para el wake-up inicial
- ✅ **Logs informativos**: Feedback visual en consola

**Flujo:**
```
1. Usuario sube Excel
   ↓
2. wakeUpService() → GET /health (timeout 30s)
   ↓
3. Si responde OK → Proceder con upload
   ↓
4. Si falla → Retry con backoff exponencial
   ↓
5. Máximo 3 intentos antes de error final
```

## 🔧 Configuración en Render

### Health Check Path
```yaml
healthCheckPath: /health
```

**Importante:** Render usa este endpoint para:
- Verificar que el servicio está vivo
- Decidir cuándo ponerlo a dormir
- Monitorear disponibilidad

### Variables de Entorno Requeridas

```env
SUPABASE_URL_SAAS=https://xxx.supabase.co
SUPABASE_SERVICE_KEY_SAAS=eyJxxx...
SUPABASE_URL_WORKSPACE=https://yyy.supabase.co
SUPABASE_SERVICE_KEY_WORKSPACE=eyJxxx...
SUPABASE_DB_URL_WORKSPACE=postgresql://postgres:xxx@db.yyy.supabase.co:5432/postgres
APP_ENV=production
MAX_FILE_SIZE_MB=50
PROCESSING_TIMEOUT_SECONDS=300
```

## 📊 Comportamiento Esperado

### Servicio Despierto (< 15 min inactividad)
- ⚡ Response time: **< 1 segundo**
- ✅ Health check: Responde inmediatamente
- 🟢 Status: `200 OK`

### Servicio Dormido (> 15 min inactividad)
- 🐌 Response time: **30-60 segundos** (primer request)
- ⏳ Wake-up: Cliente espera automáticamente
- 🔄 Retry: Hasta 3 intentos
- 🟡 Status: Puede fallar primeros intentos

### Después de Despertar
- ⚡ Response time: **< 1 segundo**
- ✅ Funcionamiento normal
- 🟢 Status: `200 OK`

## 🧪 Testing

### 1. Verificar Health Check

```bash
curl https://nomos-excel-service.onrender.com/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "bento-excel-service",
  "version": "1.0.0",
  "timestamp": "2026-02-18T17:30:00.000Z",
  "uptime_seconds": 123.45,
  "supabase_configured": true,
  "environment": "production"
}
```

### 2. Simular Sleep

1. Esperar 15+ minutos sin hacer requests
2. Hacer request desde el frontend
3. Observar logs en consola:
   ```
   🔄 Intentando despertar el servicio Excel...
   ⏱️ Timeout esperando que el servicio despierte
   ⚠️ Servicio no responde, reintentando...
   ✅ Servicio Excel despierto y listo
   ```

### 3. Verificar Retry Logic

```typescript
// En la consola del navegador
const service = new ExcelUploadService()
const isHealthy = await service.checkServiceHealth()
console.log('Service healthy:', isHealthy)
```

## 🚀 Alternativas para Evitar Sleep

### Opción 1: Cron Job Externo (Recomendado para MVP)

**UptimeRobot** (Gratis):
- Configurar ping cada 5 minutos a `/health`
- Mantiene el servicio despierto 24/7
- URL: https://uptimerobot.com

**Configuración:**
```
Monitor Type: HTTP(s)
URL: https://nomos-excel-service.onrender.com/health
Monitoring Interval: 5 minutes
```

### Opción 2: GitHub Actions (Gratis)

```yaml
# .github/workflows/keep-alive.yml
name: Keep Render Service Alive
on:
  schedule:
    - cron: '*/10 * * * *'  # Cada 10 minutos
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping service
        run: curl https://nomos-excel-service.onrender.com/health
```

### Opción 3: Upgrade a Render Paid Plan

**Starter Plan ($7/mes):**
- ✅ No sleep
- ✅ 512 MB RAM
- ✅ Mejor performance

**Recomendación:** Usar cron job gratis para MVP, upgrade cuando tengas usuarios pagando.

## 🐛 Troubleshooting

### Error: "Max retries reached"

**Causa:** Servicio no responde después de 3 intentos

**Solución:**
1. Verificar que el servicio está deployed en Render
2. Verificar logs en Render dashboard
3. Verificar variables de entorno
4. Hacer deploy manual si es necesario

### Error: "Timeout esperando que el servicio despierte"

**Causa:** El servicio tarda más de 30s en despertar

**Solución:**
1. Normal en primera vez después de deploy
2. Esperar y reintentar
3. Si persiste, verificar logs de Render

### Error: "Service unavailable"

**Causa:** Servicio crasheado o error en código

**Solución:**
1. Revisar logs en Render dashboard
2. Verificar que todas las dependencias están instaladas
3. Verificar variables de entorno
4. Hacer redeploy

## 📈 Monitoreo

### Logs en Render Dashboard

1. Ir a https://dashboard.render.com
2. Seleccionar `bento-excel-service`
3. Tab "Logs"
4. Buscar:
   - `"GET /health"` → Health checks
   - `"POST /api/excel/upload"` → Uploads
   - Errores de Python

### Métricas Importantes

- **Response Time**: Debe ser < 1s cuando despierto
- **Uptime**: Debe estar > 0 después de request
- **Error Rate**: Debe ser < 5%
- **Wake-up Time**: 30-60s es normal

## 🎯 Best Practices

1. ✅ **Siempre usar el cliente con retry logic**
2. ✅ **Configurar UptimeRobot para producción**
3. ✅ **Monitorear logs regularmente**
4. ✅ **Informar al usuario cuando el servicio está despertando**
5. ✅ **Considerar upgrade a paid plan con usuarios reales**

## 📝 Notas Adicionales

- El sleep es **inevitable** en Render Free Tier
- El retry logic **mitiga** el problema, no lo elimina
- Para producción real, **considerar paid plan** o alternativas (Railway, Fly.io)
- El wake-up automático **mejora UX** significativamente
