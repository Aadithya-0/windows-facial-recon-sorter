# Windows Facial Recognition Sorter

A Python-based facial recognition system that automatically organizes photos by identifying and grouping people using deep learning face embeddings. It features both a graphical user interface (GUI) and a command-line interface.

## Features

- **Graphical User Interface**: Browse and select any folder using the built-in GUI
- **Automatic Face Detection**: Uses InsightFace's state-of-the-art face detection model (buffalo_l)
- **Face Recognition**: Groups photos by person using facial embeddings and similarity matching
- **Smart Caching**: Caches face embeddings to avoid reprocessing images
- **Incremental Processing**: Can resume processing from where it left off
- **Quality-First Processing**: Processes larger images first to establish high-quality "anchor" faces
- **Multi-Face Support**: Handles multiple faces in a single image
- **Subfolder Scanning**: Recursively scans all subfolders in the selected directory

## Requirements

- Python 3.7+
- OpenCV (cv2)
- NumPy
- InsightFace
- ONNX Runtime (for InsightFace models)
- Flet (for the GUI)
- Tkinter (included with most Python installations)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Aadithya-0/windows-facial-recon-sorter.git
cd windows-facial-recon-sorter
```

2. Install the required dependencies:
```bash
pip install opencv-python numpy insightface onnxruntime flet
```

**Note**: For GPU acceleration, install `onnxruntime-gpu` instead of `onnxruntime`.

## Usage

### GUI Usage (Recommended)

1. Launch the GUI application:
```bash
python gui.py
```

2. Click **Browse** to select any folder containing your images, or paste the folder path directly into the text field
3. Click **Start Sorting** to begin processing
4. A progress bar will show the processing status
5. Once complete, the results are displayed as a grid of person thumbnails
   - Click any name label to edit it, then press **Enter** to save the new name
6. Find the sorted results in the `sorted_results` folder, organized by person

### Command-Line Usage

1. Create a `testimage` folder in the project directory
2. Place your images in the `testimage` folder (supports `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`)
3. Run the main script:
```bash
python main.py
```

4. Find the sorted results in the `sorted_results` folder, organized by person

### Clear Sorted Results

To clear the `sorted_results` folder and start fresh:
```bash
python clear.py
```

### Configuration

- **GPU Usage**: In `main.py`, you can enable GPU processing by changing:
  ```python
  engine = FaceEngine(use_gpu=True)  # Set to False for CPU-only
  ```

- **Similarity Threshold**: The matching threshold (default: 0.45) can be adjusted in `main.py`:
  ```python
  if global_max_score > 0.45:  # Adjust this value
  ```
  - Higher values (e.g., 0.6): Stricter matching, may create more person groups
  - Lower values (e.g., 0.3): Looser matching, may merge different people

## Project Structure

```
windows-facial-recon-sorter/
├── gui.py            # Graphical user interface (Flet-based)
├── main.py           # Core face recognition and sorting logic
├── engine.py         # FaceEngine class wrapping InsightFace
├── db.py            # VectorDB class for caching embeddings
├── clear.py         # Utility to clear sorted results
├── face_cache.pkl   # Cache file storing processed embeddings (auto-generated)
└── sorted_results/  # Output folder with sorted images (auto-generated)
```

## How It Works

1. **Image Processing**: The system reads images from the selected folder (and all subfolders)
2. **Face Detection**: InsightFace detects all faces in each image
3. **Embedding Extraction**: Each face is converted to a 512-dimensional embedding vector
4. **Similarity Matching**: New faces are compared against known faces using cosine similarity
5. **Grouping**: 
   - If similarity > 0.45: Face is matched to an existing person
   - If similarity ≤ 0.45: A new person is created
6. **Organization**: Images are copied to person-specific folders in `sorted_results`
7. **Caching**: All embeddings are cached in `face_cache.pkl` for faster subsequent runs

## Performance Tips

- **GPU Acceleration**: Enable GPU processing for faster face detection (requires compatible GPU and `onnxruntime-gpu`)
- **Image Quality**: Higher resolution images provide better face recognition accuracy
- **Batch Processing**: The system processes all images in one run; larger batches are more efficient

## Troubleshooting

### Missing testimage folder
If you see "Error: Could not find folder: testimage", create the folder:
```bash
mkdir testimage
```

### InsightFace model download
On first run, InsightFace will automatically download the required models (~500MB). Ensure you have a stable internet connection.

### Low accuracy
- Adjust the similarity threshold (lower for more lenient matching)
- Ensure input images are high quality
- Check that faces are clearly visible and well-lit

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Acknowledgments

- Built with [InsightFace](https://github.com/deepinsight/insightface) for state-of-the-art face recognition
- Uses OpenCV for image processing
