

// Pet Dating
let currentMatchId = null;

function displaySelectedPet() {
    const petId = document.getElementById('petSelect').value;
    if (petId) {
        // Fetch the pet details using an AJAX request
        fetch(`/get_pet_details/${petId}`)
            .then(response => response.json())
            .then(pet => {
                // Build and display the pet card
                const petCardHTML = `
                    <div class="card h-100">
                        <img src="/static/${pet.photo_path}" class="card-img-top" alt="${pet.pet_name}">
                        <div class="card-body">
                            <h4 class="card-title">${pet.pet_name}</h4>
                            <hr class="hr-card" />
                            <p class="card-text">Sex: ${pet.pet_sex}</p>
                            <p class="card-text">Breed: ${pet.breed}</p>
                            <p class="card-text">Date of Birth: ${pet.pet_dob}</p>
                        </div>
                    </div>`;
                document.getElementById('selectedPetCard').innerHTML = petCardHTML;

                // Fetch and display potential matches
                fetchPotentialMatches(petId);
            })
            .catch(error => console.error('Error:', error));

        fetch(`/get_accepted_matches/${petId}`)
            .then(response => response.json())
            .then(matches => {
                const matchesGrid = document.getElementById('matchesGrid');
                const matchesTitle = document.getElementById('matchesGridTitle');
                matchesGrid.innerHTML = '';  // Clear existing matches
                if (matches.length > 0) {
                    // Show the title if there are matches
                    matchesTitle.style.display = 'block';
                    // Add each match to the grid
                    matches.forEach(match => {
                        // Add match to matchesGrid
                        const matchHTML = `
                            <div class="col-2">
                            <div class="card">
                                <img src="/static/${match.photo_path}" class="card-img-top" alt="${match.pet_name}">
                                <div class="card-body">
                                    <h6 class="card-title">${match.pet_name}</h6>
                                </div>
                            </div>
                        </div>`;
                        document.getElementById('matchesGrid').innerHTML += matchHTML;
                    });
            })
            .catch(error => console.error('Error:', error));
    } else {
        displayPlaceholderCard();
        document.getElementById('selectedPetCard').innerHTML = '';
        // Clear potential matches as well
        document.getElementById('potentialMatches').innerHTML = '';
    }
}

function fetchPotentialMatches(petId) {
    fetch(`/get_potential_matches/${petId}`)
        .then(response => response.json())
        .then(fetchedMatches => {
            matchedPets = fetchedMatches;
            matchIndex = 0; // Reset the index

            if (matchedPets.length > 0) {
                displayNextMatch();
                matchIndex++; // Increment for the next match
            } else {
                displayPlaceholderCard();
                flashMessage('No match found');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            flashMessage('An error occurred while fetching matches');
        });
}

function displayNextMatch() {
    if (matchIndex < matchedPets.length) {
        displayPotentialMatch(matchedPets[matchIndex]);
        matchIndex++;
    } else {
        displayPlaceholderCard();
        flashMessage('No more matches');
    }
}

function displayPotentialMatch(match) {
    // Display match details in potentialMatchCard
    const matchCardHTML = `
            <div class="card h-100">
            <img src="/static/${match.photo_path}" class="card-img-top" alt="${match.pet_name}">
            <div class="card-body">
                <h4 class="card-title">${match.pet_name}</h4>
                <hr class="hr-card" />
                <p class="card-text">Sex: ${match.pet_sex}</p>
                <p class="card-text">Breed: ${match.breed}</p>
                <p class="card-text">Date of Birth: ${match.pet_dob}</p>
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
            <img src="/static/placeholder.jpg" class="card-img-top" alt="Placeholder">
            <div class="card-body">
                <h4 class="card-title">No More Matches</h4>
                <hr class="hr-card" />
                <p class="card-text"> </p>
                <p class="card-text"> </p>
                <p class="card-text"> </p>
            </div>
            <div class="card-footer text-center">
                <button class="btn btn-danger btn-lg mx-2">
                    <i class="bi bi-x-circle"></i> NO
                </button>
                <button class="btn btn-success btn-lg mx-2">
                    <i class="bi bi-check-circle"></i> YES
                </button>
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

function addToMatchesGrid(matchedPet) {
    const matchesGrid = document.getElementById('matchesGrid');
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
}

function flashMessage(message) {
    // Simple implementation - log to console
    console.log("Message:", message);
}

*/
