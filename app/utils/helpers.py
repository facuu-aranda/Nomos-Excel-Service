import uuid
from datetime import datetime


def generate_unique_id() -> str:
    """Genera un ID único"""
    return str(uuid.uuid4())


def format_file_size(size_bytes: int) -> str:
    """Formatea el tamaño de archivo en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def generate_timestamp() -> str:
    """Genera un timestamp en formato ISO"""
    return datetime.utcnow().isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitiza un nombre de archivo"""
    # Remover caracteres no permitidos
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Limitar longitud
    return filename[:255]
