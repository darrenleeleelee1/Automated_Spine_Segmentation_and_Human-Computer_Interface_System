from fastapi import FastAPI
import MySQLdb
import MySQLdb.cursors as cursors
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from typing import List
import os
app = FastAPI()

os.system('chcp')

# connection = MySQLdb.connect(
#     host='localhost',user='CDJY',password='C04D10J02Y09',db='sb', cursorclass = cursors.SSCursor)

# if(connection):
#     print("Connection Successful.")
# else:
#     print("Connection Unsuccessful.")

# class pt_dicom(BaseModel):


@app.get("/gdicom/{medical_number}") # get dicom path
async def get_dicom(medical_number: int):
    dicom_path = './01372635/5F3279B8'
    return {'01372635', dicom_path}

@app.post("/pdicom") # save dicoms
async def post_dicom(file: UploadFile = File(...)):
    return {'filename': file.filename}

@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}