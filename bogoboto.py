import requests
import time
import random
from bs4 import BeautifulSoup as bs

class request_bogo():
    url = "https://zipbogo.net/cdsb/login_process.php"
    new_movie_url = "https://zipbogo.net/cdsb/board.php?board=newmovie&category=&search=&keyword=&recom=&page=%d"

    headers = {
        'origin': 'https://zipbogo.net',
        'referer': 'https://zipbogo.net/',
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4,fr;q=0.2,ja;q=0.2",
        'referer': "https://zipbogo.net/cdsb/login_process.php",
        'cache-control': "max-age=0",
        'content-length': '61',
        'content-type': 'application/x-www-form-urlencoded',
        #    'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        'cache-control': "no-cache"
    }

    payload = "mode=login&kinds=outlogin&user_id={id}&passwd={passwd}"

    def __init__(self, id, passwd):
        self.id = id
        self.passwd = passwd
        self.payload = self.payload.format_map({"id": id, "passwd": passwd})

    def doLogin(self):
        s = requests.Session()
        s.headers = self.headers
        Resopnse = s.post(self.url, data=self.payload)

        if Resopnse.ok:
            self.session = s

            del self.headers['cache-control']
            del self.headers['content-length']
            del self.headers['content-type']
            del self.headers['origin']
            self.headers['referer'] = "https://zipbogo.net/cdsb/login_process.php"

        return Resopnse

    def getMovieList(self, page_num):
        print("start crawlling page_num : %d" % page_num)
        result = list()

        target = self.new_movie_url % page_num
        Response = self.session.get(target)

        if Response.ok == False:
            return []

        soup = bs(Response.text, 'html.parser')

        # 게시판 마지막 번호 체크
        if "alert" in soup.find_all('script')[-1].text:
            return ["EOF"]

        articles = soup.find("tbody", class_="num").find_all("tr")

        if not isinstance(articles, list):
            return []

        for article in articles[2:]:
            docs = article.find_all("td")
            try:
                index_num = int(docs[0].text)
                promotion = int(docs[5].text)
                subject =  docs[2].a.text
                url =  "https://zipbogo.net/cdsb/" + docs[2].a["href"].replace("amp;", "")

                comment_string = docs[2].a.text.split()[-1][1:-1]
                if comment_string.isdigit():
                    comment_num = int(comment_string)
                else:
                    comment_num = 0

                result.append([index_num, promotion, comment_num, subject, url])
            except:
                continue

        return result

if __name__ == "__main__":
    # TODO : input account information
    user_id = "user_id"
    password = "password"

    bogo = request_bogo(user_id, password)
    ret = bogo.doLogin()

    if ret.ok and "로그인하셨습니다" in ret.text:
        print("Login success")
    else:
        print("Login failure")

    # result = bogo.getMovieList(1)
    # investigate each article from 0 to 2000 until EOF
    for num in range(0, 2000):
        result = bogo.getMovieList(num)
        if len(result) == 0:
            continue
        elif "EOF" in result[0]:
            break

        for page_result in result:
            print("subject: " + page_result[3][0:64])

        time.sleep(1 + random.random() * 1)
