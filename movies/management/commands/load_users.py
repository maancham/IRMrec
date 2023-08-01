import json
from django.core.management import BaseCommand
from django.contrib.auth.hashers import make_password
from ...models import Movie, Participant, ParticipantInfo
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Load user data into the database"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str)

    def handle(self, *args, **kwargs):
        User.objects.filter(is_superuser=False).delete()
        Participant.objects.all().delete()
        path = kwargs["path"]

        with open(path, encoding="utf-8") as json_file:
            user_dicts = json.load(json_file)

        for user_data in user_dicts:
            participant_info = ParticipantInfo.objects.get(
                ParticipantId=user_data["participant_id"]
            )

            user_obj = User(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                username="participant_"
                + str(participant_info.ParticipantId)
                + str(user_data["dataset_id"]),
                password=make_password(user_data["pass"]),
            )
            user_obj.save()

            rec_movies = Movie.objects.filter(movieId__in=user_data["recs"])

            new_participant = Participant(
                user=user_obj,
                participant_info=participant_info,
                datasetId=user_data["dataset_id"],
                remaining_judge_actions=len(rec_movies),
            )
            new_participant.save()

            new_participant.movies.add(*rec_movies)

            print(f"User: {user_data['dataset_id']} saved...")


"""
python manage.py load_users --path users.json
"""
