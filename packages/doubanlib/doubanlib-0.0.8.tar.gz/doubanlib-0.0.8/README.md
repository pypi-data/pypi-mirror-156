## Introduce

This is an api tool for DouBan movie(https://movie.douban.com/),you can get the basic information from movies.

## Usage

an example of usage

```
from doubanlib.movies import MovieInfo

# Doctor Strange in the Multiverse of Madness which id is 30304994(https://movie.douban.com/subject/30304994).
obj = MovieInfo(30304994)

# Print the Description of the movie.
print('Description:{}'.format(obj.description))
```

complete usage

```
from doubanlib.movies import MovieInfo

# Doctor Strange in the Multiverse of Madness which id is 30304994(https://movie.douban.com/subject/30304994).
obj = MovieInfo(30304994)

# Print all the information of the movie.
print(
    'ID:{}\nName:{}\nChinese_Name:{}\nYear:{}\nGenre:{}\nRegions:{}\nLanguage:{}\nRating:{}\nVotes:{}\nLength_Movie:{}\nDirectors:{}\nAlias:{}\nImage:{}\nDate_Published:{}\nActors:{}\nDescription:{}'
    .format(obj.m_id, obj.name, obj.chineseName, obj.year, obj.genre,
            obj.regions, obj.languages, obj.rating, obj.votes, obj.length_movie,
            obj.directors, obj.alias, obj.image, obj.pubDate, obj.actors,
            obj.actors, obj.description))
```