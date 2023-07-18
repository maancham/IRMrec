from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Movie, Participant, Interaction
from django.contrib.auth import logout


"""
TODO:
------------------------------
add normal info level logging and test it out
handle anon logging in (just on the surface!)
add critical or failiure level logging and also proper notification
"""


"""
PROCESS TO POPULATE AN EMPTY DB:
1 - make migrations
2 - migrate
3 - create superuser (admin)
4 - add movies from file
5 - add participants from file

"""


# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(
                request,
                "Invalid username or password, please contact h2chaman@uwaterloo.ca for assistance",
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
    # participant = Participant.objects.get(user=request.user)
    # user_movies = participant.movies.all().order_by("title")

    # judged_movies = []

    # interactions = {}
    # for movie in user_movies:
    #     try:
    #         interaction = Interaction.objects.get(movie=movie, participant=participant)
    #         interactions[movie.movieId] = interaction
    #         judged_movies.append(movie)
    #     except Interaction.DoesNotExist:
    #         interactions[movie.movieId] = None

    participant = Participant.objects.get(user=request.user)
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
        "Very Interested",
        "Interested",
        "Not Interested",
        "Disappointed",
        "Awful/Horrible",
    ]

    if sort_by == "reaction":
        judged_movies.sort(
            key=lambda movie: INTEREST_LEVELS.index(
                interactions[movie.movieId].likely_to_watch
            )
        )

    elif sort_by == "rating":
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

    # try:
    #     interaction = Interaction.objects.get(participant=participant, movie=movie)
    #     ex_seen_status = interaction.seen_status
    #     ex_rating = "N/A" if interaction.rating == None else interaction.rating
    #     ex_likely_to_watch = interaction.likely_to_watch
    #     interaction_exists = True
    # except:
    #     ex_seen_status = None
    #     ex_rating = None
    #     ex_likely_to_watch = None
    #     interaction_exists = False

    interaction = Interaction.objects.filter(
        participant=participant, movie=movie
    ).first()

    if request.method == "POST":
        seen_status = request.POST.get("seen_status")
        rating = request.POST.get("rating")
        likely_to_watch = request.POST.get("likely_to_watch")

        if interaction:
            interaction.seen_status = seen_status
            interaction.rating = rating
            interaction.likely_to_watch = likely_to_watch
            interaction.save()
        else:
            interaction = Interaction.objects.create(
                participant=participant,
                movie=movie,
                seen_status=seen_status,
                rating=rating,
                likely_to_watch=likely_to_watch,
            )
            participant.remaining_judge_actions -= 1
            participant.save()

        return redirect("movie_judge")

    context = {
        "movie": movie,
        "ex_seen_status": interaction.seen_status if interaction else None,
        "ex_rating": "N/A"
        if not interaction or not interaction.rating
        else interaction.rating,
        "ex_likely_to_watch": interaction.likely_to_watch if interaction else None,
        "interaction_exists": interaction is not None,
    }

    # if request.method == "POST":
    #     seen_status = request.POST.get("seen_status")
    #     rating = request.POST.get("rating")
    #     likely_to_watch = request.POST.get("likely_to_watch")

    #     try:
    #         interaction = Interaction.objects.get(participant=participant, movie=movie)
    #         interaction.seen_status = seen_status
    #         interaction.rating = rating
    #         interaction.likely_to_watch = likely_to_watch
    #         interaction.save()
    #     except Interaction.DoesNotExist:
    #         interaction = Interaction.objects.create(
    #             participant=participant,
    #             movie=movie,
    #             seen_status=seen_status,
    #             rating=rating,
    #             likely_to_watch=likely_to_watch,
    #         )

    #     if interaction_exists == False:
    #         participant.remaining_judge_actions -= 1
    #         participant.save()

    # return redirect("movie_judge")

    # context = {
    #     "movie": movie,
    #     "ex_seen_status": ex_seen_status,
    #     "ex_rating": ex_rating,
    #     "ex_likely_to_watch": ex_likely_to_watch,
    #     "interaction_exists": interaction_exists,
    # }
    return render(request, "movies/item.html", context)


@login_required
def judge(request):
    participant = Participant.objects.get(user=request.user)
    unjudged_movie = participant.movies.exclude(
        interaction__participant=participant
    ).first()
    if unjudged_movie is None:
        return render(request, "movies/judgeDone.html")
    else:
        return redirect("movie_detail", movie_id=unjudged_movie.movieId)

    # unjudged_movie = None

    # remaining = participant.remaining_judge_actions

    # if remaining == 0:
    #     return render(request, "movies/judgeDone.html")
    # else:
    #     # get the first unjudged movie
    #     for movie in participant.movies.all():
    #         try:
    #             interaction = Interaction.objects.get(
    #                 movie=movie, participant=participant
    #             )
    #         except Interaction.DoesNotExist:
    #             unjudged_movie = movie
    #             break
    #     return redirect("movie_detail", movie_id=unjudged_movie.movieId)


@login_required
def final_ranking(request):
    participant = Participant.objects.get(user=request.user)
    remaining = participant.remaining_judge_actions
    if remaining != 0:
        return render(request, "movies/rankingLocked.html")

    if participant.fully_done:
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

    return render(request, "movies/ranking.html", context)


def handle_404(request, exception):
    return render(request, "movies/404.html", status=404)


def logout_view(request):
    logout(request)
    return redirect("login")
