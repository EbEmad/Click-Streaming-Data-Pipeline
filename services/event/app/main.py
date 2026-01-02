import logging
import signal
from typing import Any

from quixstreams import Application
from quixstreams.sinks.base.item import SinkItem
from quixstreams.sinks.community.elasticsearch import ElasticsearchSink

from .config import get_settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


class EventProcessor:
    """CDC event processor with Elasticsearch indexing."""


    def __init__(self):
        self.app=Application(
            broker_address=settings.kafka_bootstrap_servers,
            consumer_group=settings.kafka_consumer_group,
            auto_offset_reset="earliest",
        )

    def _transform_for_elasticsearch(
        self,
        value: dict[str, Any],
        key: Any,
        timestamp: int,
        headers: list[tuple[str, bytes]] | None,
    )->dict[str,Any] | None:
        """Transform CDC event to Elasticsearch document."""
        try:
            op=value.get("op")
            # Skip snapshots and deletes
            if op in ["r","d"]:
                return None
            
            after=value.get('after',{})
            document_id=after.get("id")
            # Skip if no S3 content yet
            if not after.get("s3_key"):
                return None

            # Transform to ES document
            return {
                "id": str(document_id),
                "title": after.get("title", ""),
                "status": after.get("status", "created"),
                "created_by": after.get("created_by", ""),
                "content_type": after.get("content_type"),
                "content_size": after.get("content_size", 0),
                "created_at": after.get("created_at"),
                "updated_at": after.get("updated_at"),
                "version": after.get("version", 1),
            }

        except Exception as e:
            logger.error(f"Failed to transform event: {e}")
            return None
    def start(self):
        logger.info(f"{settings.service_name} starting...")

        try:
            # Document ID extractor for ES
            def get_document_id(item:SinkItem)->str:
                return str(item.value.get("id"))
            
            es_sink = ElasticsearchSink(
                url=settings.elasticsearch_url,
                index=settings.elasticsearch_index_documents,
                document_id_setter=get_document_id,
                batch_size=50,
                mapping={
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "title": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                            "status": {"type": "keyword"},
                            "created_by": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                            "content_type": {"type": "keyword"},
                            "content_size": {"type": "long"},
                            "created_at": {
                                "type": "date",
                                "format": "strict_date_optional_time||epoch_millis",
                            },
                            "updated_at": {
                                "type": "date",
                                "format": "strict_date_optional_time||epoch_millis",
                            },
                            "version": {"type": "integer"},
                        }
                    }
                },
            )

            # Documents topic
            topic = self.app.topic(settings.cdc_documents_topic, value_deserializer="json")

            sdf = self.app.dataframe(topic)
            sdf = sdf.apply(self._transform_for_elasticsearch, metadata=True)
            sdf = sdf.filter(lambda v: v is not None)
            sdf.sink(es_sink)

            logger.info(f"Processing: {settings.cdc_documents_topic} -> Elasticsearch")

            self.app.run()
        except KeyboardInterrupt:
            logger.info("Stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise



def main():
    EventProcessor().start()


if __name__ == "__main__":
    main()
