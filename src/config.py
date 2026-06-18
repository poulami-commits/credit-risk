"""Central configuration loaded from environment / .env file."""
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Artifact paths
    MODEL_PATH: str = str(BASE_DIR / "models" / "xgb_credit_risk.joblib")

    # Training hyperparameters
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42
    N_ESTIMATORS: int = 500
    MAX_DEPTH: int = 6
    LEARNING_RATE: float = 0.05
    SUBSAMPLE: float = 0.8
    COLSAMPLE_BYTREE: float = 0.8
    MIN_CHILD_WEIGHT: int = 5

    # API
    APP_NAME: str = "Credit Risk Scoring Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Persistence
    DATABASE_URL: str = "sqlite:///./credit_risk.db"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
