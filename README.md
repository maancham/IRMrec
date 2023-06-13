# IRMrec
A web application to make movie recommendations, gather user feedback, and create a test collection


## Getting Started
To set up IRMrec locally, follow these steps:

1. Clone this repository:
   ```bash
   $ git clone https://github.com/maancham/IRMrec.git

2. Create a Python virtual environment and activate it:
   ```bash
   $ python -m venv env
   $ source env/bin/activate

3. Install dependencies from requirements file:
   ```bash
   $ pip install -r requirements.txt
   
4. Then simply apply the migrations:
   ```bash
   $ python manage.py migrate

5. You will need two files to populate the database, I have excluded them from the repository due to privacy reasons. The first file is called `movies.csv` which is as follows:

    | Column     | Description                                                            |
    |------------|------------------------------------------------------------------------|
    | movieId    | Unique identifier for each movie                                        |
    | imdbId     | IMDb identifier for each movie                                          |
    | tmdbId     | TMDB identifier for each movie                                          |
    | title      | Title of the movie                                                      |
    | genres     | Genres associated with the movie (comma-separated string)               |
    | year       | Year of release of the movie                                            |
    | overview   | Brief overview or synopsis of the movie                                 |
    | img_path   | TMDB link to the movie's image                                          |
    | runtime    | Duration of the movie in minutes                                        |
    | cast       | Actors and actresses in the movie (comma-separated string)              |
    | directors  | Directors of the movie (comma-separated string)                         |
    | languages  | Languages spoken in the movie (comma-separated string)                  |
    | map        | MAP rating of the movie (e.g., PG-13, R, etc.)                          |
 
  and the second one is `users.json`, which is a list of json objects. Each object has the following structure:

  - `first_name`: First name of the user associated with the dataset.
  - `last_name`: Last name of the user associated with the dataset.
  - `dataset_id`: Unique identifier from the training dataset.
  - `pass`: Password or access key to log into the webapp.
  - `recs`: An array of recommended movie IDs for the user.

6. Populate the database with movies and users:
   ```bash
   $ python manage.py load_movies --path movies.csv
   $ python manage.py load_users --path users.json
 
7. You can now start the development server:
   ```bash
   $ python manage.py runserver
