var currentSchedule = [];

function listFiles() {
    $.get('/list_schedules', function(files) {
        var fileList = $('#file-list');
        fileList.empty();
        files.forEach(function(file) {
            fileList.append('<option value="' + file + '">' + file + '</option>');
        });
    });
}

var calendar;

document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            center: 'prev,next today',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,list'
        },
        editable: true,
        dayMaxEvents: true,
        eventDrop: function(info) {
            handleEventDrop(info);
        }
    });

    calendar.render();
    listFiles();
});

function handleEventDrop(info) {
    // Get the new date of the event
    var newDate = info.event.start;
    // Update the event data 
    $.ajax({
        url: '/update_event_date',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            eventId: info.event.id,
            newDate: newDate
        }),
        success: function(response) {
            if (response.success) {
                showNotification('success', 'Shift date updated successfully!');
            } else {
                showNotification('error', 'Failed to update to shift date.');
                info.revert();
            }
        },
        error: function() {
            showNotification('error', 'An error occurred while updating the shift.');
            info.revert(); 
        }
    });
}

function optimizeCalendar() {
    $('#optimizing').show();
    $('#btn-optimize').attr('disabled', true);

    var names = [];
    $('.worker-name').each(function() {
        names.push($(this).val());
    });

    $.ajax({
        url: '/optimize',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ names: names }),
        success: function(data) {
            updateCalendar(data);
            $('#optimizing').addClass('d-none');
            $('#btn-optimize').attr('disabled', false);
        }
    });

}

function showNotification(type, message) {
    let swalType;
    
    if (type === 'success') {
        swalType = 'success'; // Notifikasi sukses
    } else if (type === 'error') {
        swalType = 'error'; // Notifikasi error
    } else if (type === 'warning') {
        swalType = 'warning'; // Notifikasi warning
    } else {
        swalType = 'info';
    }

    Swal.fire({
        icon: swalType,
        title: message,
        showConfirmButton: false,
        timer: 2000 // Notifikasi akan hilang setelah 5 detik
    });
}

function loadSchedule() {
    var selectedFile = $('#file-list').val();
    if (!selectedFile) {
        showNotification('warning', 'Silahkan Pilih File Schedule!');
        return;
    }

    $.ajax({
        url: '/load_file_schedule',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({filename: selectedFile}),
        success: function(response) {
            if (response.success) {
                var data = response.data;
                updateCalendar(data);
                showNotification('success', 'Program Berhasil di Load');
            } else {
                showNotification('danger', response.message || 'Error! Terjadi Kesalahan');
            }
        }
    });
}

// Menyimpan jadwal 
function saveSchedule() {
    if (!currentSchedule || currentSchedule.length === 0) {
        showNotification('danger', 'Jadwal Kosong! Silahkan Buat Jadwal Terlebih Dahulu');
        return;
    }
    
    $.ajax({
        url: '/save_schedule',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(currentSchedule),
        success: function(data) {
            showNotification(data.success ? 'success' : 'danger', data.message);
        }
    });
}

function deleteSchedule() {
    var selectedFile = $('#file-list').val();
    if (!selectedFile) {
        showNotification('warning', 'Silahkan Pilih File Schedule Terlebih Dahulu!');
        return;
    }

    $.ajax({
        url: '/delete_schedule',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ filename: selectedFile }),
        success: function(response) {
            if (response.success) {
                showNotification('success', 'File Schedule Berhasil Dihapus!');
                listFiles(); // Refresh file list
            } else {
                showNotification('error', response.message || 'Gagal Menghapus File Schedule.');
            }
        },

        error: function() {
            showNotification('error', 'Terjadi Kesalahan Saat Menghapus!');
        }
    });

}

function addNameField() {
    var nameField = '<div class="input-group mb-2">' +
                        '<input type="text" class="worker-name form-control" placeholder="Masukan Nama Karyawan">' +
                        '<button class="btn btn-danger remove-name-btn" onclick="removeNameField(this)">X</button>' +
                    '</div>';
    $("#names-list").append(nameField);
}

function removeNameField(button) {
    $(button).closest(".input-group").remove();
}

function geneticAlgorithm(populationSize, generations, mutationRate) {
    // Inisialisasi populasi
    let population = [];
    for (let i = 0; i < populationSize; i++) {
        let individual = [];
        for (let j = 0; j < 7; j++) {
            individual.push(Math.floor(Math.random() * 6)); // shift
        }
        population.push(individual);
    }

    // Evaluasi fitness
    function evaluateFitness(individual) {
        let fitness = [];
        for (let i = 0; i < 7; i++) {
            if (individual[i] === 0) { // shift 1
                fitness += 10;
            } else if (individual[i] === 1) { // shift 2
                fitness += 8;
            } else if (individual[i] === 2) { // shift 3
                fitness += 6;
            } else if (individual[i] === 3) { // shift 4
                fitness += 4;
            } else if (individual[i] === 4) { // shift 5
                fitness += 2;
            } else if (individual[i] === 5) { // Libur
                fitness -= 10;
            }
        }
        return fitness;
    }

    // Seleksi
    function selection(population) {
        let selected = [];
        for (let i = 0; i < populationSize; i++) {
            let randomIndex = Math.floor(Math.random() * populationSize);
            selected.push(population[randomIndex]);
        }
        return selected;
    }

    // Crossover
    function Crossover(parent1, parent2) {
        let child = [];
        for (let i = 0; i < 7; i++) {
            if (Math.random() < 0.05) {
                child.push(parent1[i]);
            } else {
                child.push(parent2[i]);
            }
        }
        return child;
    }

    function mutation(individual) {
        for (let i = 0; i < 7; i++) {
            if (Math.random() < mutationRate) {
                individual[i] = Math.floor(Math.random() * 6); // 6 shift
            }
        }
        return individual;
    }

    // Evolusi
    for (let i = 0; i < generations; i++) {
        let selected = selection(population);
        let offspring = [];
        for (let j = 0; j < populationSize; j++) {
            let parent1 = selected[j];
            let parent2 = selected[(j + 1) % populationSize];
            let child = Crossover(parent1, parent2);
            child = mutation(child);
            offspring.push(child);
        }
        population = offspring;
    }

    // Evaluasi Fitness terakhir
    let bestIndividual = population[0];
    let bestFitness = evaluateFitness(bestIndividual);
    for (let i = 1; i < populationSize; i++) {
        let individual = population[i];
        let fitness = evaluateFitness(individual);
        if (fitness > bestFitness) {
            bestIndividual = individual;
            bestFitness = fitness;
        }
    }

    return bestIndividual;
}

// Optimize
function optimize() {
    let populationSize = 100;
    let generations = 200;
    let mutationRate = 0.2;
    let bestIndividual = geneticAlgorithm(populationSize, generations, mutationRate);
    $('#optimizing').show();
    $('#btn-optimize').attr('disabled', true);

    var names = [];
    $('.worker-name').each(function() {
        names.push($(this).val());
    });

    $.ajax({
        url: '/optimize',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ names: names }),
        success: function(data) {
            updateCalendar(data);
            $('#optimizing').hide();
            $('#btn-optimize').attr('disabled', false);
        }
    });
}

function updateCalendar(data) {
    let events = transformToEvents(data);
    currentSchedule = data; // Simpan Jadwal
    calendar.removeAllEventSources();
    calendar.addEventSource(events);
    generateMetrics(data );
    generateMonthlyMetrics(data);
}

var currentYear = new Date().getFullYear();

function getDateFromWeek(weekNumber, year) {
    // Pertama, cari tanggal awal dari minggu pertama untuk bulan yang diberikan
    const janFirst = new Date(year, 0, 1);
    const janFirstDayOfWeek = janFirst.getDay();
    const daysToNextMonday = (janFirstDayOfWeek === 0 ? 1 : 8 - janFirstDayOfWeek);
    
    const firstMondayOfYear = new Date(janFirst.setDate(daysToNextMonday));
    
    // Hitung tanggal berdasarkan tiap minggunya
    const resultDate = new Date(firstMondayOfYear);
    resultDate.setDate(firstMondayOfYear.getDate() + (weekNumber - 1) * 7);
    
    return resultDate;
}
// Overlapping for shifts schedule when generated
function shiftsOverlap(shift1, shift2, shift3, shift4, shift5) {
    return (shift1.start < shift2.end && shift1.end > shift2.start) ||
           (shift2.start < shift1.end && shift2.end > shift1.start) || 
           (shift3.start < shift4.end && shift3.end > shift4.start) ||
           (shift5.start < shift4.end && shift5.end > shift4.start); 
}

function adjustOverlappingShifts(shift) {
    shift.sort((shift1, shift2, shift3, shift4, shift5) => shift1.start - shift2.start - shift3.start - shift4.start - shift5.start);
    for (let i = 0; i < shift.length - 1; i++) {
        if (shiftsOverlap(shift[i], shift[i + 1])) {
            // adjust waktu terakhir untuk shift sekarang yang diberikan dalam memulai waktu
            shift[i].end = new Date(Math.min(shift[i].end, shift[i + 1].start));
        }
    }
}

function transformToEvents(data) {
    return data.map(function(week, index) {
        var startDate = getDateFromWeek(index, currentYear);
        // Tambahkan 1 hari untuk perbaikan shift
        startDate.setDate(startDate.getDate() + 1); 

        var endDate = new Date(startDate);
        // Tambahkan 6 hari untuk mencapai hari Minggu
        endDate.setDate(startDate.getDate() + 6); 
        
        // Shift 1 dari jam 10:00 AM - 18:00 PM
        var shift1Start = new Date(startDate);
        shift1Start.setHours(10, 0);
        
        var shift1End = new Date(startDate);
        shift1End.setDate(shift1End.getDate() + 1);
        shift1End.setHours(18, 0)

        // Shift 2 dari Jam 14:00 PM - 22:00 PM
        var shift2Start = new Date(startDate);
        shift2Start.setHours(14, 0);
        
        var shift2End = new Date(shift2Start);
        shift2End.setDate(shift2End.getDate() + 1);
        shift2End.setHours(22, 0);

        // Shift 3 dari jam 12:00 PM - 20:00 PM
        var shift3Start = new Date(startDate);
        shift3Start.setHours(12, 0);
        
        var shift3End = new Date(shift3Start);
        shift3End.setDate(shift3End.getDate() + 1);
        shift3End.setHours(20, 0);

        // Shift 4 dari jam 10:00 AM - 20:00 PM 
        var shift4Start = new Date(startDate);
        shift4Start.setHours(10, 0);

        var shift4End = new Date(shift4Start);
        shift4End.setDate(shift4End.getDate() + 2);
        shift4End.setHours(20, 0);

        // Shift 5 dari jam 10:00 AM - 19:00 PM
        var shift5Start = new Date(startDate);
        shift5Start.setHours(10, 0);

        var shift5End = new Date(shift5Start);
        shift5End.setDate(shift5End.getDate() + 1);
        shift5End.setHours(19, 0);

        // Shift 6 Libur (Off Day)
        var offDayStart = new Date(startDate);
        offDayStart.setHours(0, 0);

        var offDayEnd = new Date(offDayStart);  
        offDayEnd.setHours(23, 59);

        // Menentukan off day berdasarkan hari weekday
        if (startDate.getDay() >= 1 && startDate.getDay() <= 4) { // Senin - Kamis
            offDayStart.setDate(offDayStart.getDate()); // Tetap dihari yang sama
            offDayEnd.setDate(offDayEnd.getDate()); // Selesai pada waktu akhir 
        } else {
            offDayStart.setDate(offDayStart.getDate() - 1); // set ke hari Jum'at
            offDayEnd.setDate(offDayEnd.getDate()); // Selesai pada akhir hari
        }
        offDayStart.setHours(0, 0); // Mulai dari tengah malam
        offDayEnd.setHours(23, 59); // selesai waktu akhir jam 11:59 PM

        return [
            { title: 'Shift 1: ' + week[0], start: shift1Start, end: shift1End, color: '#FF8C00' }, 
            { title: 'Shift 2: ' + week[1], start: shift2Start, end: shift2End, color: '#FCD703' }, 
            { title: 'Shift 3: ' + week[2], start: shift3Start, end: shift3End, color: '#338A11' },
            { title: 'Shift 4: ' + week[3], start: shift4Start, end: shift4End, color: '#5050DB' },
            { title: 'Shift 5: ' + week[4], start: shift5Start, end: shift5End, color: '#0E1EC9' },
            { title: 'Libur: ' + week[5], start: offDayStart, end: offDayEnd, color: '#FF0000' }
        ];
    }).flat();

    // adjust overlapping shifts
    adjustOverlappingShifts(shift);

    return shift;
}

// Screenshot for calendar event shift when get result
function takeScreenshot() {
    const calendarElement = document.getElementById('calendar');
    html2canvas(calendarElement).then(canvas => {
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        link.download = 'calendar-screenshot.png';
        link.click();
    });
}

function generateMetrics(data) {
    const counts = {};
    
    data.forEach(function(week) {
        counts[week[0]] = counts[week[0]] || { shift1: 0, shift2: 0, shift3: 0, shift4: 0, shift5: 0, shift6: 0, offDay: 0};
        counts[week[0]].shift1 += 1;
        
        counts[week[1]] = counts[week[1]] || { shift1: 0, shift2: 0, shift3: 0, shift4: 0, shift5: 0, offDay: 0};
        counts[week[1]].shift2 += 1;
        
        counts[week[2]] = counts[week[2]] || { shift1: 0, shift2: 0, shift3: 0, shift4: 0, shift5: 0, offDay: 0};
        counts[week[2]].shift3 += 1;

        counts[week[3]] = counts[week[3]] || { shift1: 0, shift2: 0, shift3: 0, shift4: 0, shift5: 0, offDay: 0};
        counts[week[3]].shift4 += 1;

        counts[week[4]] = counts[week[4]] || { shift1: 0, shift2: 0, shift3: 0, shift4: 0, shift5: 0, offDay: 0};
        counts[week[4]].shift5 += 1;

        counts[week[5]] = counts[week[5]] || { shift1: 0, shift2: 0, shift3: 0, shift4: 0, shift5: 0, offDay: 0};
        counts[week[5]].offDay += 1;
    });


    let tableHTML = '<h4>Metriks Tahunan</h4>';
    tableHTML += '<table class="table table-striped table-bordered">'; 
    tableHTML += '<thead><tr><th>Nama Karyawan</th><th>Shift 1</th><th>Shift 2</th><th>Shift 3</th><th>Shift 4</th><th>Shift 5</th><th>Libur</th></tr></thead><tbody>';

    for (const [name, shift] of Object.entries(counts)) {
        tableHTML += `<tr><td>${name}</td><td>${shift.shift1}</td><td>${shift.shift2}</td><td>${shift.shift3}</td><td>${shift.shift4}</td><td>${shift.shift5}</th><th>${shift.offDay}</th></tr>`;
    }

    tableHTML += '</tbody></table>';

    const metricsDiv = document.getElementById('metrics');
    metricsDiv.innerHTML = tableHTML;
}

function getMonthFromDate(date) {
    return date.getMonth();
}

function generateMonthlyMetrics(data) {
    const counts = {};

    console.log('generateMonthlyMetrics');
    console.log(data);
    
    data.forEach((week, weekIndex) => {
        const date = getDateFromWeek(weekIndex, currentYear);
        const month = date.getMonth();
        
        if (!counts[month]) {
            counts[month] = {};
        }

        ["shift1", "shift2", "shift3", "shift4", "shift5", "offDay"].forEach((shiftType, index) => {
            const name = week[index];
            if (!counts[month][name]) {
                counts[month][name] = { 'shift1': 0, 'shift2': 0, 'shift3': 0, 'shift4': 0, 'shift5': 0, 'offDay': 0 };
            }
            counts[month][name][shiftType]++;
        });
    });
    console.log(counts);
    
    let tableHTML = '<h4>Metriks Bulanan</h4>';
    tableHTML += '<table class="table table-striped table-bordered">';
    tableHTML += '<thead><tr><th>Bulan</th><th>Nama Karyawan</th><th>Shift 1</th><th>Shift 2</th><th>Shift 3</th><th>Shift 4</th><th>Shift 5</th><th>Libur</th></tr></thead><tbody>';

    for (const [month, names] of Object.entries(counts)){            
        for (const [name, shift] of Object.entries(names)) {
            tableHTML += `<tr><td>${new Date(currentYear, month, 1).toLocaleString('id-ID', { month: 'long' })}</td><td>${name}</td><td>${shift.shift1}</td><td>${shift.shift2}</td><td>${shift.shift3}</td><td>${shift.shift4}<td>${shift.shift5}</td><td>${shift.offDay}</td></tr>`;
}
}

tableHTML += '</tbody></table>';

const metricsDiv = document.getElementById('monthlyMetrics');
metricsDiv.innerHTML = tableHTML;
}