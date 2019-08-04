from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlencode, parse_qs
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def mainPage():
    if request.method == 'POST':
        search_params= {'first_letters':request.form['first-letters'], 'last_letters':request.form['last-letters'], 'txt_length':request.form['text-length'],'txt_url':request.form['text-url']}
        search_path = urlencode(search_params)
        return redirect(url_for('searchResult', search_path=search_path))
    return render_template('index.html')


@app.route('/results/<path:search_path>/')
def searchResult(search_path):
    search_params=parse_qs(search_path)
    print(search_params)
    first_letters= search_params['first_letters']
    last_letters= search_params['last_letters']
    txt_length= search_params['txt_length']
    txt_url= search_params['txt_url']
    return render_template('results.html',first_letters=first_letters,last_letters=last_letters,txt_length=txt_length,txt_url=txt_url)


if __name__ == '__main__':
    app.run(debug=True)
