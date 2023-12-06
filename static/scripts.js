// Fading effect of the alert messages
$(document).ready(function() {
    setTimeout(function() {
        $(".alert").fadeOut('slow');
    }, 5000); // 5 seconds
});

// Tooltip function from Bootstrap 
$(document).ready(function(){
    $('[data-bs-toggle="tooltip"]').tooltip({
        trigger: 'focus'
    });
});

// Password strength progress bar
document.getElementById('password').addEventListener('input', function() {
    var password = this.value;
    var strength = 0;

    if (password.match(/[a-z]+/)) strength += 20;
    if (password.match(/[A-Z]+/)) strength += 20;
    if (password.match(/[0-9]+/)) strength += 20;
    if (password.match(/[\W]+/)) strength += 20;
    if (password.length > 7) strength += 20;

    var strengthBar = document.getElementById('password-strength-bar');
    strengthBar.style.width = strength + '%';

    if (strength < 40) {
        strengthBar.className = 'progress-bar bg-red';
    } else if (strength < 80) {
        strengthBar.className = 'progress-bar bg-orange';
    } else if (strength < 100) {
        strengthBar.className = 'progress-bar bg-yellow';
    } else {
        strengthBar.className = 'progress-bar bg-green';
    }
});
