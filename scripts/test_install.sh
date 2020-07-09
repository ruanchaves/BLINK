#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ..

MODEL_DIR=../../models/blink_faiss

mkdir -p $MODEL_DIR

pip install -r requirements.txt
chmod +x download_models.sh
./download_models.sh
python blink/build_faiss_index.py --output_path $MODEL_DIR/faiss_flat_index.pkl