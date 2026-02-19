from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.models import ExcelValidationResponse, SuccessResponse
from app.models.excel import ExcelProcessingResult
from app.contracts import IExcelProcessor, IDatabaseClient
from app.factories import get_excel_processor, get_database_client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def _process_excel_upload(
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    user_id: str = Form(...),
    dashboard_name: str = Form(None),
    excel_processor: IExcelProcessor = Depends(get_excel_processor),
    db_client: IDatabaseClient = Depends(get_database_client),
):
    """Shared Excel processing logic for upload/process endpoints."""
    try:
        # Validar tamaño del archivo
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo: {settings.max_file_size / 1024 / 1024}MB"
            )
        
        # Validar archivo
        is_valid, errors = excel_processor.validate_file(file_content, file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # Procesar Excel
        logger.info(f"Processing Excel file: {file.filename} for workspace: {workspace_id}")
        processing_result = excel_processor.process_excel(
            file_content,
            workspace_id,
            dashboard_name or file.filename.rsplit('.', 1)[0]
        )
        
        if not processing_result["success"]:
            raise HTTPException(status_code=500, detail=processing_result.get("error"))
        
        # Crear dashboard en Supabase
        dashboard = await db_client.create_dashboard(
            workspace_id=workspace_id,
            name=dashboard_name or file.filename.rsplit('.', 1)[0],
            description=f"Dashboard generado desde {file.filename}",
            icon="table",
            color="#228BE6"
        )
        
        # ✅ IMPLEMENTADO: Persistir datos en Supabase
        rows_stored = await db_client.store_excel_data(
            workspace_id=workspace_id,
            table_name=processing_result["table_name"],
            data=processing_result["data"],
            column_types=processing_result["column_types"]
        )
        
        logger.info(f"Stored {rows_stored} rows in Supabase for table {processing_result['table_name']}")
        
        # Crear widget de tabla
        await db_client.create_widget(
            dashboard_id=dashboard["id"],
            widget_type="table",
            config={
                "title": "Datos de Excel",
                "columns": processing_result["column_names"],
                "data_source": processing_result["table_name"],
                "column_types": processing_result["column_types"],
            }
        )
        
        return ExcelProcessingResult(
            success=True,
            dashboard_id=dashboard["id"],
            rows_processed=rows_stored,
            columns=processing_result["columns"],
            table_name=processing_result["table_name"],
            widgets_created=1,
            processing_time=processing_result["processing_time"],
            message=f"Excel procesado exitosamente. Dashboard '{dashboard['name']}' creado con {rows_stored} filas."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=ExcelProcessingResult)
async def upload_excel(
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    user_id: str = Form(...),
    dashboard_name: str = Form(None),
    excel_processor: IExcelProcessor = Depends(get_excel_processor),
    db_client: IDatabaseClient = Depends(get_database_client),
):
    """
    Sube y procesa un archivo Excel

    - **file**: Archivo Excel (.xlsx, .xls)
    - **workspace_id**: ID del workspace
    - **user_id**: ID del usuario
    - **dashboard_name**: Nombre opcional del dashboard
    """
    return await _process_excel_upload(
        file=file,
        workspace_id=workspace_id,
        user_id=user_id,
        dashboard_name=dashboard_name,
        excel_processor=excel_processor,
        db_client=db_client,
    )


@router.post("/process", response_model=ExcelProcessingResult)
async def process_excel(
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    user_id: str = Form(...),
    dashboard_name: str = Form(None),
    excel_processor: IExcelProcessor = Depends(get_excel_processor),
    db_client: IDatabaseClient = Depends(get_database_client),
):
    """
    Endpoint canónico para procesar un archivo Excel (MVP Fase 5).

    - **file**: Archivo Excel (.xlsx, .xls)
    - **workspace_id**: ID del workspace
    - **user_id**: ID del usuario
    - **dashboard_name**: Nombre opcional del dashboard
    """
    return await _process_excel_upload(
        file=file,
        workspace_id=workspace_id,
        user_id=user_id,
        dashboard_name=dashboard_name,
        excel_processor=excel_processor,
        db_client=db_client,
    )


@router.post("/validate", response_model=ExcelValidationResponse)
async def validate_excel(
    file: UploadFile = File(...),
    excel_processor: IExcelProcessor = Depends(get_excel_processor),
):
    """
    Valida un archivo Excel sin procesarlo
    
    - **file**: Archivo Excel a validar
    """
    try:
        file_content = await file.read()
        
        # Validar archivo
        is_valid, errors = excel_processor.validate_file(file_content, file.filename)
        if not is_valid:
            return ExcelValidationResponse(
                valid=False,
                sheets=[],
                rows=0,
                columns=0,
                column_info=[],
                file_size=len(file_content),
                errors=errors
            )
        
        # Analizar archivo
        analysis = excel_processor.analyze_file(file_content)
        
        return ExcelValidationResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error validating Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_excel(
    file: UploadFile = File(...),
    rows: int = Form(10),
    excel_processor: IExcelProcessor = Depends(get_excel_processor),
):
    """
    Obtiene un preview de los datos del Excel
    
    - **file**: Archivo Excel
    - **rows**: Número de filas a mostrar (default: 10)
    """
    try:
        file_content = await file.read()
        
        # Validar archivo
        is_valid, errors = excel_processor.validate_file(file_content, file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # Obtener preview
        preview = excel_processor.get_data_preview(file_content, rows)
        
        return SuccessResponse(
            message="Preview generado exitosamente",
            data=preview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
