import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
class FaceEngine:
    def __init__(self,use_gpu=True):
        self.app=FaceAnalysis(name='buffalo_l')
        if use_gpu:
            self.app.prepare(ctx_id=0,det_size=(640,640))
        else:
            self.app.prepare(ctx_id=-1,det_size=(640,640))
    def process_image(self,img_bgr):
        faces=self.app.get(img_bgr)
        for face in faces:
            print("Score is :", face.det_score)
            print("Embedding shape is :", face.embedding.shape)
        return faces
if __name__=="__main__":
    engine=FaceEngine(use_gpu=False)
    base_dir = os.path.dirname(__file__)
    img_path = os.path.join(base_dir, "testimage", "LH.jpg")    
    img=cv2.imread(img_path)
    if img is None:
        print("ERROR: Could not load image!")
        print("Please check that the folder 'testimage' exists and contains 'LH.jpg'")
    else:
        print(f"Image loaded successfully. Shape: {img.shape}")
    faces=engine.process_image(img)
    print(f"Found {len(faces)} faces.")