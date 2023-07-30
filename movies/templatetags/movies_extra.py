from django.template import Library

register = Library()


# -------------- items.html filters --------------#
@register.filter
def get_item(dictionary, key):
    return dictionary[key]


@register.filter
def get_familiarity(dictionary, key):
    return dictionary.get(key, None).familiarity if key in dictionary else None


@register.filter
def get_rating(dictionary, key):
    rating = dictionary.get(key, None).rating if key in dictionary else "N/A"
    if rating == None:
        return "N/A"
    else:
        return rating
    # return dictionary.get(key, None).rating if key in dictionary else None


@register.filter
def get_will(dictionary, key):
    return dictionary.get(key, None).will_to_watch if key in dictionary else None


@register.filter
def get_seen(dictionary, key):
    return dictionary.get(key, None).seen_status if key in dictionary else None


# -------------- item.html filters --------------#
@register.filter
def get_map(movie):
    map_rating = movie.map
    if not map_rating or map_rating == "nan":
        return "N/A"
    else:
        return map_rating


@register.filter
def get_language(movie):
    langs = movie.languages
    if langs and langs != "nan":
        return langs
    else:
        return "N/A"
