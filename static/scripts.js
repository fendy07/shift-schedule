// Form untuk melakukan optimasi jadwal
document.getElementById('optimizeForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const names = document.getElementById('names').value.split(',').map(name => name.trim());
    const muslims = document.getElementById('muslims').value.split(',').map(name => name.trim());
    const generations = parseInt(document.getElementById('generations').value);

    const requestData = { names, muslims, generations };

    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        const result = await response.json();
        
        // Tampilkan hasil optimasi
        const optimizationResult = document.getElementById('optimizationResult');
        if (result.success) {
            optimizationResult.innerHTML = `<strong>Optimization Result:</strong><br>${JSON.stringify(result.data, null, 2)}`;
        } else {
            optimizationResult.innerHTML = `<strong>Error:</strong> ${result.message}`;
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

// Fungsi untuk memuat jadwal yang tersimpan
async function loadSchedules() {
    try {
        const response = await fetch('/list_schedules');
        const schedules = await response.json();

        const savedSchedules = document.getElementById('savedSchedules');
        savedSchedules.innerHTML = '';

        schedules.forEach(filename => {
            const listItem = document.createElement('li');
            listItem.textContent = filename;

            // Tambahkan tombol load
            const loadButton = document.createElement('button');
            loadButton.textContent = 'Load';
            loadButton.onclick = async () => loadSchedule(filename);

            listItem.appendChild(loadButton);
            savedSchedules.appendChild(listItem);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

// Fungsi untuk memuat jadwal tertentu
async function loadSchedule(filename) {
    try {
        const response = await fetch('/load_file_schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        const result = await response.json();

        if (result.success) {
            alert(`Loaded Schedule: ${JSON.stringify(result.data, null, 2)}`);
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
