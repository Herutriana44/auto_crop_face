# Auto Face Crop

Web application sederhana untuk auto-crop wajah dari foto dan video menggunakan face recognition dengan MediaPipe.

## Features

- ✅ Upload foto (JPG, PNG, WebP) atau video (MP4, AVI, MOV, MKV, WebM)
- ✅ Auto-detect wajah menggunakan MediaPipe Face Detection
- ✅ Crop wajah dengan padding 1.5x ukuran bounding box
- ✅ Support multiple faces dalam satu file
- ✅ Auto GPU detection (CUDA, ROCm, Metal)
- ✅ Download hasil sebagai ZIP file
- ✅ UI responsive dengan drag-and-drop upload

## Tech Stack

- **Backend**: Flask
- **Face Detection**: MediaPipe
- **Video Processing**: OpenCV
- **GPU Support**: PyTorch CUDA detection
- **Frontend**: Vanilla JS + CSS

## Installation

### Local Setup

```bash
# Clone repository
git clone https://github.com/USERNAME/auto_crop_face.git
cd auto_crop_face

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Akses aplikasi di `http://localhost:5000`

### Google Colab / Kaggle

Gunakan notebook yang tersedia di folder `notebook/colab_deploy.ipynb` untuk deployment di Google Colab atau Kaggle dengan port forwarding otomatis.

## Usage

1. Buka aplikasi di browser
2. Upload foto atau video dengan:
   - Drag & drop file ke area upload, atau
   - Klik area upload untuk memilih file
3. Klik "Upload & Proses"
4. Tunggu hingga proses selesai
5. Download hasil crop:
   - Klik gambar individual untuk melihat, atau
   - Klik "Download Semua (ZIP)" untuk download semua hasil

## Configuration

### File Size Limits

- **Images**: Maksimum 50MB
- **Videos**: Maksimum 200MB

### Video Processing

- Frame sampling: 1 FPS (default)
- Maximum frames: 300 frames per video
- Output: Individual JPG untuk setiap wajah yang terdeteksi

### Padding Factor

Default: **1.5x** ukuran bounding box face detection

Untuk mengubah, edit parameter di `face_cropper.py`:

```python
def crop_face_with_padding(self, image, face, padding_factor=1.5):
```

## GPU Support

Aplikasi otomatis mendeteksi GPU yang tersedia:

- **CUDA** (NVIDIA GPUs)
- **ROCm** (AMD GPUs)
- **Metal** (Apple Silicon)
- **CPU** (fallback)

Status GPU ditampilkan di header aplikasi.

## Project Structure

```
auto_crop_face/
├── app.py                 # Flask application
├── face_cropper.py        # Face detection & cropping logic
├── utils.py               # GPU detection utilities
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # UI styling
│   └── js/
│       └── main.js       # Frontend logic
├── templates/
│   └── index.html        # Main interface
├── uploads/              # Temporary upload storage
├── outputs/              # Cropped results storage
├── notebook/
│   └── colab_deploy.ipynb # Colab/Kaggle deployment
└── README.md
```

## API Endpoints

### `GET /`
Render upload interface

### `POST /upload`
Upload dan proses file

**Request:**
- `multipart/form-data` dengan field `file`

**Response:**
```json
{
  "task_id": "abc123",
  "file_type": "image",
  "faces_found": 3,
  "results": [
    {
      "filename": "image_face_0.jpg",
      "score": 0.987,
      "size": [256, 256]
    }
  ],
  "zip_url": "/download/abc123/faces_abc123.zip",
  "preview_urls": ["/download/abc123/image_face_0.jpg"]
}
```

### `GET /download/<task_id>/<filename>`
Download cropped image atau ZIP file

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "gpu": {
    "type": "cuda",
    "name": "Tesla T4",
    "memory_mb": 15360
  }
}
```

## Troubleshooting

### MediaPipe Installation Error

Jika mengalami error saat install MediaPipe:

```bash
pip install --upgrade pip
pip install mediapipe --no-cache-dir
```

### OpenCV Error

Untuk Termux atau environment terbatas:

```bash
pip install opencv-python-headless
```

### GPU Not Detected

Pastikan CUDA toolkit terinstall (untuk NVIDIA):

```bash
nvidia-smi  # Check GPU status
```

## License

MIT License

## Contributing

Pull requests are welcome! Untuk perubahan major, harap buka issue terlebih dahulu.

## Author

Created with Flask + MediaPipe
