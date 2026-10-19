# app/api/dependencies.py
from functools import lru_cache
from app.infrastructure.database.sqlite_manager import SQLiteManager
from app.infrastructure.llm.openrouter_client import OpenRouterClient
from app.infrastructure.speech.whisper_client import FasterWhisperClient
from app.services.sql_service import SQLService
from app.services.audio_service import AudioService
from app.services.dataset_service import DatasetService

@lru_cache()
def get_llm_client() -> OpenRouterClient:
    return OpenRouterClient()

@lru_cache()
def get_db_manager() -> SQLiteManager:
    return SQLiteManager()

@lru_cache()
def get_stt_client() -> FasterWhisperClient:
    return FasterWhisperClient()

def get_sql_service() -> SQLService:
    return SQLService(llm=get_llm_client(), db=get_db_manager())

def get_audio_service() -> AudioService:
    return AudioService(stt_provider=get_stt_client())

def get_dataset_service() -> DatasetService:
    return DatasetService(db=get_db_manager())