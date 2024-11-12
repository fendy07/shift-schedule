import os
import json
import hashlib
from datetime import datetime
from optimization import optimized_schedule
from flask import Flask, render_template, request, jsonify

# Folder untuk menyimpan jadwal
SAVE_PATH = "saved_schedules"  
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

app = Flask(__name__)


def file_content_hash(filepath):
    """Mengembalikan hash berdasarkan isi file."""
    with open(filepath, 'r') as f:
        file_content = f.read()
        if not file_content.strip():
            return None
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
        file_hash = file_content_hash(filepath)
        if file_hash and file_hash == current_schedule_hash:
            return jsonify(success=False, message="Jadwal sudah ada!")

    # Jika tidak ada yang cocok, simpan file
    filename = "schedule_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + ".json"
    filepath = os.path.join(SAVE_PATH, filename)

    with open(filepath, 'w') as f:
        json.dump(schedule, f, indent=4)

    return jsonify(success=True, message="Program berhasil disimpan!")

# Load file Schedule ketika data sudah mendapatkan hasil dan ter-generate 
@app.route('/load_file_schedule', methods=['POST'])
def load_file_schedule():
    try:
        schedule = request.json
        filename = schedule.get('filename')
        filepath = os.path.join(SAVE_PATH, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                schedule_data = json.load(f)
            return jsonify({'success': True, 'data': schedule_data})
        
        else:
            return jsonify({'success': False, 'message': 'File Tidak Ditemukan!'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/list_schedules', methods=['GET'])
def list_schedules():
    files = os.listdir(SAVE_PATH)
    files.sort(reverse=True)  # Urutkan file dari yang terbaru ke yang paling lama
    return jsonify(files)

# Delete file schedule when was not valid
@app.route('/delete_schedule', methods=['DELETE'])
def delete_schedule():
    try:
        data = request.json
        filename = data.get('filename')
        filepath = os.path.join(SAVE_PATH, filename)

        # Periksa jika file sudah ada
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Program Berhasil Dihapus!'})
        else:
            return jsonify({'success': False, 'message': 'File Tidak Ditemukan!'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update_event_date', methods=['POST'])
def update_event_date():
    try:
        data = request.json
        event_id = data.get('eventId')
        new_date = data.get('newDate')

        # Load the existing schedule
        filename = "schedule_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + ".json"
        filepath = os.path.join(SAVE_PATH, filename)
        if not os.path.exists(filepath):
            return jsonify({'Success': False, 'message': 'Schedule file not found!'}), 404
        
        with open(filepath, 'r') as file:
            schedule = json.load(file)

        # Update the event date
        event_found = False
        for event in schedule['events']:
            if event['id'] == event_id:
                event['date'] = new_date
                event_found = True
                break
        
        if not event_found:
            return jsonify({'success': False, 'message': 'Event not found!'}), 404
        
        # Simpan untuk jadwal yang diupdate
        with open(filepath, 'w') as file:
            json.dump(schedule, file, indent=4)

        return jsonify({'success': True, 'message': 'Event date updated successfully!'})

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    names = data['names']
    muslim = data.get('muslims')

    optimize_schedule = optimized_schedule(names, muslim, generations=200)
    return jsonify(optimize_schedule)


if __name__ == '__main__':
    app.run(debug=True)