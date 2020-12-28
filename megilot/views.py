from urllib.parse import parse_qs, urlencode
import os
from werkzeug.utils import secure_filename
import uuid
import pickle
import sys
import glob
from flask import redirect, render_template, request, url_for, session, flash
import shutil
from megilot import app
from megilot import searchUtils as sutils
from megilot import fileUtils
import csv



def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


def get_bible_files(folder):
    return glob.glob("%s/*.txt" % folder)


@app.route('/', methods=['GET'])
def mainPage():
    fileUtils.clear_old_texts()  # remove all text files in texts\uploads
    create_id()
    return render_template('index.html', last_updated = dir_last_updated('megilot/static'), is_main=True)

@app.route('/about', methods=['GET'])
def aboutPage():
    return render_template('about.html',  is_main=True)

@app.route('/contact', methods=['GET'])
def contactPage():
    return render_template('contact.html', is_main=True)

@app.route('/usage', methods=['GET'])
def usagePage():
    return render_template('usage.html', is_main=True)


@app.route('/searching', methods=['POST'])
def search():

    if 'search_id' in session:
        pickled_res_path = os.path.join(
            app.config['TEXT_UPLOADS'], session.get('search_id'), 'results.pickle')
        if os.path.exists(pickled_res_path):
            try:
                os.unlink(pickled_res_path)
            except Exception as e:
                print("failed unlinking pickled_res_path")
                print(e)
                flash("Something went wrong. Sorry.", "danger")
                return redirect(url_for('mainPage'))

        #if request.files:
        # Make sure there's a directory with session_id as it's name.
        search_path = os.path.join(
            app.config['TEXT_UPLOADS'], session.get('search_id'))
        if not os.path.exists(search_path):
            try:
                os.mkdir(search_path)
            except OSError as e:
                print("Can't Make directory search_path")
                print(e)
                flash("Something went wrong. Sorry.", "danger")
                return redirect(url_for('mainPage'))

            # upload files
        filenames = []
        if "input_files" in request.form:
            app.config["input_files"] = request.form["input_files"]
        elif "input_files" not in app.config:
            app.config["input_files"] = "תנ״ך"
        if app.config["input_files"] == "תנ״ך":
            uploaded_files = get_bible_files(os.path.join(app.config['TEXT_UPLOADS'], "../bible"))
            for f in uploaded_files:
                simple_name = os.path.join(os.path.basename(os.path.dirname(f)), os.path.basename(f))
                filename = secure_filename(simple_name)
                shutil.copyfile(f, (os.path.join(search_path, filename)))
                filenames.append(filename)
        else:
            uploaded_files = request.files.getlist("files")
            for f in uploaded_files:
                filename = secure_filename(f.filename)
                f.save(os.path.join(search_path, filename))
                filenames.append(filename)

    else:
        flash("Something went wrong. Sorry.", "danger")
        return redirect(url_for('mainPage'))

    search_params = {
        'letters': request.form['letters'], 'txt_length': request.form['minRow']+"-"+request.form['maxRow'], 'search_id': session.get('search_id', None)}
    if 'search_params' in session:
        session['search_params'] = search_params
        session.modified = True
    else:
        session['search_params'] = search_params

    return redirect(url_for('searchResult'))

def save_results_to_csv(results, csv_file_name):
    with open(csv_file_name, mode='w', encoding="utf8") as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for f, lines in results.items():
            for i,line in enumerate(lines[0]):
                for l in line:
                    l = ["*" + x + "*" if i%2 ==1 else x for i, x in enumerate(l) ]
                    verse_title = "" if lines[2] is None else lines[2][i]
                    results_writer.writerow([f, verse_title, " ".join(l).replace("\r\n", " ").replace("\n", " ")])



@app.route('/results', methods=['GET'])
def searchResult():

    path = os.path.join(app.config['TEXT_UPLOADS'], session.get('search_id'))
    texts = fileUtils.texts_from_dir(path)

    if 'search_params' in session:
        search_params = session.get('search_params', None)
    else:
        flash("Something went wrong. Sorry.", "danger")
        return redirect(url_for('mainPage'))

    # extract letters entered into a list, each row is a separate item.
    strings = search_params.get('letters')
    strings_list = strings.split('\r\n')
    strings_list = sutils.strip_strings(strings_list)

    # extract text length from user input
    txt_length = search_params.get('txt_length')
    window = txt_length.split('-')
    window_l = int(window[0])
    window_r = int(window[1])

    if texts:
        # return list of all txt files in the url
        pickled_res_path = os.path.join(path, 'results.pickle')
        csv_results_path = os.path.join(path, 'results.csv')
        if os.path.exists(pickled_res_path):
            try:
                pickle_in = open(pickled_res_path, 'rb')
            except Exception as e:
                print("Failed opening pickled_res_path for reading")
                print(e)
                flash("Something went wrong. Sorry.", "danger")
                pickle_in.close()
                return(redirect(url_for('mainPage')))
            else:
                results = pickle.load(pickle_in)
                pickle_in.close()
        else: #results found for the first time (no pickled results exist yet)
            results = sutils.search_txt(
                texts, strings_list, window_l, window_r)
            if results == None:
                return render_template('results.html', letters=strings, min_row_len = window[0], max_row_len=window[1],
                                       title='Search Results', txt_length=txt_length, header="תוצאות חיפוש", result=results,
                                       is_main=False, filenames=None, cur_page=None, message="לא נמצאו תוצאות")
            try:
                pickle_out = open(pickled_res_path, 'wb')
            except Exception as e:
                print("Failed opening pickled_res_path for writing")
                print(e)
                flash("Something went wrong. Sorry.", "danger")
                pickle_out.close()
                return(redirect(url_for('mainPage')))
            else: #pickle the new results
                pickle.dump(results, pickle_out)
                pickle_out.close()
        filenames = sorted(list(results.keys()))
        page = request.args.get('page', filenames[0], type=str)
        cur_res = results.get(page)
        #handle index
        for text in texts:
            if text.endswith("index.txt"):
                headers = texts[text].split("\n")
                index = []
                for i in cur_res[2]:
                    index.append([headers[x] for x in i])
                cur_res = (cur_res[0], cur_res[1], index)
                break
        else:
            cur_res = (cur_res[0], cur_res[1], None)
        results[page] = cur_res
        save_results_to_csv({page: cur_res}, csv_results_path)
        csv_results_path = "../static/" + csv_results_path.split("static/")[1]
        return render_template('results.html', letters=strings,
                               min_row_len = window[0], max_row_len=window[1], txt_length=txt_length, title='Search Results',
                               header="תוצאות חיפוש", result=cur_res,
                               is_main=False,  filenames=filenames, cur_page=page, output_csv_file=csv_results_path)
    else:
        flash("Oops, you're session timed-out. Please re-enter texts and search parameters", "danger")
        return(redirect(url_for('mainPage')))


"""Create new search id and store it in the current session."""


def create_id():
    id = str(uuid.uuid1())
    session.pop('search_params', None)
    if 'search_id' in session:
        session['search_id'] = id
        session.modified = True
    else:
        session['search_id'] = id
