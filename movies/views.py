from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Movie, Participant, ParticipantInfo, Interaction
from django.contrib.auth import logout
from .forms import ParticipantInfoForm
import logging


## global flag to set the stage (1 or 2)
STUDY_STAGE = 1


"""
TODO:
------------------------------
http://127.0.0.1:8000/accounts/login/?next=/home/
results in error when not logged in!

sudo service postgresql start


activate SessionTimeoutMiddleware in settings
"""


"""
PROCESS TO POPULATE AN EMPTY DB:
1 - make migrations
2 - migrate
3 - create superuser (admin)
4 - add movies from file
5 - add participants from file
"""


logger = logging.getLogger(__name__)


def overview(request):
    if request.method == "POST":
        form = ParticipantInfoForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data["full_name"]
            email = form.cleaned_data["email"]
            age = form.cleaned_data["age"]
            country = form.cleaned_data["country"]
            consent = True

            participant_info = ParticipantInfo(
                full_name=full_name,
                email=email,
                age=age,
                country=country,
                consent=consent,
            )
            participant_info.save()

            logger.info(
                f"submit_consent: {full_name}, {age}, with email {email}, from {country} gave consent"
            )

            return render(request, "movies/overviewDone.html")
    else:
        form = ParticipantInfoForm()

    return render(request, "movies/overview.html", {"form": form})


# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"login_action: User {username} successfully logged in.")
            return redirect("home")
        else:
            messages.error(
                request,
                "Invalid username or password, please try again or contact h2chaman@uwaterloo.ca for assistance",
            )
    return render(request, "movies/login.html")


@login_required
def demographic(request):
    participant = Participant.objects.get(user=request.user)
    participant_info = participant.participant_info

    if request.method == "POST":
        participant_info.gender = request.POST["gender"]
        participant_info.race = request.POST["race"]
        participant_info.education = request.POST["education"]
        participant_info.save()

        participant.given_demographics = True
        participant.save()

        logger.info(
            f"demographic_action: User {participant.user.username} submitted their demographic info. Gender: {participant_info.gender}, Race: {participant_info.race}, Education: {participant_info.education}"
        )

        return redirect("home")

    return render(request, "movies/demographic.html")


@login_required
def tutorial(request):
    participant = Participant.objects.get(user=request.user)

    if request.method == "POST":
        participant.taken_initial_quiz = True
        participant.save()
        return redirect("home")

    return render(request, "movies/tutorial.html")


@login_required
def home(request):
    participant = Participant.objects.get(user=request.user)
    if participant.given_demographics != True:
        return redirect("demographic")

    if not participant.taken_initial_quiz:
        return redirect("tutorial")

    fully_done = (
        participant.fully_p1_done if STUDY_STAGE == 1 else participant.fully_p2_done
    )
    if fully_done:
        return render(request, "movies/rankingDone.html", {"study_stage": STUDY_STAGE})
    else:
        remaining_judge_actions = (
            participant.remaining_p1_judge_actions
            if STUDY_STAGE == 1
            else participant.remaining_p2_judge_actions
        )
        return render(
            request,
            "movies/home.html",
            {"remaining_judge_actions": remaining_judge_actions},
        )


@login_required
def movie_list(request):
    participant = Participant.objects.get(user=request.user)
    if not participant.taken_initial_quiz:
        return redirect("home")

    logger.info(
        f"view_movie_list: User {participant.user.username} shown movie list page."
    )

    user_interactions = (
        Interaction.objects.filter(participant=participant)
        .select_related("movie")
        .order_by("movie__title")
    )
    judged_movies = [interaction.movie for interaction in user_interactions]

    if (STUDY_STAGE == 1 and participant.fully_p1_done) or (
        STUDY_STAGE == 2 and participant.fully_p2_done
    ):
        return render(request, "movies/rankingDone.html", {"study_stage": STUDY_STAGE})

    interactions = {
        interaction.movie.movieId: interaction for interaction in user_interactions
    }

    sort_by = request.GET.get("sort_by", None)
    INTEREST_LEVELS = [
        "Extremely interested",
        "Very interested",
        "Interested",
        "Somewhat interested",
        "Not interested",
    ]

    if sort_by == "willingness":
        logger.info(
            f"change_sort_by: User {participant.user.username} changed sorting to willingness."
        )
        judged_movies.sort(
            key=lambda movie: INTEREST_LEVELS.index(
                interactions[movie.movieId].will_to_watch
            )
        )

    elif sort_by == "rating":
        logger.info(
            f"change_sort_by: User {participant.user.username} changed sorting to rating."
        )
        judged_movies = sorted(
            judged_movies,
            key=lambda m: interactions[m.movieId].rating
            if interactions[m.movieId] and interactions[m.movieId].rating
            else -9999,
            reverse=True,
        )

    paginator = Paginator(judged_movies, 10)
    page = request.GET.get("page")
    try:
        logger.info(
            f"change_list_page: User {participant.user.username} changed page to {page}."
        )
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    remaining_judge_actions = (
        participant.remaining_p1_judge_actions
        if STUDY_STAGE == 1
        else participant.remaining_p2_judge_actions
    )
    return render(
        request,
        "movies/items.html",
        {
            "movies": movies,
            "interactions": interactions,
            "remaining_judge_actions": remaining_judge_actions,
        },
    )


@login_required
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    participant = Participant.objects.get(user=request.user)

    if not participant.taken_initial_quiz:
        return redirect("home")

    if (STUDY_STAGE == 1 and participant.fully_p1_done) or (
        STUDY_STAGE == 2 and participant.fully_p2_done
    ):
        return render(request, "movies/rankingDone.html", {"study_stage": STUDY_STAGE})

    logger.info(
        f"view_movie: User {participant.user.username} shown movie/{movie.movieId} page."
    )

    interaction = Interaction.objects.filter(
        participant=participant, movie=movie
    ).first()

    if request.method == "POST":
        seen_status = request.POST.get("seen_status")
        familiarity = request.POST.get("familiarity")
        rating = request.POST.get("rating")
        will_to_watch = request.POST.get("will_to_watch")

        if seen_status == "true":
            seen_status = True
        else:
            seen_status = False

        if interaction:
            interaction.seen_status = seen_status
            interaction.familiarity = familiarity
            interaction.rating = rating
            interaction.will_to_watch = will_to_watch
            interaction.save()

            logger.info(
                f"edit_judge_action: User {participant.user.username} edited interaction with movie/{movie.movieId}. Seen Status: {seen_status}, Familiarity: {familiarity}, Rating: {rating}, Will to Watch: {will_to_watch}"
            )
        else:
            interaction = Interaction.objects.create(
                participant=participant,
                movie=movie,
                seen_status=seen_status,
                familiarity=familiarity,
                rating=rating,
                will_to_watch=will_to_watch,
            )
            if STUDY_STAGE == 1:
                participant.remaining_p1_judge_actions -= 1
            else:
                participant.remaining_p2_judge_actions -= 1
            participant.save()

            logger.info(
                f"submit_judge_action: User {participant.user.username} submitted interaction with movie/{movie.movieId}. Seen Status: {seen_status}, Familiarity: {familiarity}, Rating: {rating}, Will to Watch: {will_to_watch}"
            )

        return redirect("movie_judge")

    context = {
        "movie": movie,
        "ex_seen_status": interaction.seen_status if interaction else None,
        "ex_familiarity": interaction.familiarity if interaction else None,
        "ex_rating": "N/A"
        if not interaction or not interaction.rating
        else interaction.rating,
        "ex_will_to_watch": interaction.will_to_watch if interaction else None,
        "interaction_exists": interaction is not None,
    }

    return render(request, "movies/item.html", context)


@login_required
def judge(request):
    participant = Participant.objects.get(user=request.user)
    if not participant.taken_initial_quiz:
        return redirect("home")

    if STUDY_STAGE == 1:
        unjudged_movie = participant.phaseone_movies.exclude(
            interaction__participant=participant
        ).first()
    else:
        unjudged_movie = participant.phasetwo_movies.exclude(
            interaction__participant=participant
        ).first()

    remaining_judge_actions = (
        participant.remaining_p1_judge_actions
        if STUDY_STAGE == 1
        else participant.remaining_p2_judge_actions
    )

    if unjudged_movie is None and remaining_judge_actions == 0:
        logger.info(
            f"view_judge_done: User {participant.user.username} shown judge done page."
        )
        return render(request, "movies/judgeDone.html")
    else:
        return redirect("movie_detail", movie_id=unjudged_movie.movieId)


@login_required
def final_ranking(request):
    participant = Participant.objects.get(user=request.user)
    if not participant.taken_initial_quiz:
        return redirect("home")

    remaining_judge_actions = (
        participant.remaining_p1_judge_actions
        if STUDY_STAGE == 1
        else participant.remaining_p2_judge_actions
    )
    if remaining_judge_actions != 0:
        logger.info(
            f"view_ranking_locked: User {participant.user.username} shown ranking locked page."
        )
        return render(request, "movies/rankingLocked.html")

    fully_done = (
        participant.fully_p1_done if STUDY_STAGE == 1 else participant.fully_p2_done
    )

    if fully_done:
        logger.info(
            f"view_feedback: User {participant.user.username} shown feedback page."
        )
        return redirect("feedback")

    if request.method == "POST":
        ranks = []
        ranks.append(request.POST.get("rank1"))
        ranks.append(request.POST.get("rank2"))
        ranks.append(request.POST.get("rank3"))

        for idx, movie_id in enumerate(ranks):
            try:
                movie = get_object_or_404(Movie, pk=movie_id)
                interaction = Interaction.objects.get(
                    participant=participant, movie=movie
                )
                if STUDY_STAGE == 1:
                    interaction.rank_p1 = idx + 1
                else:
                    interaction.rank_p2 = idx + 1
                interaction.save()
            except:
                print("ranking save not successful!")

        if STUDY_STAGE == 1:
            participant.fully_p1_done = True
        else:
            participant.fully_p2_done = True
        participant.save()

        rank_values = ", ".join(ranks)
        logger.info(
            f"submit_ranking_action: User {participant.user.username} submitted ranking. Ranks: {rank_values}"
        )

        return redirect("feedback")

    top_interactions = Interaction.objects.filter(
        participant=participant, will_to_watch="Extremely interested"
    )

    if len(top_interactions) < 3:
        top_interactions = Interaction.objects.filter(
            participant=participant,
            will_to_watch__in=["Extremely interested", "Very interested"],
        )

    if len(top_interactions) < 3:
        top_interactions = Interaction.objects.filter(
            participant=participant,
            will_to_watch__in=[
                "Extremely interested",
                "Very interested",
                "Interested",
            ],
        )

    if len(top_interactions) < 3:
        top_interactions = Interaction.objects.filter(
            participant=participant,
            will_to_watch__in=[
                "Extremely interested",
                "Very interested",
                "Interested",
                "Somewhat interested",
            ],
        )

    # Get all movies for the top interactions
    top_movies = Movie.objects.filter(interaction__in=top_interactions).distinct()

    context = {"top_movies": top_movies}

    logger.info(f"view_ranking: User {participant.user.username} shown ranking page.")
    return render(request, "movies/ranking.html", context)


@login_required
def feedback(request):
    participant = Participant.objects.get(user=request.user)

    if (participant.gave_p1_feedback and STUDY_STAGE == 1) or (
        participant.gave_p2_feedback and STUDY_STAGE == 2
    ):
        return render(request, "movies/rankingDone.html", {"study_stage": STUDY_STAGE})

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        if STUDY_STAGE == 1:
            participant.p1_feedback = feedback_text
            participant.gave_p1_feedback = True
        else:
            participant.p2_feedback = feedback_text
            participant.gave_p2_feedback = True
        participant.save()
        return render(request, "movies/rankingDone.html", {"study_stage": STUDY_STAGE})

    return render(request, "movies/feedback.html", {"study_stage": STUDY_STAGE})


def handle_404(request, exception):
    participant = Participant.objects.get(user=request.user)
    logger.info(
        f"view_404: User {participant.user.username} shown 404 page for {request}."
    )
    return render(request, "movies/404.html", status=404)


def logout_view(request):
    participant = Participant.objects.get(user=request.user)
    logout(request)
    logger.info(
        f"logout_action: User {participant.user.username} successfully logged out."
    )
    return redirect("login")
