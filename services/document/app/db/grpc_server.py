import logging
from concurrent import futures
import grpc
from . import document_service_pb2_grpc
from .config import get_settings
from .grpc_servicer import DocumentServicer
logger = logging.getLogger(__name__)
settings = get_settings()


async def serve_grpc():
    """Start gRPC server.
        Runs alongside the FastAPI HTTP server
    """
    server=grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length",settings.MAX_RECEIVE_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length",settings.MAX_RECEIVE_MESSAGE_LENGTH)
        ],
    )

    # add servicer
    document_service_pb2_grpc.add_DocumentServiceServicer_to_server(
        DocumentServicer(),server
    )

    # Listen on port 50051
    listen_addr="0.0.0.0:50051"
    server.add_insecure_port(listen_addr)

    logger.info(f"gRPC server starting on {listen_addr}")

    await server.start()

    logger.info(f"gRPC server started on {listen_addr}")
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("gRPC server stopping...")
        await server.stop(grace=5)
        logger.info("gRPC server stopped")