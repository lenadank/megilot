from urllib.parse import parse_qs, urlencode
import os
from werkzeug.utils import secure_filename
import uuid
import pickle

from flask import redirect, render_template, request, url_for, session

from megilot import app
from megilot import searchUtils as sutils
from megilot import fileUtils


@app.route('/', methods=['GET'])
def mainPage():
    fileUtils.clear_old_texts()  # remove all text files in texts\uploads
    create_id()
    return render_template('index.html', is_main=True)


@app.route('/searching', methods=['POST'])
def search():

    if 'search_id' in session:
        print('search id found '+session.get('search_id'))
        pickled_res_path = os.path.join(
            app.config['TEXT_UPLOADS'], session.get('search_id'), 'results.pickle')
        if os.path.exists(pickled_res_path):
            try:
                os.unlink(pickled_res_path)
                print('deleted previous pickle')
            except Exception as e:
                print(e)
                print('couldnt delete pickled results')
                return redirect(url_for('mainPage'))

        if request.files:
            print('files exist in request')
        # Make sure there's a directory with session_id as it's name.
            search_path = os.path.join(
                app.config['TEXT_UPLOADS'], session.get('search_id'))
            if not os.path.exists(search_path):
                try:
                    os.mkdir(search_path)
                except OSError:
                    print("Creation of the directory %s failed" %
                            search_path)
                    return redirect(url_for('mainPage'))
                else:
                    print("Successfully created the directory %s " %
                            search_path)

            # upload files
            uploaded_files = request.files.getlist("files")
            filenames = []
            for f in uploaded_files:

                if f.filename == "":
                    print('file must have a filename')
                    return redirect(url_for('mainPage'))

                if not fileUtils.allowed_file(f.filename):
                    print('file extentention not allowed. only txt.')
                    return redirect(url_for('mainPage'))

                filename = secure_filename(f.filename)
                f.save(os.path.join(search_path, filename))
                filenames.append(filename)

    else:
        print('search_id wasn\'t found while searching')
        return redirect(url_for('mainPage'))

    search_params = {
        'letters': request.form['letters'], 'txt_length': request.form['text-length'], 'search_id': session.get('search_id', None)}
    if 'search_params' in session:
        session['search_params'] = search_params
        session.modified=True
    else:
        session['search_params'] = search_params

    return redirect(url_for('searchResult'))


@app.route('/results', methods=['GET'])
def searchResult():

    path = os.path.join(app.config['TEXT_UPLOADS'], session.get('search_id'))
    texts = fileUtils.texts_from_dir(path)

    if 'search_params' in session:
        search_params = session.get('search_params', None)
        print(search_params)
    else:
        print('search params not found in session')
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
        print('texts still exist in directory')
        # return list of all txt files in the url
        pickled_res_path = os.path.join(path, 'results.pickle')
        if os.path.exists(pickled_res_path):
            print("results already exist as pickle")
            try:
                pickle_in = open(pickled_res_path,'rb')
            except Exception as e:
                print(e)
                print('couldnt open pickled res')
                pickle_in.close()
                return(redirect(url_for('mainPage'))) 
            else:
                results = pickle.load(pickle_in)
                pickle_in.close()
                print('succefully loaded pickled results')
        else:
            print("results found for first time:")
            results = sutils.search_txt(texts, strings_list, window_l, window_r)
            if results==None:
                return render_template('results.html', letters=strings, txt_length=txt_length, title='Search Results', header="תוצאות חיפוש", result=results, is_main=False, filenames=None, cur_page = None)
            try:
                pickle_out = open(pickled_res_path, 'wb')
            except Exception as e:
                print(e)
                print('couldnt load pickled res')
                pickle_out.close()
                return(redirect(url_for('mainPage')))
            else:
                pickle.dump(results, pickle_out)
                pickle_out.close()
                print('succefuly pickled result')
                print("pickle exists is:")
                print(os.path.exists(pickled_res_path))

        filenames = sorted(list(results.keys()))
        page = request.args.get('page', filenames[0], type=str)
        cur_res = results.get(page)
        print(cur_res)
        
        return render_template('results.html', letters=strings, txt_length=txt_length, title='Search Results', header="תוצאות חיפוש", result=cur_res, is_main=False,  filenames=filenames, cur_page = page)
    else:
        print('re-enter text - session out. make a flush here Anat!')
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