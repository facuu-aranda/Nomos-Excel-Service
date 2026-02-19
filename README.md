# Bento Excel Service

Microservicio FastAPI para procesamiento de archivos Excel y sincronización con Supabase Workspace.

## 🎯 Objetivo

Procesar archivos Excel subidos desde el panel SaaS y convertirlos en dashboards dinámicos en el workspace del usuario.

## 🏗️ Arquitectura

```
Frontend (Next.js) → API Gateway → FastAPI Microservice → Supabase Workspace
                                         ↓
                                    pandas + openpyxl
```

## 📋 Funcionalidades

- ✅ Upload y validación de archivos Excel (.xlsx, .xls)
- ✅ Análisis de estructura de datos
- ✅ Detección automática de tipos de columnas
- ✅ Creación de dashboards en Supabase
- ✅ Inserción de datos procesados
- ✅ Generación de widgets automáticos
- ✅ Manejo de errores y validaciones

## 🚀 Stack Tecnológico

- **FastAPI** - Framework web asíncrono
- **pandas** - Procesamiento de datos
- **openpyxl** - Lectura de archivos Excel
- **supabase-py** - Cliente de Supabase
- **pydantic** - Validación de datos
- **pytest** - Testing
- **uvicorn** - Servidor ASGI

## 📦 Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🔧 Configuración

Crear archivo `.env`:

```env
SUPABASE_URL=your_workspace_supabase_url
SUPABASE_KEY=your_workspace_supabase_key
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
MAX_FILE_SIZE=10485760  # 10MB
```

## 🏃 Ejecución

```bash
# Desarrollo
uvicorn app.main:app --reload --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### GET /health
Health check para monitoreo y wake-up en Render free tier.

**Response:**
```json
{
  "status": "healthy",
  "service": "bento-excel-service",
  "version": "1.0.0",
  "timestamp": "2026-02-19T06:19:30.543630",
  "uptime_seconds": 832.74,
  "supabase_configured": true
}
```

### POST /api/excel/process
Endpoint canónico para subir y procesar un archivo Excel.

**Request:**
```json
{
  "file": "binary",
  "workspace_id": "uuid",
  "user_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "dashboard_id": "uuid",
  "rows_processed": 150,
  "columns": 8
}
```

### POST /api/excel/upload
Alias backward-compatible de `/api/excel/process` (mantenido para compatibilidad).

### POST /api/excel/validate
Valida un archivo Excel sin procesarlo.

**Response:**
```json
{
  "valid": true,
  "sheets": ["Sheet1", "Sheet2"],
  "rows": 150,
  "columns": 8
}
```

### POST /api/excel/preview
Devuelve preview de filas sin persistencia.

**Response:**
```json
{
  "success": true,
  "message": "Preview generado exitosamente",
  "data": {
    "headers": ["name", "amount"],
    "rows": [["Alice", 100]],
    "total_rows": 1,
    "sample_size": 1
  }
}
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html
```

## 🚢 Deployment (Render)

1. Crear cuenta en Render.com
2. Conectar repositorio
3. Configurar variables de entorno
4. Deploy automático en cada push

## 📝 Estructura del Proyecto

```
bento-excel-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuración
│   ├── models/
│   │   ├── __init__.py
│   │   ├── excel.py         # Modelos Pydantic
│   │   └── response.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_processor.py
│   │   └── supabase_client.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── excel.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_excel_processor.py
│   └── test_routes.py
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🔒 Seguridad

- Validación de tipos de archivo
- Límite de tamaño de archivo
- Sanitización de nombres de columnas
- Rate limiting
- CORS configurado
- Autenticación con JWT (opcional)

## 📊 Monitoreo

- Logs estructurados
- Métricas de procesamiento
- Alertas de errores
- Health check endpoint

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Privado - Bento Admin SaaS

## 👥 Autores

- Equipo Bento Admin

---

**Versión:** 1.0.0  
**Última actualización:** Febrero 2026
