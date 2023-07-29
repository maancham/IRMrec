from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Movie(models.Model):
    # Movie ID in ML dataset
    movieId = models.IntegerField(null=False, primary_key=True)

    # Title
    title = models.CharField(max_length=250, null=False)

    # Summary
    overview = models.TextField()

    # Image URL
    img_path = models.URLField()

    # IMDB movie ID
    imdbId = models.CharField(max_length=40, null=False)

    # TMDB movie ID
    tmdbId = models.CharField(max_length=40, null=False)

    # Title year
    year = models.IntegerField(default=1970)

    # Genres
    genres = models.TextField(null=True)

    runtime = models.IntegerField(null=True, blank=True, default=0)
    cast = models.TextField(null=True)
    directors = models.TextField(null=True)
    languages = models.TextField(null=True)
    map = models.CharField(max_length=15, null=True)

    def __str__(self):
        movie_representation = (
            self.title + ", " + str(self.year) + ", " + str(self.movieId)
        )
        return movie_representation


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    datasetId = models.IntegerField(null=False)
    movies = models.ManyToManyField(Movie)

    taken_initial_quiz = models.BooleanField(default=False)
    remaining_judge_actions = models.IntegerField(default=0)
    fully_done = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username


class Interaction(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    familiarity = models.CharField(
        max_length=20,
        choices=[
            ("Never", "Never heard of it"),
            ("Familiar", "Familiar with movie"),
            ("Very familiar", "Very familiar (read reviews, seen trailers, etc.)"),
            ("Seen", "Seen it"),
        ],
        null=True,
        blank=True,
    )

    seen_status = models.BooleanField(default=False)

    rating = models.DecimalField(
        decimal_places=1,
        max_digits=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.5), MaxValueValidator(5)],
    )

    will_to_watch = models.CharField(
        max_length=20,
        choices=[
            ("Not interested", ""),
            ("Somewhat interested", ""),
            ("Interested", ""),
            ("Very interested", ""),
            ("Extremely interested", ""),
        ],
        null=True,
        blank=True,
    )
    rank = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [["participant", "movie"]]

    def __str__(self):
        return f"{self.participant.user.username} - {self.movie.title}"

    def get_rating(self):
        return self.rating

    def get_likely(self):
        return self.will_to_watch
