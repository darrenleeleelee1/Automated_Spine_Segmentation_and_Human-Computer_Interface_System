import requests
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import matplotlib.pyplot as plt
response = requests.get('http://127.0.0.1:8000/gdicom/13726235')
# print(response.content)
print(type(response.content))

raw = DicomBytesIO(response.content)
ds = dcmread(raw)
arr = ds.pixel_array
print(type(ds))
plt.imshow(arr, cmap="gray")
plt.show()
