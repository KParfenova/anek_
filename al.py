
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import requests
import random
import spacy
from xml.etree import ElementTree

app = Flask(__name__)


def synonims(text):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
	# выставляем и передаем такой заголовок в запросе чтобы притворяться настоящим браузером, а то сайт проверяет
    resp = requests.get(f'https://sinonim.org/s/{text}', headers = headers)
    #print(resp.text)

    soup = BeautifulSoup(resp.text, 'html.parser')

    texts = []

    divtable = soup.find_all('div', {'class': 'outtable'})
    trs = divtable[0].find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) > 1:
            td2 = tds[1].a
            texts.append(td2.text.upper())
			# upper сделал для совместимости формата с твоим другим сайтом где все приходит заглавным

    return [texts]

def get_anekdot(url):
    # 3) get anekdots for this tag (url)
    response = requests.get(url)

    # 4) parse xml with anekdots

    root = ElementTree.fromstring(response.content)

    texts = []
    for child in root[0]:
        if (child.tag == "item"):
            for child2 in child:
                if (child2.tag == "description"):
                    txt = child2.text
                    txt = txt.replace("<br>", "\n")

                    # append txt to the end of array
                    texts.append(txt)

                    #print(txt)
                    #print("------------")


    # 4) get random anek
    r = random.randint(0, len(texts) - 1)
    return texts[r]


@app.route('/', methods=['POST'])
@app.route('/alice/', methods=['POST'])
def respond():
    data = request.json
    tag = data.get('request', {}).get('command', '')

    end_session = False

    if 'выход' in tag:
        response_text = 'Живите долго и процветайте'
        end_session = True
    elif tag:
        #ищем на сайте подобный тэг
        #{tag}
        # 1) read tag from input
        # 2) get URL by tag
        response_text =''
        tags = [
         ['блондинка', "https://www.anekdot.ru/rss/tag/23.xml"],
         ['зверь', "https://www.anekdot.ru/rss/tag/129.xml"],
         ['президент', "https://www.anekdot.ru/rss/tag/8.xml"],
         ['вовочка', "https://www.anekdot.ru/rss/tag/2.xml"],
         ['кот', "https://www.anekdot.ru/rss/tag/55.xml"],
         ['мужчина',"https://www.anekdot.ru/rss/tag/67.xml"],
         ['о жизни',"https://www.anekdot.ru/rss/tag/38.xml"],
         ['политика',"https://www.anekdot.ru/rss/tag/36.xml"],
         ['программист',"https://www.anekdot.ru/rss/tag/26.xml"]
        ]

        url = ''
        for t in tags:
            if t[0] in tag:
                url = t[1]
                break
        if url == '':
            # get synonims
            syns = synonims(tag)
            

            # look for tag in synonims
            for t in tags:
                t_upper = t[0].upper()

                if url != '': break
                for syn in syns:
                    if url != '': break
                    for g in syn:
                        if t_upper == str(g):
                            url = t[1]
                            break

        # ----------
        response_text = ''

        if url == '':
            url = "https://www.anekdot.ru/rss/tag/" + str(random.randint(1, 157))+ ".xml"
            response_text += 'Анекдота на вашу тему не найдено. Вот утешительная шутка: '

        response_text += get_anekdot(url)
        
        
       
    else:
        response_text = 'Приветствую. Какой вам рассказать анекдот?'

    response = {
        'response': {
            'text': response_text,
            'end_session ': end_session
        },
        'version': '1.0'
    }
    return response


app.run(host='0.0.0.0', port=5000, debug=True)
