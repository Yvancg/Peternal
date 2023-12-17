// Fading effect of the alert messages
$(document).ready(function() {
    setTimeout(function() {
        $(".alert").fadeOut('slow');
    }, 5000); // 5 seconds
});

// Tooltip function from Bootstrap 
$(document).ready(function(){
    $('[data-bs-toggle="tooltip"]').tooltip({
        trigger: 'focus',
        html: true
    });
});

// Password strength progress bar
function updateStrengthBar(passwordFieldId) {
    const password = document.getElementById(passwordFieldId).value;
    let strength = 0;

    if (password.match(/[a-z]+/)) strength += 20;
    if (password.match(/[A-Z]+/)) strength += 20;
    if (password.match(/[0-9]+/)) strength += 20;
    if (password.match(/[\W]+/)) strength += 20;
    if (password.length > 7) strength += 20;

    const strengthBar = document.getElementById('password-strength-bar');
    strengthBar.style.width = strength + '%';
    strengthBar.setAttribute('aria-valuenow', strength);

    if (strength < 40) {
        strengthBar.className = 'progress-bar bg-red';
    } else if (strength < 80) {
        strengthBar.className = 'progress-bar bg-orange';
    } else if (strength < 100) {
        strengthBar.className = 'progress-bar bg-yellow';
    } else {
        strengthBar.className = 'progress-bar bg-green';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('password');
    const newPasswordField = document.getElementById('new_password');

    if (passwordField) {
        passwordField.addEventListener('input', function() {
            updateStrengthBar('password');
        });
    }

    if (newPasswordField) {
        newPasswordField.addEventListener('input', function() {
            updateStrengthBar('new_password');
        });
    }
});

// Spinner visibility
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('register-form');
    const spinner = document.getElementById('spinner');
    const flashMessage = document.querySelector('.alert');

    form.addEventListener('submit', function () {
        // Show spinner on form submit
        spinner.classList.remove('visually-hidden');
    });
        // Hide spinner if flash message is present
        if (flashMessage) {
            spinner.classList.add('visually-hidden');
        }
});

// Select2 extended features https://select2.org/
$(document).ready(function() {
    $('#breed').select2({
        placeholder: "Choose...",
        allowClear: true,
    });
});
