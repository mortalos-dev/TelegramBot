# script file with handling DB request
# in test variant use python dict and random choise to get from DB

from random import choice
from typing import NamedTuple


available_categories = ["топ", "по жанрам", "адаптивное"]


class DBEntry(NamedTuple):
    """Class container of DB Entry"""
    tconst: str
    primaryTitle: str
    originalTitle: str
    description: str
    isAdult: bool
    startYear:  int
    endYear: int
    genres: str


MOVIES_DICT = {
    1: DBEntry('tt100500', '100500Film', '100500Filme', 'smth about jokes', False, 1980, 1988, 'Comedy,Action'),
    2: DBEntry('tt666', '666Film', '666Filme', 'smth about horrors', True, 1990, 1998, 'Horror,Thriller'),
    3: DBEntry('tt69', '69Film', '69Filme', 'smth about adults', True, 2008, 2018, 'Adult,Action')
    }

SERIES_DICT = {
    1: DBEntry('tt600', '600Film', '600Filme', 'smth about heroes', False, 1981, 1982, 'Comedy,Action'),
    2: DBEntry('tt700', '700Film', '700Filme', 'smth about superheroes', False, 2009, 2019, 'Heroic,Thriller'),
    3: DBEntry('tt800', '800Film', '800Filme', 'smth about clowns', True, 2011, 2021, 'Horror,Action')
    }


available_genres = ["боевики", "драма", "комедия", "триллер", "ужасы", "приключения"]


GENRE_TRANSLATION_DICT = {"боевики": "action", "драма": "drama", "комедия": "comedy",
                          "триллер": "Thriller", "ужасы": "Horror", "приключения": "adventure"

}


async def get_genre_movies(genre: str):
    items = []
    for value in MOVIES_DICT.values():
        for item in value.genres.split(','):
            if item.lower() == GENRE_TRANSLATION_DICT[genre.lower()]:
                items.append(value)
                break
    if len(items) == 0:
        return None
    else:
        return choice(items)


async def get_genre_series(genre: str):
    items = []
    for value in SERIES_DICT.values():
        for item in value.genres.split(','):
            if item.lower() == GENRE_TRANSLATION_DICT[genre.lower()]:
                items.append(value)
                break
    if len(items) == 0:
        return None
    else:
        return choice(items)


async def get_top_movies():
    item = choice(list(MOVIES_DICT.keys()))
    return MOVIES_DICT[item]


async def get_top_series():
    item = choice(list(SERIES_DICT.keys()))
    return SERIES_DICT[item]


async def get_adaptive_movies(user_id: int):
    # method to
    pass


async def get_adaptive_series(user_id: int):
    pass


async def get_movie_data(*categories):
    data = None
    if categories[0] == available_categories[0]:
        data = await get_top_movies()
    elif categories[0] == available_categories[1]:
        data = await get_genre_movies(categories[1])
    elif categories[0] == available_categories[2]:
        pass
    else:
        raise Exception('Bad category')
    if data is None:
        raise Exception('Nothing found in dict')

    return data


async def get_series_data(*categories):
    data = None
    if categories[0] == available_categories[0]:
        data = await get_top_series()
    elif categories[0] == available_categories[1]:
        data = await get_genre_series(categories[1])
    elif categories[0] == available_categories[2]:
        pass
    else:
        raise Exception('Bad category')
    if data is None:
        raise Exception('Nothing found in dict')

    return data
