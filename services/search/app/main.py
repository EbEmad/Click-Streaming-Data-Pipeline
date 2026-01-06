import logging
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI, HTTPException, Query
from .config import get_settings


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def get_es_client()->AsyncElasticsearch:
    """Dependency to get Elasticsearch client."""
    if not hasattr(app.state,"es_client"):
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch client not initialized"
        )
    return app.state.es_client


@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Search Service starting...")
    app.state.es_client = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        request_timeout=30
    )

    try:
        info=await app.state.es_client.info()
        logger.info(f"Connected to Elasticsearch {info['version']['number']}")
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        raise
    
    yield

    await app.state.es_client.close()
    logger.info("Search Service shutdown complete")

app = FastAPI(
    title="Search Service",
    description="Read-only search API for documents",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health/live")
async def liveness():
    """Liveness probe."""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(es:AsyncElasticsearch=Depends(get_es_client)):
    """Readiness probe - checks Elasticsearch connection."""
    try:
        info=await es.info()
        return {"status": "ready", "elasticsearch": info["version"]["number"]}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Elasticsearch unavailable") from e
    

@app.get("/search")
async def search(
    q:str=Query(..., min_length=1, description="Search query"),
    status:str | None = Query(None, description="Filter by status"),
    created_by: str | None = Query(None, description="Filter by creator"),
    min_quality_score: float | None = Query(None, ge=0, le=100, description="Minimum quality score"),
    exclude_pii: bool = Query(False, description="Exclude documents with PII"),
    from_: int=Query(0, ge=0, alias="from", description="Offset"),
    size:int=Query(10, ge=1, le=100, description="Number of results"),
    es: AsyncElasticsearch = Depends(get_es_client)
):
    """
    Search documents with filters including quality score.
    
    Example: GET /search?q=contract&status=signed&min_quality_score=70&from=0&size=10
    """

    try:
        must_clauses=[
            {
                "multi_match":{
                    "query":q,
                    "fields": ["title^2", "created_by"],  # ← Fixed
                    "fuzziness": "AUTO",
                }
            }

        ]
        filter_clauses=[]

        if status:
            filter_clauses.append({"term": {"status": status}})
        if created_by:
            filter_clauses.append({"term": {"created_by.keyword": created_by}})
        if min_quality_score is not None:
            filter_clauses.append({"range": {"quality_score": {"gte": min_quality_score}}})
        if exclude_pii:
            filter_clauses.append({"term": {"has_pii": False}})
        search_body={
            "query":{
                "bool":{"must":must_clauses, "filter":filter_clauses}
            },
            "from":from_,
            "size":size,
            "sort": [
                {"_score": {"order": "desc"}},
                {"created_at": {"order": "desc"}}
            ],
            "highlight": {
                "fields": {
                    "title": {}
                }
            },
        }


        response=await es.search(
            index=settings.elasticsearch_index,
            body=search_body
        )

        hits = response["hits"]
        return {
            "total": hits["total"]["value"],
            "documents": [
                {
                    **hit["_source"],
                    "score": hit["_score"],
                    "highlights": hit.get("highlight", {}),
                }
                for hit in hits["hits"]
            ],
            "took_ms": response["took"],
            "from": from_,
            "size": size,
        }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed") from e
    
    