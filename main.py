from utils import *

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from io import BytesIO
from pathlib import Path
import aiofiles

import json

app = FastAPI()


UPLOADED_FNAME = 'uploads/uploaded.sgy'
TEST_DATA_FNAME = 'uploads/demo_data.sgy'
data = None
dt = 0

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/get_testdata')
async def get_testdata():  
    global data, dt
    data, dt = read_segy(TEST_DATA_FNAME)  
    freq, spec = get_spectrum(data, dt)     
    return [normalize_data(data).tolist(), dt, freq.tolist(), spec.tolist()]


@app.post('/upload')
async def upload_data(file: UploadFile = File(...)):  
    global data, dt 
    file_content = await file.read()    

    async with aiofiles.open(UPLOADED_FNAME, "wb") as f:
        await f.write(file_content)

    data, dt = read_segy(UPLOADED_FNAME)      
    freq, spec = get_spectrum(data, dt)

    return [normalize_data(data).tolist(), dt, freq.tolist(), spec.tolist(), file.filename]

@app.post('/update_spec')
async def update_spec(request : Request):
    global data, dt
    request_body = await request.json()
    x0, y0, x1, y1 = request_body
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    x0 = round(x0)
    x1 = round(x1)
    y0 = round(y0/dt/1000)
    y1 = round(y1/dt/1000)
    print(x0, x1, y0, y1)
    selected_data = data[y0:y1+1, x0:x1+1]
    freq, spec = get_spectrum(selected_data, dt)
    return [freq.tolist(), spec.tolist()]

