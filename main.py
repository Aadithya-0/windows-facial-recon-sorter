from fileinput import filename
import os
import cv2
import numpy
import shutil
from engine import FaceEngine
from db import VectorDB
def compute_similarity(embedding1,embedding2):
    similarity=numpy.dot(embedding1,embedding2)/(numpy.linalg.norm(embedding1)*numpy.linalg.norm(embedding2))
    return similarity
def register_faces(source_dir,output_dir,engine):
    db=VectorDB()
    known_faces=db.get_known_people()
    # NEW WAY (Recursive / Subfolders):
    image_files = []
    print(f"Scanning '{source_dir}' for images...")

    # os.walk automatically dives into every subfolder
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                # We save the FULL path so we can find it later
                full_path = os.path.join(root, file)
                image_files.append(full_path)

    # Sort by file size (High Quality First)
    image_files.sort(key=lambda x: os.path.getsize(x), reverse=True)

    print(f"Found {len(image_files)} images across all subfolders.")
    c=0
    for p in known_faces:
        try:
            num=int(p['name'].replace("person",""))
            if num>c:c=num
        except:
            pass
    print(f"resuming from person count : {c}")
    for img_path in image_files:  # iterating directly over full paths now
        filename = os.path.basename(img_path)  # Extract basename for the DB key
        cached_embeddings = db.get_file_embeddings(filename)
        face_embeddings = []
        if cached_embeddings is not None:
            # HIT! We know this file. Use the cache.
            face_embeddings = cached_embeddings
        else:
            # MISS! We need to process it.
            img = cv2.imread(img_path)
            if img is None: continue
            faces = engine.process_image(img)
            face_embeddings = [face.embedding for face in faces]
            db.add_file_embeddings(filename, face_embeddings)
        found_people_in_this_image = set()
        for i, face in enumerate(face_embeddings):
            current_embedding = face
            global_max_score=0.0
            best_name="unknown"
            for person in known_faces:
                known_vec=person['embeddings']
                person_score=[compute_similarity(current_embedding,past_emb) for past_emb in person['embeddings']]
                if not person_score:
                    continue
                best_score_for_this_person=max(person_score)
                if best_score_for_this_person>global_max_score:
                    global_max_score=best_score_for_this_person
                    best_name=person['name']
            if global_max_score>0.45:
                final_name=best_name
                print(f"Match: {filename} face {i} is {final_name} (Score: {global_max_score:.2f})")
                for p in known_faces:
                    if p['name']==final_name:
                        p['embeddings'].append(current_embedding)
                        break
            else:
                if global_max_score>0.3:
                    print(f"No Match: {filename} face {i} closest was {best_name} but score {global_max_score:.2f} was too low.")
                c+=1
                final_name="person"+str(c)
                print(f"New face: {filename} is {final_name}")
                known_faces.append({
                    'name': final_name,
                    'embeddings': [current_embedding]
                })
                print(f"New Face Discovered in {filename}: {final_name}")
            if final_name not in found_people_in_this_image:       
                person_folder = os.path.join(output_dir, final_name)
                if not os.path.exists(person_folder):
                    os.makedirs(person_folder)
                
                shutil.copy(img_path, os.path.join(person_folder, filename))
                
                found_people_in_this_image.add(final_name)
                print(f"-> Copied {filename} to {final_name}")
    db.update_known_people(known_faces)
    db.save_data()
    print("DB saved")
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