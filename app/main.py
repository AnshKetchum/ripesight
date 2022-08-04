# import requirements needed
# pip install firebase_admin
from audioop import add
from flask import Flask, render_template

from flask import send_from_directory
from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template
from url_utils import get_base_url
import os
import torch
import numpy as np
import json
from flask import jsonify




import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("/ripesight-firebase-adminsdk-8dne2-7a07c80392.json")
firebase_admin.initialize_app(cred)

mainref = db.reference("https://ripesight-default-rtdb.firebaseio.com")

def sendToDatabase(filename):
    pass

titles = []
descs = []
ratings = []
urls = []
data_list = []
fileListNames = ["appleRecipeData.txt","bananaRecipeData.txt","bell pepperRecipeData.txt","carrotRecipeData.txt","cornRecipeData.txt","cucumberRecipeData.txt","gourdRecipeData.txt","kiwiRecipeData.txt","onionRecipeData.txt","orangeRecipeData.txt","potatoRecipeData.txt","tomatoRecipeData.txt"]

for i in fileListNames:
    with open("static/assets/recipes/{}".format(i),"r") as file:
        data_list.append(json.loads(file.read()))

for x in data_list:
    for y in x:
        titles.append(y[0])
        descs.append(y[1])
        ratings.append(y[2])
        urls.append(y[3])


#with open('rec.json') as f:
#   important = json.load(f)
#list(important.keys())
#important['Ripe Apple']['urls']

#json.dump(data_list)

titles = json.dumps(titles);
descs = json.dumps(descs);
ratings = json.dumps(ratings);
urls = json.dumps(urls);

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 9999
base_url = get_base_url(port)

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['SECRET_KEY'] = os.urandom(24)


# UNCOMMENT THIS EVENTUALLY
model = torch.hub.load("ultralytics/yolov5", "custom", path = 'best.pt', force_reload=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route(f'{base_url}', methods=['GET', 'POST'])
def home():

    #Delete any files in the uploads directory
    print("METHOD RUN")
    print(request)
    print(request.method)

    for filename in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'image-upload')):
        print(f'Deleting {filename}')
        os.remove((os.path.join(app.config['UPLOAD_FOLDER'], 'image-upload' , filename)))
    if request.method == 'POST':
        print('in post')
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print('file', request.files)
        print('file', request.files['file'])
        print("file name: ",file.filename)

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            print(file.filename)
            filename = secure_filename(file.filename)

            print("after secure_filename: ", filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],'image-upload' , filename))
            print("after save: ", filename)

            print('saving at: ', os.path.join(app.config['UPLOAD_FOLDER'], 'image-upload' , filename))

            print('uploading file ... 107')
            return redirect(url_for('uploaded_file',filename=filename))
    return render_template('index.html')

@app.route(f'{base_url}/rec')
def rec():
    print('recipes.html load')
    print('line 112')
    return render_template('recipes.html')

@app.route(f'{base_url}/uploads/<filename>', methods=['GET', 'POST'])# <filename>
def uploaded_file(filename):

    print('file',filename)
    here = os.getcwd()

    print('looking for image')
    image_path = os.path.join(here, app.config['UPLOAD_FOLDER'], 'image-upload' , filename)
    print('path', image_path, filename)
    print('Getting results')
    results = model(image_path, size=416)
    print(results)
    if len(results.pandas().xyxy) > 0:
        print('results')
        results.print()
        save_dir = os.path.join(here, app.config['UPLOAD_FOLDER'], 'image-upload')
        results.save(save_dir=save_dir)
        def and_syntax(alist):
            if len(alist) == 1:
                alist = "".join(alist)
                return alist
            elif len(alist) == 2:
                alist = " and ".join(alist)
                return alist
            elif len(alist) > 2:
                alist[-1] = "and " + alist[-1]
                alist = ", ".join(alist)
                return alist
            else:
                return
        confidences = list(results.pandas().xyxy[0]['confidence'])
        # confidences: rounding and changing to percent, putting in function
        format_confidences = []
        for percent in confidences:
            format_confidences.append(str(round(percent*100)) + '%')
        format_confidences = and_syntax(format_confidences)

        labels = list(results.pandas().xyxy[0]['name'])
        # labels: sorting and capitalizing, putting into function
        labels = set(labels)
        labels = [emotion.capitalize() for emotion in labels]
        labels = and_syntax(labels)
        important = [ x[-1] for x in results.pandas().xyxy[0].values.tolist()]
        counts = {items:important.count(items) for items in important}
        #This is going to send it to the results

        print('DONE, RENDERED ONCE!')
        print('line 161')
        print(type(counts))
        return render_template('recipes.html', confidences=format_confidences, labels=labels,
                               old_filename=filename,
                               filename= f'{filename[0:filename.rfind(".")]}.jpg', message=counts, titles=titles, descs=descs, ratings=ratings, urls=urls)
    else:
        found = False
        print('line 165')
        return render_template('recipes.html', labels='Nothing Recognized', old_filename=filename, filename=filename)



@app.route(f'{base_url}/sendRecipe',methods=['POST', 'GET'])
#@app.route('/sendRecipe',methods=['POST', 'GET'])
def sendRecipe():
    newRecipe = []
    print("HERE!!!")
    if request.method == "POST":
        print("Request json: ", request.form)
        # TODO: MAKE IT ITERATE THROUGH THE request.form BECAUSE THAT WORKS
        recipe_ingredients = request.form.getlist('array1[]')
        print(">",recipe_ingredients)
        print("Popped item", request.form.getlist('array1[]'))
        ## INSERT COOL AI STUFF HERE ##
        # Returns newRecipe, a list of the title first and then ingredients
        newRecipe = recipe_ingredients # Replace this with some formula to get recipe list based on ingredients
    return jsonify(newRecipe)

@app.route(f'{base_url}/uploads/image-upload/<path:filename>')
def files(filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'image-upload'), filename, as_attachment=True)



@app.route(f'{base_url}/recipes')
def recipes():
     return render_template('recipes.html', confidences="", labels="",
                               old_filename="",
                               filename="", message="None", titles=titles, descs=descs, ratings=ratings, urls=urls)

@app.route(f'{base_url}/view_recipe/<url>')
def view_recipe(url):
    return render_template('recipe_view.html', url=url)

@app.route(f'{base_url}/login')
def login():
    return render_template('login.html')

@app.context_processor
def override_url_for():
    print('test override')
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    print('test url_for?', endpoint, values)
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'https://cocalc22.ai-camp.dev'
    print(f'Try to open\n\n   {website_url}' + base_url + '\n\n')
    app.run(host = '0.0.0.0', port=port, debug=True)