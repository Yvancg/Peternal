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
> [!NOTE]
>This module initializes and configures the Flask application for the Peternal platform. 
>It sets up necessary configurations for session management and security. The application 
>provides users with features related to pets tracking, pets memories, and afterlife. 
>Database connections are imported from the 'database' module. Functions for user authentication, 
>registration, password validation, and session handling are imported from the 'auth' module.
>Here are the functions in the order they appear:
>-    def after_request(response):
>-    get_username_info():
>-    def index():
>-    def register():
>-    def send_confirmation_email(email):
>-    def confirm_email(token, expiration=3600):
>-    def resend_verification_email():
>-    def login():
>-    def login_with_github():
>-    def callback():
>-    def change():
>-    def request_password_reset():
>-    def send_password_reset_email(email):
>-    def reset_password(token):
>-    def logout():
>-    def add_pet():
>-    def edit_photo():
>-    def edit_tracker():
>-    def dating():
>-    def get_pet_details(pets_id):
>-    def get_potential_matches(pets_id):
>-    def reject_match_route(pet_id, matched_pet_id):
>-    def accept_match_route(pet_id, matched_pet_id):
>-    def get_accepted_matches_route(pet_id):
>
>The app uses SQLite for database operations and Werkzeug for password hashing and verification.
- `auth.py`: Handles user authentication processes.
- `database.py`: Manages database interactions.
- `config.py`: Contains configuration settings.
- `utils.py`: Utility functions for various tasks.
> [!NOTE]
>The functions are:
>-    save_pet_photo
>-    send_email
>-    get_sorted_breeds
>-    sanitize_email
>-    sanitize_username
>-    row_to_dict
- `.env`: Environment variables for secure configuration.
- `.gitignore`: Specifies files to be ignored by Git.
- `petlife.db`: SQLite database file.
> [!NOTE]
>here is the schema of the database:
```
CREATE TABLE users
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    email_verified INTEGER DEFAULT 0

CREATE TABLE pets
    pets_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    pet_type TEXT NOT NULL,
    pet_sex TEXT NOT NULL,
    pet_name TEXT NOT NULL,
    photo_path TEXT,
    breed TEXT,
    pet_dob DATE,
    tracker TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)

CREATE TABLE dating
    dating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER,
    matched_pet_id INTEGER,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY (pet_id) REFERENCES pets(pets_id),
    FOREIGN KEY (matched_pet_id) REFERENCES pets(pets_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
```
- `templates/`: HTML templates for web pages.
> [!NOTE]
>Some files are just placeholders, like tracking.html or afterlife.html for instance, as the functions have not yet been created.
- `static/`: Static files including JavaScript, CSS, images.
> [!NOTE]
>Pet photos are stored there in a specific folder named "pet_photos".

Other files, for example those used by sign in with GitHub, are present, but the process has not yet been finalized.

### Lessons learned

I made the choice to start this project out of the CS50 sandbox and take out the learning wheels. It was a steep learning curve. I had a bad local installation of Python to start with, so I had to remove it all (thanks to Google and chatGPT for the tremendous help) and re-install it all properly using homebrew. Then connecting my local git with GitHub and CodeSpaces has been another challenge, especially to make the whole thing sync seamlessly regardless of the platform I was using for coding. But I do not regret any of those choices.

There has been A LOT of iterations on this project, learning a large amount of new stuff along the way, breaking thing that were working fine while trying to secure the whole process, make it more readable and pythonic, following the latest industry's best practices, and so on.

I tried to focus on the user experience, to make the interface simple and intuitive, and to make the whole thing as accessible as possible. I also tried to make the project as modular as possible, so that it can be easily extended and improved.

I chose Flask as it was new for me and the last thing we learnt from David, but it seems that, if I really want to develop the full features for this project, I may have to shift to Django. Advice and recommendations are always welcome and appreciated, especially if they come with a detailed explanation as for why, how, what...

I started 3 projects for my final project before settling on this one, as I can see it can really be developed much further. I am planning to take another CS50 course, but still hesitant whether it will be Python, AI or cyber security. In any case, these courses will help me build this Peternal project further until I have an MVP that I can test with real users.

This project gave me confidence, and made me appreciate the beauty of a well organized code. Now the next step would be to practice coding together with other contributors, and may be start working on small projects within an organization and which are not time bound. 

If you have read so far and want to hook me up with any such company that would welcome part time junior programmer, please be my guest.

### Contributing

We welcome contributions! Please submit pull requests or issues on GitHub. Follow coding standards and provide meaningful commit messages.

### Acknowledgements

Special thanks to the CS50x 2023 course team (namely the legendary David J. Malan, Carter Zenke and all others who contributed to make this course so goddam captivating) and contributors who provided invaluable resources and support. A big thanks to the ddb Cyber Duck, and other virtual assistants, which not only provided great support, always answering multiple questions with a smile, but also gave me the idea for this virtual pet project.

### Contact

For inquiries or collaboration, reach out via [GitHub](https://github.com/yvancg).

> [!IMPORTANT]
> If you are a co-founder with a solid experience in AI-generated avatars
> or an angel investor who see the value of this project, please reach out to me directly on GitHub.
