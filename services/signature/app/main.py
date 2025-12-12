from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from db.config import get_settings
from db.database import engine,Base,get_db
from db.schemes import SignatureCreate,SignatureResponse
from db.models import Signature
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from uuid import UUID
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.service_name} starting...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    
    logger.info(f"{settings.service_name} started")

    yield

    logger.info(f"{settings.service_name} shutting down...")
    await engine.dispose()
    logger.info(f"{settings.service_name} stopped")


app = FastAPI(
    title="Signature Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health/live")
async def liveness():
    """Liveness check."""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness(db:AsyncSession=Depends(get_db)):
    """Readiness probe - checks dependencies. """
    try:
        await db.execute(select(1))
        return {"status":"ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/signatures",response_model=SignatureResponse,status_code=201)
async def create_signature(
    signature: SignatureCreate,
    request:Request,
    background_tasks:BackgroundTasks,
    db:AsyncSession=Depends(get_db)
):

    # Get client IP
    client_ip = signature.ip_address or request.client.host

    # Create signature record

    db_signature=Signature(
        document_id=signature.document_id,
        signer_email=signature.signer_email,
        signer_name=signature.signer_name,
        signature_data=signature.signature_data,
        ip_address=client_ip,
    )   


    db.add(db_signature)
    await db.flush()


    await db.commit()
    await db.refresh(db_signature)
    logger.info(f"Signature created: {db_signature.id} for document {signature.document_id}")
    return db_signature

