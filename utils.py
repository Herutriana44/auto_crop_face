import os
import sys
import logging

logger = logging.getLogger(__name__)


def detect_gpu():
    """Deteksi GPU yang tersedia. Return: 'cuda', 'rocm', 'metal', atau 'cpu'"""
    gpu_type = 'cpu'

    # Cek CUDA via environment
    cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if cuda_visible and cuda_visible != '-1':
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi'], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                logger.info("GPU NVIDIA (CUDA) terdeteksi via nvidia-smi")
                return 'cuda'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Cek CUDA via PyTorch
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"GPU CUDA terdeteksi via PyTorch: {torch.cuda.get_device_name(0)}")
            return 'cuda'
    except ImportError:
        pass

    # Cek via OpenCV CUDA
    try:
        import cv2
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            logger.info("GPU CUDA terdeteksi via OpenCV")
            return 'cuda'
    except (ImportError, AttributeError):
        pass

    # Cek ROCm (AMD)
    rocm_path = '/opt/rocm'
    if os.path.exists(rocm_path):
        logger.info("AMD ROCm terdeteksi")
        return 'rocm'

    # Cek Metal (Apple)
    if sys.platform == 'darwin':
        try:
            import subprocess
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True, text=True, timeout=5
            )
            if 'Metal' in result.stdout:
                logger.info("Apple Metal terdeteksi")
                return 'metal'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    logger.info("Tidak ada GPU terdeteksi, menggunakan CPU")
    return gpu_type


def get_gpu_info():
    """Return informasi GPU untuk ditampilkan di UI"""
    gpu_type = detect_gpu()
    info = {'type': gpu_type, 'name': 'CPU', 'memory_mb': 0}

    if gpu_type == 'cuda':
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                info['name'] = parts[0].strip()
                info['memory_mb'] = int(parts[1].strip()) if len(parts) > 1 else 0
        except Exception:
            try:
                import torch
                info['name'] = torch.cuda.get_device_name(0)
                info['memory_mb'] = torch.cuda.get_device_properties(0).total_mem // (1024 * 1024)
            except Exception:
                pass
    elif gpu_type == 'rocm':
        info['name'] = 'AMD ROCm GPU'
    elif gpu_type == 'metal':
        info['name'] = 'Apple Metal GPU'

    return info


def allowed_file(filename, file_type='all'):
    """Validasi tipe file yang diizinkan"""
    image_exts = {'jpg', 'jpeg', 'png', 'webp', 'bmp'}
    video_exts = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()

    if file_type == 'image':
        return ext in image_exts
    elif file_type == 'video':
        return ext in video_exts
    else:
        return ext in (image_exts | video_exts)


def get_file_type(filename):
    """Tentukan tipe file: 'image', 'video', atau None"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in {'jpg', 'jpeg', 'png', 'webp', 'bmp'}:
        return 'image'
    elif ext in {'mp4', 'avi', 'mov', 'mkv', 'webm'}:
        return 'video'
    return None
