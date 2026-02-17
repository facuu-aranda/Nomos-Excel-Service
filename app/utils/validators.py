from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def validate_workspace_access(
    workspace_id: str,
    user_id: str
) -> bool:
    """
    Valida que un usuario tenga acceso a un workspace
    
    En producción, esto debería verificar en Supabase que el usuario
    pertenece al workspace especificado
    """
    # TODO: Implementar validación real con Supabase
    # Por ahora, retornamos True para desarrollo
    logger.info(f"Validating access for user {user_id} to workspace {workspace_id}")
    return True


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Valida que la extensión del archivo sea permitida"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def validate_file_size(file_size: int, max_size: int) -> bool:
    """Valida que el tamaño del archivo no exceda el máximo permitido"""
    return file_size <= max_size
