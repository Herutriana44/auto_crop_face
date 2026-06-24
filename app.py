import os
import uuid
import shutil
import logging
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, jsonify, send_file, send_from_directory
)

from face_cropper import FaceCropper
from utils import detect_gpu, get_gpu_info, allowed_file, get_file_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'outputs')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

gpu_info = get_gpu_info()
face_cropper = FaceCropper()

logger.info(f"GPU: {gpu_info['type']} - {gpu_info['name']}")


def cleanup_old_files(folder, minutes=60):
    """Hapus file yang lebih lama dari N menit"""
    cutoff = datetime.now() - timedelta(minutes=minutes)
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
        elif os.path.isdir(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                shutil.rmtree(path)


@app.route('/')
def index():
    return render_template('index.html', gpu_info=gpu_info)


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'gpu': gpu_info
    })


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diupload'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nama file kosong'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Format file tidak didukung. Gunakan JPG/PNG/WebP untuk gambar, MP4/AVI/MOV/MKV/WebM untuk video'
        }), 400

    # Cleanup old files
    cleanup_old_files(app.config['UPLOAD_FOLDER'])
    cleanup_old_files(app.config['OUTPUT_FOLDER'])

    # Save uploaded file
    task_id = str(uuid.uuid4())[:8]
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_name = f"{task_id}.{ext}"
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    file.save(upload_path)

    # Create output subfolder
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], task_id)
    os.makedirs(output_dir, exist_ok=True)

    file_type = get_file_type(file.filename)

    try:
        if file_type == 'image':
            results = face_cropper.process_image(upload_path, output_dir)
        elif file_type == 'video':
            results = face_cropper.process_video(upload_path, output_dir)
        else:
            return jsonify({'error': 'Tipe file tidak dikenali'}), 400

        if not results:
            return jsonify({
                'task_id': task_id,
                'file_type': file_type,
                'faces_found': 0,
                'message': 'Tidak ada wajah terdeteksi dalam file',
                'results': []
            })

        # Create ZIP for download
        zip_name = f"faces_{task_id}.zip"
        face_cropper.create_zip(output_dir, zip_name)

        return jsonify({
            'task_id': task_id,
            'file_type': file_type,
            'faces_found': len(results),
            'results': results,
            'zip_url': f'/download/{task_id}/{zip_name}',
            'preview_urls': [f'/download/{task_id}/{r["filename"]}' for r in results[:20]]
        })

    except Exception as e:
        logger.error(f"Error processing: {e}")
        return jsonify({'error': f'Gagal memproses file: {str(e)}'}), 500


@app.route('/download/<task_id>/<filename>')
def download_file(task_id, filename):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], task_id)
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File tidak ditemukan'}), 404

    mimetype = 'application/zip' if filename.endswith('.zip') else 'image/jpeg'
    return send_file(filepath, mimetype=mimetype, as_attachment=False)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
