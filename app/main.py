import asyncio
from app.infrastructure.grpc_server.server import serve

if __name__ == "__main__":
    print("Application starting...")
    asyncio.run(serve())
