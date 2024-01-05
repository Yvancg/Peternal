// Global declaration of variables
let matchedPets = [];
let matchIndex = 0;

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
    const registerButton = document.getElementById('registerButton');
    const flashMessage = document.querySelector('.alert');

    // Debugging - log elements to console
    console.log({ form, registerButton, flashMessage });

    if (form && registerButton) {
        form.addEventListener('submit', function () {
            // Change button to spinner on submit
            registerButton.innerHTML = `<span class="spinner-border m-1" role="status" aria-hidden="true"></span> In progress...`;
            registerButton.disabled = true;
        });
    }
});

// Select2 extended features https://select2.org/
$(document).ready(function() {
    $('#breed').select2({
        placeholder: "Choose...",
        allowClear: true,
    });
});

// Replace photo and tracker info in pet cards
function editPhoto(petId) {
    // Set the petId in the hidden input
    document.getElementById('editPhotoPetId').value = petId;
    // Show the modal
    var photoModal = new bootstrap.Modal(document.getElementById('photoEditModal'));
    photoModal.show();
}

function editTracker(petId) {
    // Set the petId in the hidden input
    document.getElementById('editTrackerPetId').value = petId;
    // Show the modal
    var trackerModal = new bootstrap.Modal(document.getElementById('trackerEditModal'));
    trackerModal.show();
}

// Login toggle
const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

// Pet Dating
let currentMatchId = null;

function displaySelectedPet() {
    const petId = document.getElementById('petSelect').value;
    if (petId) {
        Promise.all([
            fetchPetDetails(petId),
            fetchAcceptedMatches(petId)
        ]).then(() => {
            fetchPotentialMatches(petId);
        }).catch(error => {
            console.error('Error:', error);
            displayErrorMessage('An error occurred while fetching pet data');
        });
    } else {
        window.location.reload(); // Reload page if "Select Your Pet" is chosen
    }
}

function fetchPetDetails(petId) {
    return fetch(`/get_pet_details/${petId}`)
        .then(handleResponse)
        .then(pet => displayPetCard(pet))
        .catch(error => {
            console.error('Error fetching pet details:', error);
            displayErrorMessage('Failed to load pet details');
        });
}

function fetchAcceptedMatches(petId) {
    return fetch(`/get_accepted_matches/${petId}`)
        .then(handleResponse)
        .then(matches => displayMatchesGrid(matches))
        .catch(error => {
            console.error('Error fetching accepted matches:', error);
            displayErrorMessage('Failed to load accepted matches');
        });
}

function handleResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function displayPetCard(pet) {
    const petCardHTML = `
        <div class="card h-100">
            <img src="/static/${pet.photo_path || 'placeholder.jpg'}" class="card-img-top" alt="${pet.pet_name || 'Unknown Pet'}">
            <div class="card-body">
                <h4 class="card-title">${pet.pet_name || 'Unknown'}</h4>
                <hr class="hr-card" />
                <p class="card-text">Sex: ${pet.pet_sex || 'N/A'}</p>
                <p class="card-text">Breed: ${pet.breed || 'N/A'}</p>
                <p class="card-text">Date of Birth: ${pet.pet_dob || 'N/A'}</p>
            </div>
        </div>`;
    document.getElementById('selectedPetCard').innerHTML = petCardHTML;
}

function displayMatchesGrid(matches) {
    const matchesGrid = document.getElementById('matchesGrid');
    const matchesTitle = document.getElementById('matchesGridTitle');
    matchesGrid.innerHTML = '';
    if (matches.length > 0) {
        matchesTitle.style.display = 'block';
        matches.forEach(match => {
            const matchHTML = `
                <div class="col-2">
                <div class="card">
                    <img src="/static/${match.photo_path || 'placeholder.jpg'}" class="card-img-top" alt="${match.pet_name || 'Unknown'}">
                    <div class="card-body">
                        <h6 class="card-title">${match.pet_name || 'Unknown'}</h6>
                    </div>
                </div>
            </div>`;
            matchesGrid.innerHTML += matchHTML;
        });
    } else {
        matchesTitle.style.display = 'none';
    }
}

function fetchPotentialMatches(petId) {
    fetch(`/get_potential_matches/${petId}`)
        .then(handleResponse)
        .then(fetchedMatches => {
            matchedPets = fetchedMatches;
            matchIndex = 0; // Reset the index
            displayNextMatch();
        })
        .catch(error => {
            console.error('Error:', error);
            displayErrorMessage('An error occurred while fetching matches');
        });
}

function displayNextMatch() {
    if (matchIndex < matchedPets.length) {
        const match = matchedPets[matchIndex];
        displayPotentialMatch(match);
        matchIndex++;
    } else {
        displayPlaceholderCard();
        flashMessage('No more matches');
    }
}

function displayPotentialMatch(match) {
    const matchCardHTML = `
        <div class="card h-100">
            <img src="/static/${match.photo_path || 'placeholder.jpg'}" class="card-img-top" alt="${match.pet_name || 'Unknown'}">
            <div class="card-body">
                <h4 class="card-title">${match.pet_name || 'Unknown'}</h4>
                <hr class="hr-card" />
                <p class="card-text">Sex: ${match.pet_sex || 'N/A'}</p>
                <p class="card-text">Breed: ${match.breed || 'N/A'}</p>
                <p class="card-text">Date of Birth: ${match.pet_dob || 'N/A'}</p>
            </div>
            <div class="card-footer text-center">
                <button class="btn btn-danger btn-lg mx-2" data-matched-pet-id="${match.pets_id}" onclick="rejectMatch(this)">
                    <i class="bi bi-x-circle"></i> NO
                </button>
                <button class="btn btn-success btn-lg mx-2" data-matched-pet-id="${match.pets_id}" onclick="acceptMatch(this)">
                    <i class="bi bi-check-circle"></i> YES
                </button>
            </div>
        </div>`;
    document.getElementById('potentialMatches').innerHTML = matchCardHTML;
}

function displayPlaceholderCard() {
    const placeholderCardHTML = `
        <div class="card">
            <img src="/static/placeholder.jpg" class="card-img-top" alt="No More Matches">
            <div class="card-body">
                <h4 class="card-title">No More Matches</h4>
                <hr class="hr-card" />
            </div>
        </div>`;
    document.getElementById('potentialMatches').innerHTML = placeholderCardHTML;
}

function rejectMatch(buttonElement) {
    const matchedPetId = buttonElement.getAttribute('data-matched-pet-id');
    const selectedPetId = document.getElementById('petSelect').value;
    fetch(`/reject_match/${selectedPetId}/${matchedPetId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayNextMatch();
                console.log('Match rejected');
            } else {
                console.error('Error rejecting match');
            }
        })
        .catch(error => console.error('Error:', error));
}

function acceptMatch(buttonElement) {
    const matchedPetId = buttonElement.getAttribute('data-matched-pet-id');
    const selectedPetId = document.getElementById('petSelect').value;
    fetch(`/accept_match/${selectedPetId}/${matchedPetId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Match accepted');
                
                // Find the matched pet information
                const matchedPet = matchedPets.find(pet => pet.pets_id.toString() === matchedPetId);
                if (matchedPet) {
                    addToMatchesGrid(matchedPet);  // Add to the matches grid
                }

                displayNextMatch();
            } else {
                console.error('Error accepting match');
            }
        })
        .catch(error => console.error('Error:', error));
}

function displayErrorMessage(message) {
    document.querySelector('#errorModal .modal-body').textContent = message;
    new bootstrap.Modal(document.getElementById('errorModal')).show();
}

function flashMessage(message) {
    // Simple implementation - log to console
    console.log("Message:", message);
}

function addToMatchesGrid(matchedPet) {
    const matchesGrid = document.getElementById('matchesGrid');
    const matchesGridTitle = document.getElementById('matchesGridTitle');
    const petCardHTML = `
        <div class="col-2">
            <div class="card">
                <img src="/static/${matchedPet.photo_path}" class="card-img-top" alt="${matchedPet.pet_name}">
                <div class="card-body">
                    <h6 class="card-title">${matchedPet.pet_name}</h6>
                </div>
            </div>
        </div>`;
    matchesGrid.innerHTML += petCardHTML;

    // Check if there are any pets in the grid and display the title if so
    if (matchesGrid.children.length > 0) {
        matchesGridTitle.style.display = 'block';
    }
}
  