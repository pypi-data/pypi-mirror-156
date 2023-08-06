# DouBanLib


# Usage
```
from doubanlib.movie import Movie

movie = Moive(1292220)
print(
    '豆瓣ID:{}\nIMDB：{}\n电影名称：{}\n中文名称：{}\n生产时间：{}\n电影类型：{}\n制片地区：{}\n电影语言：{}\n电影评分：{}\n投票人数：{}\n电影片长：{}\n导演列表：{}\n电影别名：{}\n海报地址：{}\n出版日期：{}\n演员列表：{}\n电影介绍：{}'
    .format(movie.m_id, movie.imdb, movie.name, movie.chineseName, movie.year,
            '/'.join(movie.genre), '/'.join(movie.regions),
            '/'.join(movie.language), movie.rating, movie.votes,
            movie.length_movie, '/'.join(movie.directors),
            '/'.join(movie.alias), movie.image, '/'.join(movie.pubDate),
            '/'.join([i[1] for i in movie.actors]),
            movie.description.strip().replace(' ', '').replace('\n', '')))
```

