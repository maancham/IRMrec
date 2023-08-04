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


class ParticipantInfo(models.Model):
    ParticipantId = models.IntegerField(null=False, primary_key=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    age = models.IntegerField()
    gender = models.CharField(max_length=15, null=True, blank=True)
    ethnicity = models.CharField(max_length=50, null=True, blank=True)
    race = models.CharField(max_length=50, null=True, blank=True)
    education = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100)
    consent = models.BooleanField()

    def __str__(self) -> str:
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.ParticipantId:
            latest_participant_info = ParticipantInfo.objects.order_by(
                "-ParticipantId"
            ).first()

            if latest_participant_info:
                self.ParticipantId = latest_participant_info.ParticipantId + 1
            else:
                self.ParticipantId = 1

        super().save(*args, **kwargs)


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    participant_info = models.OneToOneField(ParticipantInfo, on_delete=models.CASCADE)

    taken_initial_quiz = models.BooleanField(default=False)
    given_demographics = models.BooleanField(default=False)

    datasetId = models.IntegerField(null=False)
    phaseone_movies = models.ManyToManyField(Movie)
    phasetwo_movies = models.ManyToManyField(Movie)

    remaining_p1_judge_actions = models.IntegerField(default=0)
    fully_p1_done = models.BooleanField(default=False)

    remaining_p2_judge_actions = models.IntegerField(default=0)
    fully_p2_done = models.BooleanField(default=False)

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
    rank_p1 = models.IntegerField(null=True, blank=True)
    rank_p2 = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [["participant", "movie"]]

    def __str__(self):
        return f"{self.participant.user.username} - {self.movie.title}"

    def get_rating(self):
        return self.rating

    def get_likely(self):
        return self.will_to_watch
