import os
import cv2
import numpy as np
import shutil
from engine import FaceEngine
from db import VectorDB


def _batch_best_similarity(current_embedding, known_faces):
    """Vectorised cosine similarity against all known people.
    Returns (best_name, best_score)."""
    best_name = "unknown"
    best_score = 0.0
    cur = np.asarray(current_embedding, dtype=np.float32)
    cur_norm = np.linalg.norm(cur)
    if cur_norm == 0:
        return best_name, best_score
    for person in known_faces:
        embs = person['embeddings']
        if not embs:
            continue
        mat = np.array(embs, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1)
        norms[norms == 0] = 1e-10
        scores = mat @ cur / (norms * cur_norm)
        top = float(np.max(scores))
        if top > best_score:
            best_score = top
            best_name = person['name']
    return best_name, best_score


def _already_sorted(output_dir, filename):
    """Check if this filename is already present in any person folder."""
    if not os.path.isdir(output_dir):
        return False
    for person_dir in os.listdir(output_dir):
        if os.path.isfile(os.path.join(output_dir, person_dir, filename)):
            return True
    return False


def register_faces(source_dir, output_dir, engine, progress_callback=None):
    db = VectorDB()
    known_faces = db.get_known_people()

    # Collect all image files recursively
    image_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                image_files.append(os.path.join(root, file))

    # Sort by file size (high-quality first)
    image_files.sort(key=lambda x: os.path.getsize(x), reverse=True)

    total_files = len(image_files)
    print(f"Found {total_files} images across all subfolders.")

    # Build a set of already-sorted filenames for O(1) lookup
    sorted_set = set()
    if os.path.isdir(output_dir):
        for d in os.listdir(output_dir):
            dp = os.path.join(output_dir, d)
            if os.path.isdir(dp):
                for f in os.listdir(dp):
                    sorted_set.add(f)

    # Resume person counter
    c = 0
    for p in known_faces:
        try:
            num = int(p['name'].replace("person", ""))
            if num > c:
                c = num
        except:
            pass
    print(f"Resuming from person count: {c}")

    engine_loaded = False  # defer heavy model load until needed

    for index, img_path in enumerate(image_files):
        filename = os.path.basename(img_path)

        # ── Fast path: already sorted ──
        if filename in sorted_set:
            if progress_callback and total_files > 0:
                progress_callback(index + 1, total_files, filename, True)
            continue

        # ── Get or compute embeddings ──
        cached_embeddings = db.get_file_embeddings(filename)
        if cached_embeddings is not None:
            face_embeddings = cached_embeddings
        else:
            # Need the model – lazy-load once
            if not engine_loaded:
                engine._ensure_loaded()  # no-op if already loaded
                engine_loaded = True
            img = cv2.imread(img_path)
            if img is None:
                if progress_callback and total_files > 0:
                    progress_callback(index + 1, total_files, filename, True)
                continue
            faces = engine.process_image(img)
            face_embeddings = [face.embedding for face in faces]
            db.add_file_embeddings(filename, face_embeddings)

        found_people_in_this_image = set()
        for i, current_embedding in enumerate(face_embeddings):
            best_name, best_score = _batch_best_similarity(current_embedding, known_faces)

            if best_score > 0.45:
                final_name = best_name
                for p in known_faces:
                    if p['name'] == final_name:
                        p['embeddings'].append(current_embedding)
                        break
            else:
                c += 1
                final_name = "person" + str(c)
                known_faces.append({'name': final_name, 'embeddings': [current_embedding]})

            if final_name not in found_people_in_this_image:
                person_folder = os.path.join(output_dir, final_name)
                os.makedirs(person_folder, exist_ok=True)
                dest = os.path.join(person_folder, filename)
                if not os.path.exists(dest):
                    shutil.copy(img_path, dest)
                sorted_set.add(filename)
                found_people_in_this_image.add(final_name)

        # Report progress
        if progress_callback and total_files > 0:
            progress_callback(index + 1, total_files, filename, False)

    db.update_known_people(known_faces)
    db.save_data()
    print("DB saved")


def process_folder(folder_path, progress_callback=None):
    """Entry point used by gui.py to process a folder of images."""
    engine = FaceEngine(use_gpu=False)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if os.path.isabs(folder_path):
        source_folder = folder_path
    else:
        source_folder = os.path.join(base_dir, folder_path)

    output_folder = os.path.join(base_dir, "sorted_results")

    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Error: Could not find folder: {source_folder}")

    print(f"Processing images from: {source_folder}")
    register_faces(source_folder, output_folder, engine, progress_callback)

    return output_folder


if __name__=='__main__':
    # Allow running this file directly for testing without affecting gui.py imports
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_source = os.path.join(base_dir, "testimage")
    process_folder(default_source)