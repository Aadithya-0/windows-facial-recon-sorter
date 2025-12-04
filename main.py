import shutil
import os
import cv2
import face_recognition
from pathlib import Path
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
known_fingerprints=[]
known_ids=[]
nextid=1
for filenames in os.listdir(infolder):
    fullpath=os.path.join(infolder,filenames)
    print(f"Scanning:{filenames}...")
    img=face_recognition.load_image_file(fullpath)
    loc=face_recognition.face_locations(img)
    fingerprint=face_recognition.face_encodings(img,loc)
    for face_encoding in fingerprint:
        matches=[]
        personid=None
        if len(known_fingerprints)>0:
            matches=face_recognition.compare_faces(known_fingerprints,face_encoding)
        if True in matches:
            fp_index=matches.index(True)
            personid=known_ids[fp_index]
            print(f"found person -> {personid}")
        else:
            personid=nextid
            print(f"->New face...ID: {personid}")
            known_fingerprints.append(face_encoding)
            known_ids.append(personid)
            nextid+=1
        person_folder=os.path.join(outfolder,f"Person_{personid}")
        os.makedirs(person_folder,exist_ok=True)
        shutil.copy2(fullpath,person_folder)
