from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlencode, parse_qs
from searchUtils import *
from functools import reduce
app = Flask(__name__)


@app.route('/searching', methods=['POST'])
def search():
        if request.method == 'POST':
                search_params = {'letters': request.form['letters'], 'txt_length': request.form['text-length'],
                                'txt_url': request.form['text-url'], 'language': request.form['language']}
                search_path = urlencode(search_params)
                return redirect(url_for('searchResult', search_path=search_path))


@app.route('/', methods=['GET'])
def mainPage():
        return render_template('index.html', is_main=True)


@app.route('/results/<path:search_path>/', methods=['GET'])
def searchResult(search_path):
        search_params = parse_qs(search_path)

        #extract letters entered into a list, each row is a separate item.
        letters = search_params['letters'][0]
        letters_list = letters.split('\r\n')
        #extract language from user input
        language = search_params['language'][0]
        #extract text length from user input
        txt_length = search_params['txt_length'][0]
        window = txt_length.split('-')
        window_l = int(window[0])
        window_r = int(window[1])
        #extract url from user input
        txt_url = search_params['txt_url'][0]
        #return list of all txt files in the url
        texts = texts_from_url(txt_url, language)
        results = search_txt(texts,letters_list, window_l, window_r)
        total_results_num = reduce(lambda count, l: count + len(l), results,0)
        return render_template('results.html', letters=letters, txt_length=txt_length, txt_url=txt_url, title='Search Results', header="תוצאות חיפוש", results=results , is_main=False, results_num = total_results_num)


if __name__ == '__main__':
        app.run(debug=True)
