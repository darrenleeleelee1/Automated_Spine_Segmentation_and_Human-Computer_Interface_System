from fastapi import FastAPI
import MySQLdb
import MySQLdb.cursors as cursors
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from typing import List
import os, aiofiles
app = FastAPI()

os.system('chcp')

# connection = MySQLdb.connect(
#     host='localhost',user='CDJY',password='C04D10J02Y09',db='sb', cursorclass = cursors.SSCursor)

# if(connection):
#     print("Connection Successful.")
# else:
#     print("Connection Unsuccessful.")

    


@app.get("/gdicom/{medical_number}") # get dicom path
async def get_dicom(medical_number: int):
    dicom_path = "./01372635/5F3279B8"
    return {"01372635", dicom_path}

@app.post("/pdicom/{medical_number}") # save dicoms
async def post_dicom(medical_number: int, files: List[UploadFile] = File(...)):
    directory = f'./tmp/{medical_number}'
    
    
    await aiofiles.os.mkdir(directory)
    
    for file in files:
        async with aiofiles.open(directory + '/' +  file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

    return {'Result': 'OK'}    
    # return {"filenames": [file.filename for file in files]}

