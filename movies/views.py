from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Movie, Participant, Interaction
from django.contrib.auth import logout
import logging


"""
TODO:
------------------------------
edit movie list page according to updated movie details
add logging to movie detail page once everthing is finialized


add /overview url for when users first click on banner
    (no login required
    copy paste from ethics
    need to edit participant model to save consent and demographic data, movies empty for now)
add /upload_profile url for users to add their ratings.csv, need to save it to DB somehow
implement the two phase scenario
    edit userpooling so that 10 items from ratings profile are shuffled into the first 100 (depth k1 from all algo outputs)
    change user model to have two sets of movies (p1 and p2)
    change user model to have two sets of (rem_judge, done) pairs for each phase
    change interaction model to have two ranks (p1 rank and p2 rank)
    set a global flag on views.py to denote we're on phase 1 or 2?
    change all views to get movies from correct movie set based on flag


Change the load_users section, make username and password anon (B-userpooling on colab + load_users)
remove the django-toolbar from the project
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
def home(request):
    participant = Participant.objects.get(user=request.user)
    if participant.fully_done:
        return render(request, "movies/rankingDone.html")
    else:
        return render(
            request,
            "movies/home.html",
            {
                "remaining_judge_actions": participant.remaining_judge_actions,
                # TODO: CHANGE THIS BACK TO NORMAL:
                # "quiz_done": participant.taken_initial_quiz,
                "quiz_done": True,
            },
        )


@login_required
def movie_list(request):
    participant = Participant.objects.get(user=request.user)

    logger.info(
        f"view_movie_list: User {participant.user.username} shown movie list page."
    )

    user_interactions = (
        Interaction.objects.filter(participant=participant)
        .select_related("movie")
        .order_by("movie__title")
    )
    judged_movies = [interaction.movie for interaction in user_interactions]

    if participant.fully_done:
        return render(request, "movies/rankingDone.html")

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

    return render(
        request,
        "movies/items.html",
        {
            "movies": movies,
            "interactions": interactions,
            "remaining_judge_actions": participant.remaining_judge_actions,
        },
    )


@login_required
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    participant = Participant.objects.get(user=request.user)

    if participant.fully_done:
        return render(request, "movies/rankingDone.html")

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
        else:
            interaction = Interaction.objects.create(
                participant=participant,
                movie=movie,
                seen_status=seen_status,
                familiarity=familiarity,
                rating=rating,
                will_to_watch=will_to_watch,
            )
            participant.remaining_judge_actions -= 1
            participant.save()

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
    unjudged_movie = participant.movies.exclude(
        interaction__participant=participant
    ).first()
    if unjudged_movie is None and participant.remaining_judge_actions == 0:
        logger.info(
            f"view_judge_done: User {participant.user.username} shown judge done page."
        )
        return render(request, "movies/judgeDone.html")
    else:
        return redirect("movie_detail", movie_id=unjudged_movie.movieId)


@login_required
def final_ranking(request):
    participant = Participant.objects.get(user=request.user)
    remaining = participant.remaining_judge_actions
    if remaining != 0:
        logger.info(
            f"view_ranking_locked: User {participant.user.username} shown ranking locked page."
        )
        return render(request, "movies/rankingLocked.html")

    if participant.fully_done:
        logger.info(
            f"view_ranking_done: User {participant.user.username} shown ranking done page."
        )
        return render(request, "movies/rankingDone.html")

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
                interaction.rank = idx + 1
                interaction.save()
            except:
                print("ranking save not successful!")

        participant.fully_done = True
        participant.save()
        logger.info(
            f"submit_ranking_action: User {participant.user.username} submitted ranking."
        )
        return render(request, "movies/rankingDone.html")

    top_interactions = Interaction.objects.filter(
        participant=participant, likely_to_watch="Very Interested"
    )

    if len(top_interactions) < 3:
        top_interactions = Interaction.objects.filter(
            participant=participant,
            likely_to_watch__in=["Very Interested", "Interested"],
        )

    if len(top_interactions) < 3:
        top_interactions = Interaction.objects.filter(
            participant=participant,
            likely_to_watch__in=["Very Interested", "Interested", "Not Interested"],
        )

    if len(top_interactions) < 3:
        top_interactions = Interaction.objects.filter(
            participant=participant,
            likely_to_watch__in=[
                "Very Interested",
                "Interested",
                "Not Interested",
                "Disappointed",
            ],
        )

    # Get all movies for the top interactions
    top_movies = Movie.objects.filter(interaction__in=top_interactions).distinct()

    context = {"top_movies": top_movies}

    logger.info(f"view_ranking: User {participant.user.username} shown ranking page.")
    return render(request, "movies/ranking.html", context)


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
