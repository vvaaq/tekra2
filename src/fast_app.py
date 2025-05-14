from fastapi import FastAPI, Request
import uvicorn
import socket

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

if __name__ == "__main__":
    uvicorn.run("fast_app:app", host="0.0.0.0", port=8000)
