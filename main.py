from utils import *

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from io import BytesIO
from pathlib import Path
import aiofiles
import os
import shutil
from contextlib import asynccontextmanager

import json

app = FastAPI()


UPLOAD_FOLDER = 'uploads'
TEST_DATA_FNAME =  os.path.join(UPLOAD_FOLDER, 'demo_data.sgy')


@app.on_event("shutdown")
def ob_shutdown():      
    for fname in os.listdir(UPLOAD_FOLDER):
        if (os.path.exists(os.path.join(UPLOAD_FOLDER, fname))) and (fname!='demo_data.sgy'):
            os.remove(os.path.join(UPLOAD_FOLDER, fname))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/testdata')
async def get_testdata(request: Request):
    
    shutil.copyfile(TEST_DATA_FNAME, os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy'))    
    data, dt = read_segy(TEST_DATA_FNAME)  
    freq, spec = get_spectrum(data, dt)     
    return [normalize_data(data).tolist(), dt, freq.tolist(), spec.tolist()]


@app.post('/upload')
async def upload_data(request: Request, file: UploadFile = File(...)):     
    file_content = await file.read()    

    uploaded_fname = os.path.join(UPLOAD_FOLDER, f"{request.client.host}.sgy")

    async with aiofiles.open(uploaded_fname, "wb") as f:
        await f.write(file_content)

    data, dt = read_segy(uploaded_fname)     
    freq, spec = get_spectrum(data, dt)

    return [normalize_data(data).tolist(), dt, freq.tolist(), spec.tolist(), file.filename]

@app.post('/update')
async def update_spec(request : Request):    
    request_body = await request.json()
    x0, y0, x1, y1 = request_body
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    uploaded_filename = os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy')
    data, dt = read_segy(uploaded_filename)   
    x0 = round(x0)
    x1 = round(x1)
    y0 = round(y0/dt/1000)
    y1 = round(y1/dt/1000)
    selected_data = data[y0:y1+1, x0:x1+1]
    freq, spec = get_spectrum(selected_data, dt)
    return [freq.tolist(), spec.tolist()]

@app.post('/closed')
async def on_window_close(request: Request):
    if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy')):
        os.remove(os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy'))
