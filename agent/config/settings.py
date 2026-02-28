from __future__ import annotations
from pydantic import BaseModel, Field
import os

class Settings(BaseModel):
    env: str = Field(default="dev")
    dry_run: bool = Field(default=True)  # SAFE DEFAULT
    chain_id: int | None = None
    rpc_url: str | None = None

def load_settings() -> Settings:
    env = os.getenv("ENV", "dev")
    dry_run = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes", "y")
    chain_id = int(os.getenv("CHAIN_ID")) if os.getenv("CHAIN_ID") else None
    rpc_url = os.getenv("RPC_URL")
    return Settings(env=env, dry_run=dry_run, chain_id=chain_id, rpc_url=rpc_url)
