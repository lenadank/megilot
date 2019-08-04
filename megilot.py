from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlencode, parse_qs
app = Flask(__name__)

lines = [{'title': "Hey", 'text': "The well-documented monihvkhvkhdvhckvsdkcvdskjcvsdjlvcdljhcvdlcvhdcjlvdsljcvdsjcvsdhcvsdjlvcdschvsljcvlhsdvcjlsdvcdsvcjlvdscjvdscljvdschjsvdcljsvhsvlchvsdljvdscljvcjsdvclsdvcljsvdcjhvscljshtor backs into the incomplete bed. What if the flashy quarter ate the dress?"}, {'title': "How", 'text': "The well-documented monitor backs into the incomplete bed. What if the flashy quarter ate the dress?"}, {'title': "Hi", 'text': "The well-documented monitor backs into the incomplete bed. What if the flashy quarter ate the dress?"},
         {'title': "Bye", 'text': "The well-documented monitor backs into the incomplete bed. What if the flashy quarter ate the dress?"}, {'title': "Bay", 'text': "The well-documented monitor backs into the incomplete bed. What if the flashy quarter ate the dress?"}, {'title': "Bow", 'text': "The well-documented monitor backs into the incomplete bed. What if the flashy quarter ate the dress?"}]


@app.route('/searching', methods=['POST'])
def search():
    if request.method == 'POST':
        search_params = {'first_letters': request.form['first-letters'], 'last_letters': request.form['last-letters'],
                         'txt_length': request.form['text-length'], 'txt_url': request.form['text-url']}
        search_path = urlencode(search_params)
        return redirect(url_for('searchResult', search_path=search_path))


@app.route('/', methods=['GET'])
def mainPage():
    return render_template('index.html')


@app.route('/results/<path:search_path>/', methods=['GET'])
def searchResult(search_path):
    search_params = parse_qs(search_path)
    print(search_params)
    first_letters = search_params['first_letters'][0]
    last_letters = search_params['last_letters'][0]
    txt_length = search_params['txt_length'][0]
    txt_url = search_params['txt_url'][0]
    return render_template('results.html', first_letters=first_letters, last_letters=last_letters, txt_length=txt_length, txt_url=txt_url, title='Search Results', header="תוצאות חיפוש", lines=lines)


if __name__ == '__main__':
    app.run(debug=True)
