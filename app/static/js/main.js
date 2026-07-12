// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Seat selection logic
function initSeatSelection(scheduleId, fare) {
    const seats = document.querySelectorAll('.seat.available');
    const selectedDisplay = document.getElementById('selectedSeat');
    const fareDisplay = document.getElementById('totalFare');
    const seatInput = document.getElementById('selectedSeatInput');
    let selectedSeat = null;

    seats.forEach(function (seat) {
        seat.addEventListener('click', function () {
            if (selectedSeat) {
                selectedSeat.classList.remove('selected');
                selectedSeat.classList.add('available');
            }
            seat.classList.remove('available');
            seat.classList.add('selected');
            selectedSeat = seat;
            if (selectedDisplay) selectedDisplay.textContent = seat.dataset.seat;
            if (fareDisplay) fareDisplay.textContent = 'Tk ' + fare;
            if (seatInput) seatInput.value = seat.dataset.seat;
        });
    });
}
