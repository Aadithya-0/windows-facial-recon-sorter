import os
import cv2
import numpy
import shutil
from engine import FaceEngine
def compute_similarity(embedding1,embedding2):
    similarity=numpy.dot(embedding1,embedding2)/(numpy.linalg.norm(embedding1)*numpy.linalg.norm(embedding2))
    return similarity
def register_faces(source_dir,output_dir,engine):
    known_faces=[]
    files=os.listdir(source_dir)
    c=0
    for filename in files:
        img_path=os.path.join(source_dir,filename)
        img=cv2.imread(img_path)
        faces=engine.process_image(img)
        if len(faces)==0:
            print(f"Skipping {filename} no face found")
            continue
        found_people_in_this_image = set()
        for i, face in enumerate(faces):
            current_embedding = face.embedding
            max_score=0.0
            best_name="unknown"
            for person in known_faces:
                known_vec=person['embedding']
                score=compute_similarity(current_embedding,known_vec)
                if score>max_score:
                    max_score=score
                    best_name=person['name']
            if max_score>0.5:
                final_name=best_name
                print(f"Match found: {filename} is {final_name}")
            else:
                c+=1
                final_name="person"+str(c)
                print(f"New face: {filename} is {final_name}")
                known_faces.append({
                    'name': final_name,
                    'embedding': current_embedding
                })
                print(f"New Face Discovered in {filename}: {final_name}")
            if final_name not in found_people_in_this_image:       
                person_folder = os.path.join(output_dir, final_name)
                if not os.path.exists(person_folder):
                    os.makedirs(person_folder)
                
                shutil.copy(img_path, os.path.join(person_folder, filename))
                
                found_people_in_this_image.add(final_name)
                print(f"-> Copied {filename} to {final_name}")
if __name__=='__main__':
    engine=FaceEngine(use_gpu=False)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_folder = os.path.join(base_dir, "testimage")
    output_folder = os.path.join(base_dir, "sorted_results")
    if not os.path.exists(source_folder):
        print(f"Error: Could not find folder: {source_folder}")
        exit()
    print(f"Processing images from: {source_folder}")
    register_faces(source_folder, output_folder, engine)
    # faces1=engine.process_image(img)
    # vector1=faces1[0].embedding
    # faces2=engine.process_image(img2)
    # vector2=faces2[0].embedding
    # similarity=compute_similarity(vector1,vector2)
    #print("Similarity score between the two faces is :", similarity)