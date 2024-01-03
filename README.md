# PETERNAL

![Peternal](/static/peternal-logo.png)

## Video Demo: [Check it on YouTube](https://youtu.be/Nf9Ip7SxoKg)

### Description

Author: Yvan Clot-Goudard

Location: Bangkok, Thailand

**Peternal** is an innovative social media platform crafted exclusively for pets and their owners. Developed as my capstone project for Harvard's CS50x 2023 course, Peternal stands as a unique venture, open to collaborations and investments.

**Project Vision:** Merging affection for pets with cutting-edge technology, Peternal aims to offer a holistic and engaging experience for pet owners. It provides a space for sharing, caring, and even immortalizing the memories of beloved pets.

### Key Features

- **User-Friendly Registration:** Streamlined sign-up process for quick access.
- **Pet Profiles:** Detailed pet profiles including photos, names, breeds, and more.
- **Pet Matching:** "Dating" feature to find compatible matches for pets.
- **User Control:** Comprehensive management of pet trackers, photo updates, and account settings.

### Future Enhancements

- **Social Sharing:** Options to post and share pet memories with adjustable privacy settings, like a furry Muzzlebook.
- **Pet Tracking:** Integration of physical trackers for real-time pet location updates.
- **Health Management:** Tools for tracking pet health records, setting reminders, and more.
- **Eternal Life Technology:** Advanced AI to create lifelike, interactive pet avatars for lasting memories.

## Technology Stack

- **Backend:** Python with Flask framework
- **Database:** SQLite for data management
- **Frontend:** HTML, CSS, JavaScript for dynamic and responsive design

## Getting Started

To run Peternal locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/yvancg/peternal.git
   ```

2. Navigate to the project directory and install dependencies:

   ```bash
   cd peternal
   pip3 install -r requirements.txt
   ```

3. Start the Flask application:

   ```bash
   flask run
   ```

4. Access the application at `http://127.0.0.1:5000/`.

Ensure Python and Flask are installed on your machine.

### Project Structure

- `app.py`: Main application file with Flask routes.
>This module initializes and configures the Flask application for the Peternal platform. 
>It sets up necessary configurations for session management and security. The application 
>provides users with features related to pets tracking, pets memories, and afterlife. 
>Database connections are imported from the 'database' module. Functions for user authentication, 
>registration, password validation, and session handling are imported from the 'auth' module.
>Here are the functions in the order they appear:
>- [x]     def after_request(response):
>- [x]     get_username_info():
- [x]     def index():
- [x]     def register():
- [x]     def send_confirmation_email(email):
- [x]     def confirm_email(token, expiration=3600):
- [x]     def resend_verification_email():
- [x]     def login():
- [x]     def login_with_github():
- [x]     def callback():
- [x]     def change():
- [x]     def request_password_reset():
- [x]     def send_password_reset_email(email):
- [x]     def reset_password(token):
- [x]     def logout():
- [x]     def add_pet():
- [x]     def edit_photo():
- [x]     def edit_tracker():
- [x]     def dating():
- [x]     def get_pet_details(pets_id):
- [x]     def get_potential_matches(pets_id):
- [x]     def reject_match_route(pet_id, matched_pet_id):
- [x]     def accept_match_route(pet_id, matched_pet_id):
- [x]     def get_accepted_matches_route(pet_id):
The app uses SQLite for database operations and Werkzeug for password hashing and verification.
- `auth.py`: Handles user authentication processes.
- `database.py`: Manages database interactions.
- `config.py`: Contains configuration settings.
- `utils.py`: Utility functions for various tasks.
- `.env`: Environment variables for secure configuration.
- `.gitignore`: Specifies files to be ignored by Git.
- `petlife.db`: SQLite database file.
- `templates/`: HTML templates for web pages.
- `static/`: Static files including JavaScript, CSS, images.

> **Note:** Some files are just placeholders, like tracking.html or afterlife.html for instance. Other files, for example those used by sign in with GitHub, have not yet been activated.

### Contributing

We welcome contributions! Please submit pull requests or issues on GitHub. Follow coding standards and provide meaningful commit messages.

### Acknowledgements

Special thanks to the CS50x 2023 course team (namely the legendary David J. Malan, Carter Zenke and all others who contributed to make this course so goddam captivating) and contributors who provided invaluable resources and support. A big thanks to the ddb Cyber Duck, and other virtual assistants, which not only provided great support, always answering multiple questions with a smile, but also gave me the idea for this virtual pet project.

### Contact

For inquiries or collaboration, reach out via [GitHub](https://github.com/yvancg).

> **Note:** Seeking angel investors recognizing the potential of Peternal.
> [!IMPORTANT]
> If you are a co-founder with a solid experience in AI-generated avatars
> or an angel investor who see the value of this project, please reach out to me directly on GitHub.
