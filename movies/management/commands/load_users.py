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

            username = "participant_" + str(participant_info.ParticipantId) + "_" + str(user_data["dataset_id"])

            user_obj = User(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                username="participant_"
                + str(participant_info.ParticipantId) + "_"
                + str(user_data["dataset_id"]),
                password=make_password(user_data["pass"]),
            )
            user_obj.save()

            p1_recs = Movie.objects.filter(movieId__in=user_data["p1_recs"])
            p2_recs = Movie.objects.filter(movieId__in=user_data["p2_recs"])

            new_participant = Participant(
                user=user_obj,
                participant_info=participant_info,
                datasetId=user_data["dataset_id"],
                remaining_p1_judge_actions=len(p1_recs),
                remaining_p2_judge_actions=len(p2_recs),
            )
            new_participant.save()

            new_participant.phaseone_movies.add(*p1_recs)
            new_participant.phasetwo_movies.add(*p2_recs)

            print(f"User: {username} saved...")
            print("P1 items", len(user_data["p1_recs"]), len(p1_recs))
            print("P2 items", len(user_data["p2_recs"]), len(p2_recs))


"""
docker-compose exec web python code/manage.py load_users --path code/users.json
"""
