# Checklist: Deploy y Verificación Microservicio Excel

## ✅ Pre-Deploy

- [ ] Todas las dependencias en `requirements.txt`
- [ ] Variables de entorno configuradas en Render
- [ ] Health check endpoint `/health` implementado
- [ ] CORS configurado correctamente
- [ ] Tests pasando (si existen)

## 🚀 Deploy en Render

### 1. Verificar Configuración

```yaml
# render.yaml
services:
  - type: web
    name: bento-excel-service
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

### 2. Variables de Entorno Requeridas

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.xlsx,.xls
```

### 3. Deploy

1. Push a GitHub
2. Render auto-deploys
3. Esperar build (2-5 min)
4. Verificar logs

## 🧪 Post-Deploy Verification

### 1. Health Check

```bash
curl https://nomos-excel-service.onrender.com/health
```

**Esperado:**
```json
{
  "status": "healthy",
  "service": "bento-excel-service",
  "version": "1.0.0",
  "timestamp": "2026-02-18T...",
  "uptime_seconds": 12.34,
  "supabase_configured": true
}
```

### 2. Root Endpoint

```bash
curl https://nomos-excel-service.onrender.com/
```

### 3. Swagger Docs

Abrir en navegador:
```
https://nomos-excel-service.onrender.com/docs
```

### 4. Test desde Frontend

```typescript
const service = new ExcelUploadService()
const isHealthy = await service.checkServiceHealth()
console.log('Service healthy:', isHealthy)
```

## 🔧 Troubleshooting

### Servicio no responde

1. **Verificar en Render Dashboard:**
   - Estado del servicio (Running/Suspended)
   - Logs recientes
   - Último deploy exitoso

2. **Despertar manualmente:**
   ```bash
   curl https://nomos-excel-service.onrender.com/health
   ```
   Esperar 30-60s

3. **Verificar variables de entorno:**
   - Render Dashboard → Service → Environment
   - Todas las variables configuradas
   - Sin typos en nombres

### Error 500

1. **Revisar logs en Render:**
   ```
   Dashboard → Logs → Buscar errores Python
   ```

2. **Errores comunes:**
   - Missing environment variables
   - Import errors
   - Database connection issues

### CORS Error

1. **Verificar ALLOWED_ORIGINS:**
   ```env
   ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```

2. **Sin espacios, separado por comas**

3. **Incluir protocolo (https://)**

## 📊 Monitoreo Continuo

### Configurar UptimeRobot (Recomendado)

1. Crear cuenta en https://uptimerobot.com
2. Add New Monitor:
   - Type: HTTP(s)
   - URL: `https://nomos-excel-service.onrender.com/health`
   - Interval: 5 minutes
3. Configurar alertas por email

### Logs en Render

- Revisar diariamente
- Buscar patterns de errores
- Monitorear response times

## 🎯 Checklist Final

- [ ] Health check responde OK
- [ ] Swagger docs accesibles
- [ ] Frontend puede conectarse
- [ ] Retry logic funciona
- [ ] UptimeRobot configurado (opcional)
- [ ] Variables de entorno verificadas
- [ ] CORS configurado correctamente
- [ ] Logs sin errores críticos

## 📝 Comandos Útiles

### Verificar servicio desde terminal

```bash
# Health check
curl https://nomos-excel-service.onrender.com/health

# Con headers
curl -i https://nomos-excel-service.onrender.com/health

# Test CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://nomos-excel-service.onrender.com/api/excel/upload
```

### Verificar desde frontend (DevTools Console)

```javascript
// Health check
fetch('https://nomos-excel-service.onrender.com/health')
  .then(r => r.json())
  .then(console.log)

// Con retry logic
const service = new ExcelUploadService()
service.checkServiceHealth().then(console.log)
```

## 🚨 Problemas Conocidos

### Free Tier Sleep (15 min inactividad)

**Solución implementada:**
- Cliente con retry logic automático
- Wake-up mechanism en primer request
- Exponential backoff (2s, 4s, 8s)

**Mitigación adicional:**
- UptimeRobot ping cada 5 min
- O upgrade a Render Starter ($7/mes)

### Cold Start Lento (30-60s)

**Normal en:**
- Primer request después de sleep
- Después de nuevo deploy
- Después de crash/restart

**No es un bug**, es limitación de Render Free Tier.
