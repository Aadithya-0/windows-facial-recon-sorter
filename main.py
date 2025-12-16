import shutil
import os
import cv2
import face_recognition
import numpy as np
from pathlib import Path
from engine import FaceEngine
BASE_DIR = Path(__file__).resolve().parent
# img=face_recognition.load_image_file(BASE_DIR/"testimage"/"img1.webp")
# face_location1=face_recognition.face_locations(img)
# fingerprint1=face_recognition.face_encodings(img,face_location1)
# print(face_location1)
# #print(fingerprint1[0])
# img2=face_recognition.load_image_file(BASE_DIR/"testimage"/"img2.webp")
# face_location2=face_recognition.face_locations(img2)
# fingerprint2=face_recognition.face_encodings(img2,face_location2)
# #print(fingerprint2[0])
# print(face_location2)

# result=face_recognition.compare_faces([fingerprint1[0]],fingerprint2[0])
# print(result)
# folder="testimage"
# for filename in os.listdir(folder):
#     fullpath=os.path.join(folder,filename)
#     img=face_recognition.load_image_file(fullpath)
#     loc=face_recognition.face_locations(img)
#     fingerprint=face_recognition.face_encodings(img,loc)
#     result=face_recognition.compare_faces([fingerprint[0]],)
infolder="testimage"
outfolder="sorted"
engine=FaceEngine(use_cnn=True)
known_fingerprints=[]
known_ids=[]
nextid=1
for filenames in os.listdir(infolder):
    fullpath=os.path.join(infolder,filenames)
    print(f"Scanning:{filenames}...")
    img,loc=engine.get_faces_robust(fullpath)
    if len(locs)==0:
        print(f" ->No faces found moving to nofaces folder.")
        nofacefold=os.path.join(outfolder,"NoFaces")
        os.makedirs(nofacefold,exist_ok=True)
        shutil.copy2(fullpath,nofacefold)
        continue
    fingerprint=face_recognition.face_encodings(img,loc)
    for face_encoding in fingerprint:
        personid=None
        if len(known_fingerprints)>0:
            face_distances=face_recognition.face_distance(known_fingerprints,face_encoding)
            best_match_index=np.argmin(face_distances)
            if face_distances[best_match_index]<0.6:
                personid=known_ids[best_match_index]
                print(f"found person -> {personid}(distance:{face_distances[best_match_index]})")
            else:
                personid=None
        else:
            personid=None
        if personid is None:
            personid=nextid
            print(f"->New face...ID: {personid}")
            known_fingerprints.append(face_encoding)
            known_ids.append(personid)
            nextid+=1
        person_folder=os.path.join(outfolder,f"Person_{personid}")
        os.makedirs(person_folder,exist_ok=True)
        shutil.copy2(fullpath,person_folder)
