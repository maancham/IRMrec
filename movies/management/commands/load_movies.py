import pandas as pd
from math import isnan
from django.core.management import BaseCommand
from ...models import Movie


class Command(BaseCommand):
    help = "Load a movie csv file into the database"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str)

    def handle(self, *args, **kwargs):
        Movie.objects.all().delete()
        path = kwargs["path"]
        movie_df = pd.read_csv(path, lineterminator="\n", encoding="utf-8")

        for index, row in movie_df.iterrows():
            movieId = row["movieId"]
            title = row["title"]
            overview = row["overview"]
            img_path = row["img_path"]
            imdbId = row["imdbId"]
            tmdbId = row["tmdbId"]
            year = row["year"]
            genres = row["genres"]
            runtime = row["runtime"]
            cast = row["cast"]
            directors = row["directors"]
            languages = row["languages"]

            if not movieId.isdigit():
                print(row)
                continue

            if isnan(runtime):
                runtime = 0

            # Populate Movie object for each row
            movie = Movie(
                movieId=movieId,
                title=title,
                overview=overview,
                img_path=img_path,
                imdbId=imdbId,
                tmdbId=tmdbId,
                year=year,
                genres=genres,
                runtime=runtime,
                cast=cast,
                directors=directors,
                languages=languages,
                map=None,
            )

            # Save movie object
            movie.save()
            # print(f"Movie: {movieId}, {title} saved...")
        
        print("All movies: ", len(movie_df))
        print("Saved movies: ", len(Movie.objects.all()))



"""
docker-compose exec web python code/manage.py load_movies --path code/movies.csv
"""
