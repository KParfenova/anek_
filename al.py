from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import random
# import spacy
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
    if len(divtable) == 0:
        return 0
    trs = divtable[0].find_all('tr')
    
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) > 1:
            td2 = tds[1].a
            texts.append(td2.text.upper())
    

    return [texts]

def read_tag():
    tags = []
    f = open("tags.txt", "r")
    n = f.readline()
    n = n[:len(n)-1]
    url = ''

    for i in range(0, int(n), 2):
        t = f.readline()
        t= t[:len(t)-1]
        urla = f.readline()
        urla = urla[:len(urla)-1]
        tags.append([t, urla])
    return tags

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

    if len(texts) == 0:
        return 0
    # 4) get random anek
    r = random.randint(0, len(texts) - 1)
    return texts[r]


def make_response(data):
    tag = data.get('request', {}).get('command', '')

    end_session = False

    if 'выход' in tag:
        response_text = 'Живите долго и процветайте'
        end_session = True
    elif 'помощь' in tag:
        response_text = 'Напишите тему анекдота, который вы хотите услышать. Например: политика'
    elif 'что ты умеешь' in tag:
        response_text = 'Я могу рассказывать анекдоты на разные темы. Например про Штирлица.'
        
    elif tag:
        #ищем на сайте подобный тэг
        #{tag}
        # 1) read tag from input
        # 2) get URL by tag
        
        tags = read_tag()
        url = ''

        # получаем синонимы для темы и ищем совпадение синонима с тегом
        # get synonims

        response_text = ''

        rand_txt = ['Анекдота на вашу тему не найдено. Вот утешительная шутка: ',
                   'Увы, я не могу найти анекдот на эту тему. Но могу рассказать другой: ',
                   f'Анекдота на тему {tag} найти не удалось. Могу предложить такой: ',
                   f'По теме {tag} анекдотов нет. Как насчет такого: ']

        for t in tags:
            if t[0] == tag.upper():
                url = t[1]
                break
        # look for tag in synonims
        if url == '':
            syns = synonims(tag.upper())
            if syns == 0:
                url = "https://www.anekdot.ru/rss/tag/" + str(random.randint(1, 157))+ ".xml"
                response_text += rand_txt[random.randint(0, len(rand_txt)-1)]
            else:
                for t in tags:
                    t_upper = t[0]
                    for syn in syns:
                        if url != '': break
                        for g in syn:
                            if t_upper == str(g):
                                url = t[1]
                                break
        

        

        # ----------
        
        if url == '':
            url = "https://www.anekdot.ru/rss/tag/" + str(random.randint(1, 157))+ ".xml"
            response_text += rand_txt[random.randint(0, len(rand_txt)-1)]

        response_text += get_anekdot(url)
        
       
    else:
        response_text = 'Приветствую. Какой вам рассказать анекдот? \n Для помощи введите: Помощь \n Чтобы узнать о навыке: Что ты умеешь? \n Для выхода из навыка: Выход'

    response = {
        'response': {
            'text': response_text,
            'end_session ': end_session
        },
        'version': '1.0'
    }
    return response



@app.route('/', methods=['POST'])
@app.route('/alice/', methods=['POST'])
def respond():
    data = request.json
    return make_response(data)


def handler(event, context):
    return make_response(data=event)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
