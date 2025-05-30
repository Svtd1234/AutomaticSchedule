<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lesson Scheduler</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(to bottom, #2c3e50, #4ca1af);
            color: #eee;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
            padding: 30px;
            width: 100%;
            max-width: 900px;
        }
        .card-title {
            font-weight: 700;
            font-size: 2.5rem;
            color: #23bbf0;
            text-align: center;
        }
        .btn-custom {
            border: none;
            border-radius: 25px;
            padding: 12px 25px;
            color: #eee;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        .btn-secondary {
            background-color: #6c757d;
        }
        .btn-warning {
            background-color: #868e96;
        }
        .btn-success {
            background-color: #adb5bd;
        }
        .btn-info {
            background-color: #ced4da;
        }
        .btn-primary {
            background-color: #dee2e6;
        }
        .btn-danger {
            background-color: #e9ecef;
        }
        .btn-custom:hover {
            background-color: #f39c12;
            transform: scale(1.05);
        }
        .form-label {
            font-weight: bold;
        }
        input.form-control, select.form-select {
            background: #555;
            color: #eee;
            border: none;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        input.form-control:focus, select.form-select:focus {
            background: #666;
            box-shadow: 0 0 10px #f39c12;
        }
        .table {
            background: rgba(255, 255, 255, 0.1);
            color: #eee;
            border-radius: 10px;
            overflow: hidden;
        }
        .table thead {
            background-color: #444;
        }
        #timer {
            font-size: 1.8rem;
            font-weight: bold;
            color: #00ffcc;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 0 0 10px #00ffcc;
        }
        .action-cell {
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="card">

        <h2 class="card-title mb-4"><i class="fas fa-music"></i> Розклад Дзвінків</h2>
        <div class="mb-4 d-flex flex-wrap justify-content-between">
            <button id="addLessonBtn" class="btn btn-secondary btn-custom mb-3" style="background-color: #6c757d; border-color: #6c757d;"><i class="fas fa-plus"></i> Додати Урок</button>
            <button id="clearAllLessonsBtn" class="btn btn-warning btn-custom mb-3" style="background-color: #6c757d; border-color: #6c757d;"><i class="fas fa-trash-alt"></i> Очистити Все</button>
            <button id="saveScheduleBtn" class="btn btn-success btn-custom mb-3" style="background-color: #6c757d; border-color: #6c757d;"><i class="fas fa-save"></i> Зберегти таблицю</button>
            <button id="loadScheduleBtn" class="btn btn-info btn-custom mb-3" style="background-color: #6c757d; border-color: #6c757d;"><i class="fas fa-upload"></i> Завантажити нову таблицю</button>
        </div>
        <div class="mb-4">
            <label for="serverIPInput" class="form-label">Server IP:</label>
            <input type="text" id="serverIPInput" class="form-control" placeholder="Enter server IP address">
            <button id="setServerIPBtn" class="btn btn-primary btn-custom mt-3" style="background-color: #6c757d; border-color: #6c757d;">Set Server IP</button>
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th style="width: 10%;">УРОК</th>
                        <th>1 ПАРА</th>
                        <th>ПЕРЕРВА</th>
                        <th>2 ПАРА</th>
                        <th>ПЕРЕРВА</th>
                        <th> </th>
                    </tr>
                </thead>
                <tbody id="lessonTable"></tbody>
            </table>
        </div>
        <div class="mt-4">
            <button id="loadBellSoundBtn" class="btn btn-primary w-100 btn-custom mb-3" style="background-color: #6c757d; border-color: #6c757d;">Загрузити Дзвінок <i class="fas fa-bell"></i></button>
            <button id="ringBellBtn" class="btn btn-danger w-100 btn-custom mb-3" style="background-color: #ff0000; border-color: #ff0000;">Дзвінок <i class="fas fa-bell"></i></button>
        </div>
        <div id="timer"></div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            startRealTimeClock();
            loadScheduleFromLocalStorage();

            document.getElementById('addLessonBtn').addEventListener('click', addLessonRow);
            document.getElementById('clearAllLessonsBtn').addEventListener('click', clearAllLessons);
            document.getElementById('saveScheduleBtn').addEventListener('click', saveScheduleToLocalStorage);
            document.getElementById('loadScheduleBtn').addEventListener('click', loadScheduleFromLocalStorage);
            document.getElementById('loadBellSoundBtn').addEventListener('click', loadBellSound);
            document.getElementById('ringBellBtn').addEventListener('click', ringBell);
            document.getElementById('setServerIPBtn').addEventListener('click', setServerIP);

            setInterval(checkLessonTimes, 1000);
        });

        let serverIP = 'http://your-server-ip-address'; // Default server IP

        function setServerIP() {
            const serverIPInput = document.getElementById('serverIPInput').value;
            if (serverIPInput) {
                serverIP = serverIPInput;
                alert(`Server IP set to: ${serverIP}`);
            } else {
                alert('Please enter a valid server IP address.');
            }
        }

        function startRealTimeClock() {
            const timerElement = document.getElementById('timer');
            setInterval(() => {
                const now = new Date();
                timerElement.textContent = now.toLocaleTimeString('en-GB', { hour12: false });
            }, 1000);
        }

        function addLessonRow() {
            const table = document.getElementById('lessonTable');
            const newRow = table.insertRow();
            newRow.innerHTML = `
                <td><input type="text" class="form-control" placeholder="Enter lesson name"></td>
                <td><input type="time" class="form-control time-input"></td>
                <td><input type="time" class="form-control time-input"></td>
                <td><input type="time" class="form-control time-input"></td>
                <td><input type="time" class="form-control time-input"></td>
                <td class="action-cell"><button class="btn btn-danger" style="background-color: #dc3545; border-color: #dc3545;" onclick="deleteLessonRow(this)"><i class="fas fa-trash"></i></button></td>
            `;
        }

        function deleteLessonRow(button) {
            const row = button.closest('tr');
            row.remove();
        }

        function loadBellSound() {
            const link = document.createElement('input');
            link.type = 'file';
            link.accept = 'audio/*';
            link.onchange = (event) => {
                const file = event.target.files[0];
                if (file) {
                    bellSound = new Audio(URL.createObjectURL(file));
                    alert(`Loaded bell sound: ${file.name}`);
                }
            };
            link.click();
        }

        let bellSound;
        let rungTimes = new Set();

        function ringBell() {
            if (bellSound) {
                bellSound.play();
                notifyServer();
            } else {
                alert('Please load a bell sound first.');
            }
        }

        function clearAllLessons() {
            document.getElementById('lessonTable').innerHTML = '';
        }

        function saveScheduleToLocalStorage() {
            const table = document.getElementById('lessonTable');
            const schedule = Array.from(table.rows).map(row => {
                const cells = Array.from(row.cells).slice(0, 5);
                return cells.map(cell => cell.children[0].value);
            });
            localStorage.setItem('lessonSchedule', JSON.stringify(schedule));
            alert('Schedule saved to local storage.');
        }

        function loadScheduleFromLocalStorage() {
            const schedule = JSON.parse(localStorage.getItem('lessonSchedule'));
            if (schedule) {
                const table = document.getElementById('lessonTable');
                table.innerHTML = '';
                schedule.forEach(lesson => {
                    const newRow = table.insertRow();
                    newRow.innerHTML = `
                        <td><input type="text" class="form-control" value="${lesson[0]}" placeholder="Enter lesson name"></td>
                        <td><input type="time" class="form-control time-input" value="${lesson[1]}"></td>
                        <td><input type="time" class="form-control time-input" value="${lesson[2]}"></td>
                        <td><input type="time" class="form-control time-input" value="${lesson[3]}"></td>
                        <td><input type="time" class="form-control time-input" value="${lesson[4]}"></td>
                        <td class="action-cell"><button class="btn btn-danger" style="background-color: #dc3545; border-color: #dc3545;" onclick="deleteLessonRow(this)"><i class="fas fa-trash"></i></button></td>
                    `;
                });
            } else {
                alert('No schedule found in local storage.');
            }
        }

        function checkLessonTimes() {
            const now = new Date();
            const currentTime = now.toLocaleTimeString('en-GB', { hour12: false }).substring(0, 5);
            const table = document.getElementById('lessonTable');
            Array.from(table.rows).forEach(row => {
                const timeInputs = row.querySelectorAll('.time-input');
                timeInputs.forEach(input => {
                    if (input.value === currentTime && !rungTimes.has(currentTime)) {
                        ringBell();
                        rungTimes.add(currentTime);
                    }
                });
            });
        }

        function notifyServer() {
            fetch(`${serverIP}/ringBell`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ time: new Date().toLocaleTimeString('en-GB', { hour12: false }) })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Server notified:', data);
            })
            .catch(error => {
                console.error('Error notifying server:', error);
            });
        }
    </script>

<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>

</body>
</html>
