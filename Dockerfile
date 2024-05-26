# Menggunakan base image Python
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Install libgl1-mesa-glx dan paket-paket pendukung lainnya
RUN apt-get update && apt-get install -y libgl1-mesa-glx && \
    apt-get install -y libglib2.0-0 libnss3 libx11-6 libgconf-2-4 libfontconfig1 && \
    # Tambahkan baris ini untuk instalasi Tesseract OCR
    apt-get install -y tesseract-ocr && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory di dalam kontainer
WORKDIR /app

# Menyalin dependencies ke dalam kontainer
COPY requirements_docker.txt /app/

# Menginstall dependencies
RUN pip install --no-cache-dir -r requirements_docker.txt

# Menyalin seluruh konten proyek ke dalam kontainer
COPY . /app/

# Menjalankan aplikasi dengan uvicorn di port 8100
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
