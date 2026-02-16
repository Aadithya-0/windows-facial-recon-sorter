import os
import cv2
import numpy
from engine import FaceEngine
def compute_similarity(embedding1,embedding2):
    similarity=numpy.dot(embedding1,embedding2)/(numpy.linalg.norm(embedding1)*numpy.linalg.norm(embedding2))
    return similarity
if __name__=='__main__':
    engine=FaceEngine(use_gpu=False)
    base_dir = os.path.dirname(__file__)
    img_path = os.path.join(base_dir, "testimage", "LH.jpg")    
    img=cv2.imread(img_path)
    img_path = os.path.join(base_dir, "testimage", "MV.webp")
    img2=cv2.imread(img_path)
    faces1=engine.process_image(img)
    vector1=faces1[0].embedding
    faces2=engine.process_image(img2)
    vector2=faces2[0].embedding
    similarity=compute_similarity(vector1,vector2)
    print("Similarity score between the two faces is :", similarity)