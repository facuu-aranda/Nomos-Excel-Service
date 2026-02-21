from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    
    # CORS
    allowed_origins: str = "http://localhost:3000"
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = ".xlsx,.xls"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # JWT (opcional)
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convierte la cadena de orígenes permitidos en lista"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convierte la cadena de extensiones permitidas en lista"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


settings = Settings()
