from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Esto hace que el buscador cargue apenas entres a elitestaytravel.com
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# Esto sirve para que carguen tus estilos y fotos
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
