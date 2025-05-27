# fast_app.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
import socket
import uvicorn

app = FastAPI()


@app.get("/")
async def get_ip_addresses(request: Request):
    # Get client IP
    client_ip = request.client.host

    # Get host IP
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)

    return {
        "client_ip": client_ip,
        "host_ip": host_ip,
        "host_name": host_name
    }


@app.get("/ip")
def get_ip():
    import requests
    return {"ip": requests.get("https://api.ipify.org").text}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Получаем IP клиента
        client_host, client_port = websocket.client

        # Получаем IP и имя сервера
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)

        await websocket.send_json({
            "status": "connected",
            "client_ip": client_host,
            "host_ip": host_ip,
            "host_name": host_name
        })

        while True:
            # Echo, чтобы WebSocket не закрылся
            msg = await websocket.receive_text()
            await websocket.send_text(f"echo: {msg}")

    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
