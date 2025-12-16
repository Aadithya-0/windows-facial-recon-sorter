import shutil
import os
import cv2
import face_recognition
import numpy as np
from pathlib import Path
class FaceEngine:
    def __init__(self,use_cnn=True):
        self.model="cnn" if use_cnn else "hog"
        self.upsample=1
        print(f"   [Engine] Initialized using model: {self.model}")       
    def get_faces_robust(self,image_path):
        image=face_recognition.load_image_file(image_path)
        locs=face_recognition.face_locations(image,model=self.model)
        if len(locs)>0:
            print("->Found face directly")
            return image,locs
        rot_img=np.rot90(image,k=1)
        locs=face_recognition.face_locations(rot_img,model=self.model)
        if len(locs)>0:
            print("->Found face after 90 degree rotation")
            return rot_img,locs
        rot_img=np.rot90(image,k=3)
        locs=face_recognition.face_locations(rot_img,model=self.model)
        if len(locs)>0:
            print("->Found face 270 degree rotation")
            return rot_img,locs
        return image,[]
