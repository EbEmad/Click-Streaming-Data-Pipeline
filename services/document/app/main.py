from db.schemes import DocumentCreate, DocumentResponse, DocumentUpdate
from db.models import Document,DocumentStatus
from db.database import get_db,engine,Base
from db.config import get_settings
from db.grpc_server import serve_grpc
from db.storage import storage
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from uuid_extensions import uuid7
from contextlib import asynccontextmanager
import asyncio
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info(f"{settings.service_name} starting...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await storage.ensure_buckets()
    grpc_task = asyncio.create_task(serve_grpc())
    logger.info(f"{settings.service_name} started - HTTP: 8000")
    yield
   
    logger.info(f"{settings.service_name} shutting down...")
    grpc_task.cancel()
    try:
        await grpc_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()

app=FastAPI(title="Document Service",version="1.0.0",lifespan=lifespan)



@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(db:AsyncSession=Depends(get_db)):
    try:
        await db.execute(select(1))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service is not ready")

@app.post("/documents",response_model=DocumentResponse,status_code=201)
async def create_document(document:DocumentCreate,db: AsyncSession = Depends(get_db)):
    """Create document with async pg upload."""

    document_id=uuid7()
    content_bytes = document.content.encode("utf-8")
    s3_key=await storage.upload_document(str(document_id), content_bytes)

    db_document=Document(
        id=document_id,
        title=document.title,
        content_type=document.content_type,
        content_size=len(content_bytes),
        s3_key=s3_key,
        created_by=document.created_by,
        status=DocumentStatus.CREATED.value,
    )

    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    logger.info(f"Document created: {document_id}")
    return db_document

@app.get("/documents", response_model=list[DocumentResponse])
async def list_documents(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List documents with pagination."""
    result = await db.execute(
        select(Document).offset(skip).limit(limit).order_by(Document.created_at.desc())
    )
    return result.scalars().all()
    
@app.get("/documents/{document_id}",response_model=DocumentResponse)
async def get_document(
        document_id:UUID,
        request:Request,
        db:AsyncSession=Depends(get_db)
    ):


    # Cache miss - get from database
    result=await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise  HTTPException(status_code=404, detail="Document not found")
    return document

@app.patch("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
        document_id:UUID,
        update:DocumentUpdate,
        db:AsyncSession=Depends(get_db)
    ):
    """Update document with optimistic locking."""
    result=await db.execute(select(Document).where(Document.id==document_id))
    document=result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404,detail="Document not found")
    
    for field,value in update.model_dump(exclude_unset=True).items():
        setattr(document,field,value)
    
    document.version+=1
    await db.commit()
    await db.refresh(document)
    logger.info(f"Document updated: {document_id} v{document.version}")
    return document


    
