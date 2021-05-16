import os
import requests
from pyquery import PyQuery as pq
import time

"""
简单爬虫
爬取豆瓣电影 TOP250 页面，含电影海报
带页面缓存
"""


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.other = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0
        self.count = 0


def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/89.0.4389.128 '
                      'Safari/537.36',
        # 'Cookie': secret.cookie,
    }
    r = requests.get(url, headers=headers)
    return r


def cache(url, filename):
    """
    缓存
    """
    # 建立 cache 文件夹
    folder = 'cache'
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        # 读取缓存
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中
        r = get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def cached_page(url):
    filename = '{}.html'.format(url.split('=', 1)[-1])
    page = cache(url, filename)
    return page


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    # 小作用域变量可用单字符
    m = Movie()
    m.name = e('.title').text()
    m.other = e('.other').text()
    m.score = e('.rating_num').text()
    m.quote = e('.inq').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.pic').find('em').text()
    m.count = list(e('.star span').items())[3].text()

    return m


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        cache(m.cover_url, filename)


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    page = cached_page(url)
    e = pq(page)
    items = e('.item')
    movies = [movie_from_div(i) for i in items]
    save_cover(movies)
    return movies


def main():
    start = time.time()

    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)
        print('top250 movies', movies)

    end = time.time()
    # 计算爬取时间
    print('duration', end-start)


if __name__ == '__main__':
    main()
