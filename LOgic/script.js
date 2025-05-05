let lessonTimes = [];

// Function to add a lesson time
function addLesson(lessonName, times) {
    lessonTimes.push({ lessonName: lessonName, times: times });
    console.log(`Lesson '${lessonName}' added with times ${times}`);
}

// Function to clear all lessons
function clearAllLessons() {
    lessonTimes = [];
    console.log("All lessons have been cleared.");
}

// Function to save schedule to local storage
function saveSchedule() {
    localStorage.setItem('lessonSchedule', JSON.stringify(lessonTimes));
    console.log("Schedule saved to local storage.");
}

// Function to load schedule from local storage
function loadSchedule() {
    const savedSchedule = localStorage.getItem('lessonSchedule');
    if (savedSchedule) {
        lessonTimes = JSON.parse(savedSchedule);
        console.log("Schedule loaded from local storage.", lessonTimes);
    } else {
        console.log("No saved schedule found.");
    }
}

// Function to check the current time against lesson times and ring the bell if they match
function checkAndRingBell() {
    setInterval(() => {
        const now = new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
        lessonTimes.forEach(lesson => {
            if (lesson.times.includes(now)) {
                console.log(`Time for lesson: ${lesson.lessonName}! Ringing bell...`);
                const bellSound = new Audio('bell_sound.mp3');
                bellSound.play();
            }
        });
    }, 30000); // Check every 30 seconds
}

// Function to load bell sound file
function loadBellSound(filePath) {
    console.log(`Bell sound loaded: ${filePath}`);
}

// Start checking and ringing the bell
checkAndRingBell();

// Example actions
addLesson("Math", ["14:30", "15:00"]);
addLesson("Science", ["16:00"]);
saveSchedule();
loadSchedule();
