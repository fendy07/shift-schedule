from datetime import datetime
from flask import Flask, render_template, request, jsonify
from optimization import optimized_schedule
import hashlib
import json
import os

SAVE_PATH = "saved_schedules"  # Folder untuk menyimpan jadwal
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

app = Flask(__name__)


def file_content_hash(filepath):
    """Mengembalikan hash berdasarkan isi file."""
    with open(filepath, 'r') as f:
        file_content = f.read()
        parsed_content = json.loads(file_content)
        return hashlib.md5(json.dumps(parsed_content, sort_keys=True).encode()).hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    schedule = request.json

    # Periksa apakah jadwal kosong?
    if not schedule:
        return jsonify(success=False, message="Jadwal kosong. Tidak disimpan!")

    # Hitung hash jadwal yang diterima
    current_schedule_hash = hashlib.md5(json.dumps(schedule, sort_keys=True).encode()).hexdigest()

    # Periksa apakah jadwal sudah ada di direktori?
    for filename in os.listdir(SAVE_PATH):
        filepath = os.path.join(SAVE_PATH, filename)
        if file_content_hash(filepath) == current_schedule_hash:
            return jsonify(success=False, message="Jadwal sudah ada!")

    # Jika tidak ada yang cocok, simpan file
    filename = "schedule_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + ".json"
    filepath = os.path.join(SAVE_PATH, filename)

    with open(filepath, 'w') as f:
        json.dump(schedule, f, indent=4)

    return jsonify(success=True, message="Program berhasil disimpan!")


@app.route('/load_file_schedule', methods=['POST'])
def load_file_schedule():
    try:
        data = request.json
        filename = data.get('filename')
        filepath = os.path.join(SAVE_PATH, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                schedule_data = json.load(f)
            return jsonify({'success': True, 'data': schedule_data})
        
        else:
            return jsonify({'success': False, 'message': 'File Tidak Ditemukan!'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


    #filepath = os.path.join(SAVE_PATH, filename)
    #if not os.path.exists(filepath):
    #    return jsonify(success=False, message="File Tidak Ditemukan!")

    #with open(filepath, 'r') as f:
    #    schedule = json.load(f)

    #return jsonify(success=True, data=schedule)


@app.route('/list_schedules', methods=['GET'])
def list_schedules():
    files = os.listdir(SAVE_PATH)
    files.sort(reverse=True)  # Urutkan file dari yang terbaru ke yang paling lama
    return jsonify(files)


@app.route('/optimize', methods=['POST'])
def optimize():
    #if request.is_json:
    #    data = request.get_json()
    #    names = data['names']
    #    optimized_schedule = optimize_schedule(names, generations=200)
    #    # Processing data
    #    return jsonify({'optimized_schedule': optimized_schedule, 'message': 'Optimization Successful!'}), 200
    #else:
    #    return 'Unsupported Media Type', 415
    data = request.json
    names = data['names']
    muslim = data.get('muslims')

    optimize_schedule = optimized_schedule(names, muslim, generations=200)
    return jsonify(optimize_schedule)


if __name__ == '__main__':
    app.run(debug=True)