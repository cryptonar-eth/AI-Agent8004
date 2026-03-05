from __future__ import annotations
import os
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

class Settings(BaseModel):
    env: str = Field(default="dev")
    dry_run: bool = Field(default=True)  # SAFE DEFAULT
    auto_execute_trades: bool = Field(default=False)  # autonomy gate (requires explicit ack too)
    auto_execute_ack: bool = Field(default=False)     # second factor to prevent accidental enablement
    chain_id: int | None = None
    rpc_url: str | None = None

def _truthy(v: str | None) -> bool:
    if v is None:
        return False
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def load_settings() -> Settings:
    env = os.getenv("ENV", "dev")
    dry_run = _truthy(os.getenv("DRY_RUN", "true"))
    auto_exec = _truthy(os.getenv("AUTO_EXECUTE_TRADES", "false"))
    auto_ack = _truthy(os.getenv("AUTO_EXECUTE_ACK", "false"))
    chain_id = int(os.getenv("CHAIN_ID")) if os.getenv("CHAIN_ID") else None
    rpc_url = os.getenv("RPC_URL")
    return Settings(
        env=env,
        dry_run=dry_run,
        auto_execute_trades=auto_exec,
        auto_execute_ack=auto_ack,
        chain_id=chain_id,
        rpc_url=rpc_url,
    )
