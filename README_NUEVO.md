# 📊 Nomos Excel Service

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688.svg)
![License](https://img.shields.io/badge/License-Private-red.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

**Microservicio de procesamiento inteligente de archivos Excel para Nomos SaaS Platform**

[Características](#-características-principales) • [Instalación](#-instalación) • [API](#-api-endpoints) • [Arquitectura](#-arquitectura)

</div>

---

## 🎯 Descripción

**Nomos Excel Service** es un microservicio FastAPI especializado en el procesamiento inteligente de archivos Excel. Diseñado como parte de la plataforma Nomos SaaS, este servicio transforma hojas de cálculo en datos estructurados listos para visualización, generando automáticamente configuraciones de widgets (KPIs, gráficos, tablas) basándose en el análisis de tipos de datos.

### ¿Por qué un microservicio separado?

- **Escalabilidad Independiente**: Procesa archivos pesados sin afectar el frontend
- **Especialización**: Optimizado para operaciones intensivas de datos con pandas
- **Aislamiento**: Fallos en procesamiento no afectan la aplicación principal
- **Tecnología Específica**: Python/pandas es ideal para manipulación de datos
- **Despliegue Flexible**: Puede escalar horizontalmente según demanda

---

## ✨ Características Principales

### 🔍 Procesamiento Inteligente
- ✅ **Multi-Hoja**: Procesa todas las hojas de un archivo Excel simultáneamente
- ✅ **Detección Automática de Tipos**: Identifica números, fechas, texto, booleanos
- ✅ **Limpieza de Datos**: Sanitización de nombres de columnas y valores NaN
- ✅ **Validación Robusta**: Verifica formato, tamaño y estructura

### 🎨 Generación Automática de Widgets
- 📊 **Tablas**: Configuración con columnas, ordenamiento y filtrado
- 📈 **KPIs**: Agregaciones automáticas (SUM, AVG, COUNT)
- 📊 **Gráficos de Barras**: Detección de ejes X/Y apropiados
- 📉 **Gráficos de Línea**: Ideal para series temporales
- 🥧 **Gráficos de Torta**: Distribución de categorías

### 👥 Detección de Importación de Usuarios
- 🔍 Identifica hojas con estructura de usuarios (email, nombre, rol)
- 🗺️ Mapeo automático de columnas
- ✅ Sugerencia de importación al workspace

### 💾 Persistencia en Supabase
- 🗄️ Creación dinámica de tablas en Supabase Workspace
- 📝 Almacenamiento de metadatos en `data_tables_metadata`
- 🔐 Integración con Row Level Security (RLS)

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
Nomos-Excel-Service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app principal
│   ├── config.py                  # Configuración y variables de entorno
│   │
│   ├── contracts/                 # Interfaces (Dependency Inversion)
│   │   ├── __init__.py
│   │   ├── excel_processor.py    # IExcelProcessor interface
│   │   └── database_client.py    # IDatabaseClient interface
│   │
│   ├── factories/                 # Factory pattern para DI
│   │   ├── __init__.py
│   │   ├── excel_factory.py
│   │   └── database_factory.py
│   │
│   ├── infrastructure/            # Implementaciones concretas
│   │   ├── __init__.py
│   │   └── supabase_client.py    # Cliente de Supabase
│   │
│   ├── models/                    # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── excel.py              # Request/Response models
│   │   └── response.py           # Response genéricos
│   │
│   ├── routes/                    # Endpoints de la API
│   │   ├── __init__.py
│   │   └── excel.py              # Rutas de procesamiento Excel
│   │
│   ├── services/                  # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── excel_processor.py    # Procesador principal
│   │   └── supabase_client.py    # Cliente Supabase (legacy)
│   │
│   └── utils/                     # Utilidades
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/                         # Suite de tests
│   ├── __init__.py
│   ├── test_excel_processor.py
│   ├── test_routes.py
│   └── test_supabase_client.py
│
├── migrations/                    # Migraciones de BD (si aplica)
├── .env.example                   # Ejemplo de variables de entorno
├── .gitignore
├── requirements.txt               # Dependencias de producción
├── requirements-latest.txt        # Dependencias con últimas versiones
├── pytest.ini                     # Configuración de pytest
├── runtime.txt                    # Versión de Python para Render
└── README.md
```

### Principios de Diseño

#### Clean Architecture
```
┌─────────────────────────────────────────────────────┐
│                    Presentation                      │
│              (routes/excel.py - FastAPI)             │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                   Application                        │
│         (services/excel_processor.py)                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                     Domain                           │
│        (contracts/ - Interfaces abstractas)          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                 Infrastructure                       │
│    (infrastructure/supabase_client.py - Impl.)       │
└─────────────────────────────────────────────────────┘
```

#### Dependency Injection
- **Contracts**: Interfaces abstractas definen el comportamiento
- **Factories**: Crean instancias concretas
- **FastAPI Depends**: Inyecta dependencias en endpoints

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.11 o superior
- pip o poetry
- Cuenta de Supabase (Workspace instance)

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd Nomos-Excel-Service
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp .env.example .env
```

Editar `.env`:
```env
# Supabase Workspace (Instancia 2)
SUPABASE_URL=https://your-workspace-project.supabase.co
SUPABASE_KEY=your-workspace-service-role-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Configuración
MAX_FILE_SIZE=10485760  # 10MB en bytes
APP_ENV=development

# Opcional: Logging
LOG_LEVEL=INFO
```

### 5. Ejecutar el Servidor

#### Desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```

#### Producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servicio estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

---

## 📚 API Endpoints

### 🏥 Health Check

#### `GET /health`
Endpoint de monitoreo para verificar el estado del servicio.

**Response:**
```json
{
  "status": "healthy",
  "service": "bento-excel-service",
  "version": "1.0.0",
  "timestamp": "2026-02-22T10:30:00.123456",
  "uptime_seconds": 3600.45,
  "supabase_configured": true,
  "environment": "production"
}
```

---

### 📊 Procesamiento de Excel

#### `POST /api/excel/process` ⭐ **Recomendado**
Endpoint principal para procesar archivos Excel con soporte multi-hoja y generación automática de widgets.

**Request:**
- `Content-Type: multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `file` | File | ✅ | Archivo Excel (.xlsx, .xls) |
| `workspace_id` | string | ✅ | UUID del workspace |
| `user_id` | string | ✅ | UUID del usuario |

**Response:**
```json
{
  "success": true,
  "message": "3 hoja(s) procesada(s) exitosamente. 12 widget(s) sugerido(s).",
  "sheets_processed": 3,
  "sheets": [
    {
      "sheet_name": "Ventas",
      "table_name": "ventas_20260222_103000",
      "rows": 150,
      "columns": 8,
      "column_types": {
        "fecha": "date",
        "vendedor": "string",
        "monto": "number",
        "cantidad": "integer"
      },
      "sample_rows": [
        {
          "fecha": "2026-01-01",
          "vendedor": "Juan Pérez",
          "monto": 1500.50,
          "cantidad": 10
        }
      ],
      "widget_suggestions": [
        {
          "widget_type": "table",
          "title": "Ventas",
          "table_name": "ventas_20260222_103000",
          "config": {
            "columns": ["fecha", "vendedor", "monto", "cantidad"],
            "sortable": true,
            "filterable": true,
            "pageSize": 20
          }
        },
        {
          "widget_type": "kpi",
          "title": "Total monto",
          "table_name": "ventas_20260222_103000",
          "config": {
            "column": "monto",
            "aggregation": "SUM",
            "label": "Monto",
            "format": "number",
            "showVariation": false
          }
        },
        {
          "widget_type": "bar_chart",
          "title": "Ventas — Barras",
          "table_name": "ventas_20260222_103000",
          "config": {
            "xAxis": "vendedor",
            "yAxis": "monto",
            "aggregation": "SUM",
            "orientation": "vertical",
            "color": "#228BE6"
          }
        }
      ],
      "suggests_user_import": false,
      "user_columns": null
    }
  ],
  "tables": [
    "ventas_20260222_103000",
    "gastos_20260222_103000",
    "balance_20260222_103000"
  ],
  "processing_time": 2.45,
  "widgets_created": 12
}
```

**Códigos de Estado:**
- `200`: Procesamiento exitoso
- `400`: Archivo inválido o parámetros incorrectos
- `413`: Archivo demasiado grande
- `500`: Error en el procesamiento

---

#### `POST /api/excel/upload`
Endpoint legacy para compatibilidad. Procesa una sola hoja y crea un dashboard.

**Request:**
- `Content-Type: multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `file` | File | ✅ | Archivo Excel |
| `workspace_id` | string | ✅ | UUID del workspace |
| `user_id` | string | ✅ | UUID del usuario |
| `dashboard_name` | string | ❌ | Nombre del dashboard (default: nombre del archivo) |

**Response:**
```json
{
  "success": true,
  "dashboard_id": "uuid-del-dashboard",
  "rows_processed": 150,
  "columns": 8,
  "table_name": "ventas_20260222_103000",
  "widgets_created": 1,
  "processing_time": 1.23,
  "message": "Excel procesado exitosamente. Dashboard 'Ventas' creado con 150 filas."
}
```

---

#### `POST /api/excel/validate`
Valida un archivo Excel sin procesarlo ni persistir datos.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: Archivo Excel

**Response:**
```json
{
  "valid": true,
  "sheets": ["Ventas", "Gastos", "Balance"],
  "rows": 150,
  "columns": 8,
  "column_info": [
    {
      "name": "fecha",
      "type": "date",
      "nullable": false,
      "unique_values": 30
    },
    {
      "name": "monto",
      "type": "number",
      "nullable": false,
      "unique_values": 145
    }
  ],
  "file_size": 45678,
  "errors": []
}
```

---

#### `POST /api/excel/preview`
Obtiene una vista previa de las primeras filas sin persistir.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: Archivo Excel
- `rows`: Número de filas (default: 10)

**Response:**
```json
{
  "success": true,
  "message": "Preview generado exitosamente",
  "data": {
    "headers": ["fecha", "vendedor", "monto", "cantidad"],
    "rows": [
      ["2026-01-01", "Juan Pérez", 1500.50, 10],
      ["2026-01-02", "María García", 2300.00, 15]
    ],
    "total_rows": 2,
    "sample_size": 2
  }
}
```

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_excel_processor.py

# Modo verbose
pytest -v

# Con logs
pytest -s
```

### Cobertura Actual
- **Target**: ≥90%
- **Actual**: ~85% (en progreso)

### Estructura de Tests
```
tests/
├── test_excel_processor.py    # Tests del procesador
├── test_routes.py              # Tests de endpoints
├── test_supabase_client.py    # Tests de integración
└── fixtures/                   # Archivos Excel de prueba
    ├── valid_sales.xlsx
    ├── multi_sheet.xlsx
    └── invalid_format.xls
```

---

## 🔧 Configuración

### Variables de Entorno

| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `SUPABASE_URL` | ✅ | - | URL de Supabase Workspace |
| `SUPABASE_KEY` | ✅ | - | Service Role Key de Workspace |
| `ALLOWED_ORIGINS` | ✅ | `*` | Orígenes CORS permitidos (separados por coma) |
| `MAX_FILE_SIZE` | ❌ | `10485760` | Tamaño máximo de archivo en bytes (10MB) |
| `APP_ENV` | ❌ | `development` | Entorno de ejecución |
| `LOG_LEVEL` | ❌ | `INFO` | Nivel de logging |

### Configuración de CORS
```python
# En app/config.py
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com",
    "https://your-domain.vercel.app"
]
```

---

## 🚢 Deployment

### Render.com (Recomendado)

1. **Conectar Repositorio**
   - Crear nuevo Web Service en Render
   - Conectar con GitHub/GitLab

2. **Configurar Build**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Variables de Entorno**
   - Agregar todas las variables requeridas
   - Usar secretos para keys sensibles

4. **Plan**
   - Free Tier: Disponible (con sleep después de inactividad)
   - Starter: $7/mes (siempre activo)

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t nomos-excel-service .
docker run -p 8000:8000 --env-file .env nomos-excel-service
```

---

## 🔒 Seguridad

### Validaciones Implementadas
- ✅ Verificación de extensión de archivo (.xlsx, .xls)
- ✅ Límite de tamaño de archivo configurable
- ✅ Sanitización de nombres de columnas
- ✅ Limpieza de valores NaN y datos maliciosos
- ✅ Validación de workspace_id y user_id
- ✅ CORS configurado estrictamente

### Recomendaciones
- 🔐 Nunca exponer `SUPABASE_KEY` en el frontend
- 🔐 Usar Service Role Key solo en backend
- 🔐 Implementar rate limiting en producción
- 🔐 Monitorear logs de errores
- 🔐 Actualizar dependencias regularmente

---

## 📊 Monitoreo

### Logs Estructurados
```python
logger.info(f"Processing Excel file: {filename} for workspace: {workspace_id}")
logger.error(f"Error processing Excel: {str(e)}")
```

### Métricas Recomendadas
- Tiempo de procesamiento por archivo
- Número de filas procesadas
- Tasa de errores
- Uptime del servicio
- Uso de memoria

### Health Check
Configurar monitoreo externo para llamar a `/health` cada 5 minutos.

---

## 🤝 Integración con NomoSaaS

### Flujo de Integración

```typescript
// En Next.js API Route
const formData = new FormData()
formData.append('file', file)
formData.append('workspace_id', workspaceId)
formData.append('user_id', userId)

const response = await fetch('https://excel-service.render.com/api/excel/process', {
  method: 'POST',
  body: formData
})

const result = await response.json()

// Crear dashboards y widgets con las sugerencias
await createDashboardsFromExcel(workspaceId, result.sheets)
await createWidgetsFromSuggestions(result.sheets, dashboards)
```

---

## 🐛 Troubleshooting

### Error: "Archivo demasiado grande"
**Solución**: Aumentar `MAX_FILE_SIZE` en variables de entorno

### Error: "Supabase connection failed"
**Solución**: Verificar `SUPABASE_URL` y `SUPABASE_KEY`

### Error: "CORS policy blocked"
**Solución**: Agregar origen a `ALLOWED_ORIGINS`

### Servicio en Render no responde
**Solución**: Free tier duerme después de inactividad. Llamar a `/health` para despertar.

---

## 📈 Performance

### Optimizaciones Implementadas
- ✅ Procesamiento asíncrono con FastAPI
- ✅ Lectura eficiente con pandas
- ✅ Limpieza de memoria después de procesar
- ✅ Streaming de respuestas grandes

### Benchmarks
- Archivo 1MB (1000 filas): ~1-2 segundos
- Archivo 5MB (5000 filas): ~3-5 segundos
- Archivo 10MB (10000 filas): ~6-10 segundos

---

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

---

## 👥 Contribución

Este es un proyecto privado. Para contribuir:
1. Crear rama feature desde `main`
2. Implementar cambios con tests
3. Asegurar cobertura ≥90%
4. Crear Pull Request
5. Esperar code review

---

## 📞 Soporte

Para problemas o preguntas:
- Revisar documentación en `/docs`
- Consultar logs del servicio
- Contactar al equipo de desarrollo

---

**Nomos Excel Service** - *Transformando Excel en datos inteligentes*

Versión: 1.0.0 | Última actualización: Febrero 2026
