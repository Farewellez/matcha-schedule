#!/bin/bash
# start_session.sh

echo "--- MatchaSchedule REMOTE TEST SESSION ---"
echo "Initializing Python environment..."

# Pastikan kamu berada di direktori proyek
cd "$(dirname "$0")"

# Aktifkan virtual environment
source env/bin/activate

# Jalankan program utama
python -m src.main
