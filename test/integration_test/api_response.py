import requests
import numpy as np
import json

image=np.random.rand(128,128)*255
image=image.astype('uint8').tolist()
response = requests.post('http://10.3.32.88:8000/process',json={'name': 'cell_detect', 'image': json.dumps(image)}, timeout=(300, 300))