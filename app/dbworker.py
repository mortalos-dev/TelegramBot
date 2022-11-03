# script file with handling DB request
# in test variant use random choise to get from DB

from random import choice
from dataclasses import dataclass
import sqlite3
import os


available_categories = ["топ", "по жанрам", "адаптивное"]
available_genres = ["боевики", "драма", "комедия", "триллер", "ужасы", "приключения"]

dirname = os.path.dirname(__file__)
PATH_DB = os.path.join(dirname, 'db\MoviesSeriesGenres.db')
USERS_DB = os.path.join(dirname, 'db\BotUsersDB.db')
FETCH_SIZE = 100


@dataclass
class DBEntry:
    """Class container of DB Entry"""
    tconst: str
    primaryTitle: str
    originalTitle: str
    description: str
    isAdult: int
    startYear:  int
    endYear: int
    genres: str
    picLink: str
    trailerLink: str
    imdbRating: float
    actors: str
    directors: str
    runtimeMinutes: int


GENRE_TRANSLATION_DICT = {"боевики": "Action", "драма": "Drama", "комедия": "Comedy",
                          "триллер": "Thriller", "ужасы": "Horror", "приключения": "Adventure"
                          }


async def get_genre_movies(genre: str):
    select_query = '''
        SELECT DISTINCT
            movies.tconst, 
            movies.primaryTitle, 
            movies.originalTitle,
            movies.description,
            movies.isAdult,
            movies.startYear,
            movies.endYear,
            movies.genres,
            movies.linkToPic,
            movies.linkToTrailer,
            movies.averageRating,
            movies.actors,
            movies.directors,
            movies.runtimeMinutes
        FROM
            movies
        INNER JOIN
            genres 
        ON
            movies.tconst = genres.tconst
        WHERE
            genres.genre = ?
        ORDER BY
            RANDOM()
        LIMIT 1
        ;
        '''

    with sql_connection(PATH_DB) as con:
        data = execute_read_query_args(con, select_query, [GENRE_TRANSLATION_DICT[genre.lower()]])
        film_data = DBEntry(*data[0])
        return film_data


async def get_genre_series(genre: str):
    select_query = '''
        SELECT DISTINCT 
            series.tconst, 
            series.primaryTitle, 
            series.originalTitle,
            series.description,
            series.isAdult,
            series.startYear,
            series.endYear,
            series.genres,
            series.linkToPic,
            series.linkToTrailer,
            series.averageRating,
            series.actors,
            series.directors,
            series.runtimeMinutes
        FROM 
            series
        INNER JOIN 
            genres 
        ON 
            series.tconst = genres.tconst
        WHERE 
            genres.genre = ?
        ORDER BY
            RANDOM()
        LIMIT 1
        ;
        '''

    with sql_connection(PATH_DB) as con:
        data = execute_read_query_args(con, select_query, [GENRE_TRANSLATION_DICT[genre.lower()]])
        film_data = DBEntry(*data[0])
        return film_data


async def get_top_movies():
    select_query = '''
            SELECT DISTINCT 
                tconst, 
                primaryTitle, 
                originalTitle,
                description,
                isAdult,
                startYear,
                endYear,
                genres,
                linkToPic,
                linkToTrailer,
                averageRating,
                actors,
                directors,
                runtimeMinutes
            FROM 
                movies
            ORDER BY
                RANDOM()
            LIMIT 1
            ;
            '''

    with sql_connection(PATH_DB) as con:
        data = execute_read_query(con, select_query)
        # item = choice(data)
        film_data = DBEntry(*data[0])
        return film_data


async def get_top_series():
    select_query = '''
        SELECT DISTINCT 
            tconst, 
            primaryTitle, 
            originalTitle,
            description,
            isAdult,
            startYear,
            endYear,
            genres,
            linkToPic,
            linkToTrailer,
            averageRating,
            actors,
            directors,
            runtimeMinutes
        FROM 
            series
        ORDER BY
            RANDOM()
        LIMIT 1
        ;
        '''

    with sql_connection(PATH_DB) as con:
        data = execute_read_query(con, select_query)
        film_data = DBEntry(*data[0])
        return film_data


async def get_adaptive_movies(user_id: int):
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


async def user_data_update(user_id: int, tconst: str, like: int):
    write_query = '''
        INSERT INTO watches 
            (userid, tconst, choose) 
        VALUES 
            (?, ?, ?);
        '''
    check_query = '''
        SELECT DISTINCT
            userid
        FROM 
            users
        ;
    '''
    add_user_query = '''
        INSERT INTO users
            userid = ?
        ;
    '''
    args = (user_id, tconst, like)
    with sql_connection(USERS_DB) as con:
        users_raw = execute_read_query(con, check_query)
        users = (item[0] for item in users_raw)
        if user_id not in users:
            await execute_query_with_agrs(con, write_query, user_id)
        await execute_query_with_agrs(con, write_query, args)


def sql_connection(file_name):
    try:
        con = sqlite3.connect(file_name)
        return con
    except BaseException as e:
        print(f"The error '{e}' occurred in DB source file - {file_name}")
        con.close()


async def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except BaseException as e:
        print(f"The error in query '{e}' occurred")


async def execute_query_with_agrs(connection, query, args):
    cursor = connection.cursor()
    try:
        cursor.execute(query, args)
        connection.commit()
    except BaseException as e:
        print(f"The error in query with args '{e}' occurred")


async def execute_query_many(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.executemany(query, data)
        connection.commit()
    except BaseException as e:
        print(f"The error in query_many '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except BaseException as e:
        print(f"The error '{e}' while read sql occurred")


def execute_read_query_args(connection, query, args):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, args)
        result = cursor.fetchall()
        return result
    except BaseException as e:
        print(f"The error '{e}' while read sql occurred")


def execute_read_query_many(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchmany(size=FETCH_SIZE)
        return result
    except BaseException as e:
        print(f"The error '{e}' while read sql occurred")


