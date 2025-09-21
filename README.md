# Vinylcabinet

- User can add music albums to the site
- User can see albums added by themselves and others
- User can favorite albums, adding them to their "cabinet"
- User can edit and delete albums added from their cabinet
- User can create an account and sign in
- User profiles can be viewed and users cabinet can be seen by others
- Albums can be categorized by giving them genre tags
- Users can search albums and sort them by artist and genre
- Users can review albums listed on the site

# Installation and testing
1. Clone the repository
2. Create a virtual enviroment in the root: python -m venv venv
3. Activate virtual enviroment: source venv/bin/activate
4. Install dependencies: pip install flask werkzeug
5. Make config.py file with secret key in form: secret_key="..."
6. Create database file: sqlite3 database.db < schema.sql
7. Run app: flask run
