import pickle
import os
class VectorDB:
    def __init__(self,db_file='face_cache.pkl'):
        self.db_file=db_file
        self.data=self.load_data()
    def load_data(self):
        if not os.path.exists(self.db_file):
            return {'processed_files':{},'known_people':[]}
        try:
            with open(self.db_file,'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading DB:{e}")
            return {'processed_files':{},'known_people':[]}
    def save_data(self):
        with open(self.db_file,'wb') as f:
            pickle.dump(self.data,f)
        print("DB saved to disk")
    def get_file_embeddings(self, filename):
        return self.data['processed_files'].get(filename)

    def add_file_embeddings(self, filename, embeddings):
        self.data['processed_files'][filename] = embeddings
    def get_known_people(self):
        return self.data['known_people']

    def update_known_people(self, people_list):
        self.data['known_people'] = people_list