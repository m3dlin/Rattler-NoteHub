# Rattler-NoteHub
CS3340 Project + CS4395 Senior Project

## Summary 
Rattler NoteHub is a platform that allows St. Mary’s students to post notes for various classes in PDF format. This platform allows users to upload PDF files related to their courses and then add descriptions and tags to them. The system acts as a central repository for organizing and managing course materials, thereby improving students' learning outcomes. To use the website's features, users must create an account. After logging in, users can access their dashboard or course-specific pages to upload PDF files for their classes. The system allows users to store and manage multiple PDF documents, which they can categorize based on their courses. The system may also include features that improve the note-taking process, such as the ability to search for specific keywords from the note’s title and organize notes by topic or date. Other capabilities of the platform will include discussion boards for notes being posted, note annotations for other students to view, study tools such as a quiz generator based on the note uploaded, and a better user interface for navigating.
## Installation

1. Navigate to desired folder and clone the project's repository using
```sh
git clone https://github.com/m3dlin/Rattler-NoteHub.git
```

2. Install all dependencies needed for the project to run
```sh
pip install -r requirements.txt
```
## Usage
 

Run the app in development mode using
```sh
python app.py
```
open [http://127.0.0.1:5000](http://127.0.0.1:5000) to view it in your browser


### Accessing User and Password Credentials
To access user and password credentials for the database connection in this project, follow these steps:

#### Prerequisites
- Ensure you have the necessary permissions and access rights to use the database.

#### Configuration File
IMPORTANT: To be able to work locally on a development server, you must add the database credentials and firebase credentials into a .env file and .json file respectively within root of project. 

Here's a template below -

Example `.env` structure:
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_NAME=your_database_name
SECRET_KEY=your_secret_key
```

Example `.json` structure:
```env
{
    "type": "account_type",
    "project_id": "project_id",
    "private_key_id": "key",
    "private_key": "private_key",
    "universe_domain": "googleapis.com"
}
```