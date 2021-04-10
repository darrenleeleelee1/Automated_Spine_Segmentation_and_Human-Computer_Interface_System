from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import List
import MySQLdb
import MySQLdb.cursors as cursors
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
    # dicom_path = "./01372635/5F3279B8"
    # return {"01372635", dicom_path}
    root = './tmp'
    # dicom_path = os.path.join(root, str(medical_number))
    dicom_path = './tmp/13726235/5F3279B8'
    if os.path.exists(dicom_path):
        return FileResponse(dicom_path, media_type="application/dicom")
    return {'error': 'File not found.'}

@app.post("/pdicom/{medical_number}") # save dicoms
async def post_dicom(medical_number: int, files: List[UploadFile] = File(...)):
    directory = f'./tmp/{medical_number}'
    
    
    await aiofiles.os.mkdir(directory)
    
    for file in files:
        async with aiofiles.open(directory + '/' +  file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

    # return {"files": [file.read() for file in files]}
    return {'Result': 'OK'}    

@app.post("/files/")
async def create_file(fir: bytes = UploadFile(...)):
    return {'Result': 'OK'}

import uvicorn
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)