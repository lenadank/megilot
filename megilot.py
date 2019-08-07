from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlencode, parse_qs
from searchUtils import *
app = Flask(__name__)


@app.route('/searching', methods=['POST'])
def search():
    if request.method == 'POST':
        search_params = {'first_letters': request.form['first-letters'], 'last_letters': request.form['last-letters'],
                         'txt_length': request.form['text-length'], 'txt_url': request.form['text-url'], 'language': request.form['language']}
        search_path = urlencode(search_params)
        return redirect(url_for('searchResult', search_path=search_path))


@app.route('/', methods=['GET'])
def mainPage():
    return render_template('index.html')


@app.route('/results/<path:search_path>/', methods=['GET'])
def searchResult(search_path):
    search_params = parse_qs(search_path)
    first_letters = search_params['first_letters'][0]
    last_letters = search_params['last_letters'][0]
    language = search_params['language'][0]
    txt_length = search_params['txt_length'][0]
    window=txt_length.split('-')
    window_l=int(window[0])
    window_r=int(window[1])
    txt_url = search_params['txt_url'][0]
    texts= texts_from_url(txt_url,language)
    results = search_txt(texts,first_letters,last_letters,window_l,window_r)
    return render_template('results.html', first_letters=first_letters, last_letters=last_letters, txt_length=txt_length, txt_url=txt_url, title='Search Results', header="תוצאות חיפוש", results=results)


if __name__ == '__main__':
    app.run(debug=True)
