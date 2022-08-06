

#https://slidesgo.com/theme/charming-food-background#search-onion&position-1&results-135
# import requirements needed
#<<<<<<< HEAD
# pip install firebase_admin
# pip install openai
# pip install bcrypt
import bcrypt
from audioop import add
from flask import Flask, render_template
from flask import session

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
from firebase_admin import db
import os
import openai
import random


# https://cocalc22.ai-camp.dev/d76bb20d-59e1-4536-bf50-ae25d495aa4a/port/9999/
port = 1111
base_url = get_base_url(port) #'/d76bb20d-59e1-4536-bf50-ae25d495aa4a/port/9999/'
titles = []
descs = []
ratings = []
urls = []
data_list = [] # "appleRecipeData.txt","bananaRecipeData.txt",
fileListNames = ["bell pepperRecipeData.txt","carrotRecipeData.txt","cornRecipeData.txt","cucumberRecipeData.txt","gourdRecipeData.txt","kiwiRecipeData.txt","onionRecipeData.txt","orangeRecipeData.txt","potatoRecipeData.txt","tomatoRecipeData.txt"]

torch.hub._validate_not_a_forked_repo=lambda a,b,c: True

if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')

# A string must be encoded before being entered into this function in the format b'stringhere'
def toHash(password):
    salt = bcrypt.gensalt()
    pepper = password
    return [bcrypt.hashpw(pepper, salt),salt]
def toHashWithSalt(password,salt):
    newsalt = salt
    pepper = password
    return bcrypt.hashpw(pepper, newsalt)

#print("Hash", toHash(b'Hello world'))

cred = credentials.Certificate("ripesight-firebase-adminsdk-8dne2-7a07c80392.json")
firebase_admin.initialize_app(cred)

ref = db.reference("/",url="https://ripesight-default-rtdb.firebaseio.com/")
# https://cocalc22.ai-camp.dev/d76bb20d-59e1-4536-bf50-ae25d495aa4a/port/9999/


##### IMPORTANT ##### HERE THAT NERDS THAT MEANS READ ME BEFORE USING THE **** FUNCTION
# A string must be encoded before being entered into this function in the format b'stringhere'
def sendToDatabase(uname,pword):
    subref = db.reference("/loginInfo",url="https://ripesight-default-rtdb.firebaseio.com/")
    hashed = toHash(pword)
    subref.push().set({
            "username": "{}".format(uname),
            "password": hashed[0].hex(),
            "session_key": "",
            "saved_recipes": ""
        })
def pullLogins():
    subref = db.reference("/loginInfo",url="https://ripesight-default-rtdb.firebaseio.com/")
    dataPath = subref.get()
    loginArray = []
    for i in dataPath:
        loginArray.append({"passwordKey":i, "loginData":dataPath[i]})
    return loginArray
def resetLogins():
    subref = db.reference("/loginInfo",url="https://ripesight-default-rtdb.firebaseio.com/")
    subref.set({})

#print(ref.get())

def getCustomRecipe(data):
    if request.method == "POST":
        apiPath = APIref.get()
        apiKey = apiPath['key']
        if 1 == 1:
            print("Found!")
            #data = request.json['input']
            os.environ['OPENAI_API_KEY'] = apiKey
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.Completion.create(
                engine="babbage:ft-personal-2022-07-28-21-36-07",
                prompt= data,
                temperature=0.4,
                max_tokens=256,
                #top_p=1,
                frequency_penalty=0.26,
                presence_penalty=0.7
            )
            response = response.get("choices")[0]['text']
            response = response.split(" END")[0]
            print(response)
            return response



#resetLogins()
#sendToDatabase("this",b'self')

APIref = db.reference("/APIkey",url="https://ripesight-default-rtdb.firebaseio.com/")


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

#<<<<<<< HEAD
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

    for filename in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'image-upload')):
        print(f'Deleting {filename}')
        os.remove((os.path.join(app.config['UPLOAD_FOLDER'], 'image-upload' , filename)))
    if request.method == 'POST':
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
        
        
        filename =  f'{filename[0:filename.rfind(".")]}.jpg'
        print(filename)
        print(os.path.exists(filename))
        return render_template('recipes.html', confidences=format_confidences, labels=labels,
                               old_filename=filename,
                               filename= filename, message=counts, titles=titles, descs=descs, ratings=ratings, urls=urls, base_url=base_url)
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
        recipe_ingredients2 = json.dumps(recipe_ingredients)
        recipe_ingredients2 = recipe_ingredients2.replace("[", "")
        recipe_ingredients2 = recipe_ingredients2.replace("]", "")
        recipe_ingredients2 = recipe_ingredients2.replace(" ", "")
        recipe_ingredients2 = recipe_ingredients2.replace('"', '')
        print("Recipe ingredients",recipe_ingredients2)
        newRecipe = getCustomRecipe(recipe_ingredients2)
        print(newRecipe.split("\n"))
        ## INSERT COOL AI STUFF HERE ##
        # Returns newRecipe, a list of the title first and then ingredients
        #newRecipe = recipe_ingredients # Replace this with some formula to get recipe list based on ingredients
    return jsonify(newRecipe.split("\n"))


@app.route(f'{base_url}/getAccountData', methods=["GET","POST"])
def getAccountData():
    if request.method == "POST":
        accountData = request.form
        print(accountData)
        username = accountData['Uname']
        password = accountData['PSword']
        #print("Username", username)
        #print("Password", password)
        archived_login_data = pullLogins()
        canCreateAccount = True
        for i in archived_login_data:
            if i['loginData']['username'] == username:
                canCreateAccount = False
                print("Account creation failed because there was already a username with the same name")
                break
        if canCreateAccount == True:
            sendToDatabase(username,password.encode())
            print("Password success")
            alertMsg = "Account creation successful."
        else:
            alertMsg = "Account creation failed."
    return render_template("create_account.html", msg=alertMsg)
#    return redirect(url_for("login"))

@app.route(f'{base_url}/getLogin', methods=["GET","POST"])
def getLogin():
    if request.method == "POST":
        accountData = request.form
        print(accountData)
        username = accountData['Uname']
        password = accountData['PSword']
        #print("Username", username)
        #print("Password", password)
        archived_login_data = pullLogins()
        canLogin = False
        
        random_session_key = ''
        
        for p,i in enumerate(archived_login_data):
            #print("saltType", type(i['loginData']['salt']))
            #print("serverSidePassType", type(i['loginData']['password']))
            #print("clientSidePassType", type(password))
            #print("randomSaltType", bcrypt.gensalt())
            #print("serverSalt", bytes.fromhex(i['loginData']['salt']))
            #print("byteServerPass",bytes.fromhex(i['loginData']['password']))
            #print("byteMyPass",toHashWithSalt(password.encode(),bytes.fromhex(i['loginData']['salt'])))
            if i['loginData']['username'] == username and bcrypt.checkpw(password.encode(),bytes.fromhex(i['loginData']['password'])):
                canLogin = True
                print("Login success!")
                for j in range(1,51):
                    random_session_key = random_session_key + str(random.randint(1,9))
                current_ref = db.reference("/loginInfo",url="https://ripesight-default-rtdb.firebaseio.com/")
                
                pass_key = i['passwordKey']
                new_ref_data = ref.get()
                print("new_ref_data before aug", new_ref_data)
                new_ref_data['loginInfo'][pass_key]['session_key'] = random_session_key
                print("new_ref_data after", new_ref_data)
                
                ref.update(new_ref_data)
                alertMsg = "Login successful."
                break
        if canLogin == False:
            print("Username or password is incorrect.")
            alertMsg = "Login failed."
            random_session_key = '-1'
            # Session key is negative one if there is no login data
        print("Session-key", random_session_key)
        session['session_key'] = random_session_key
    return render_template('login.html', session_key=random_session_key, msg=alertMsg)





@app.route(f'{base_url}/uploads/image-upload/<path:filename>')
def files(filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'image-upload'), filename, as_attachment=True)



@app.route(f'{base_url}/recipes')
def recipes():
    return render_template('recipes.html', confidences="", labels="",
                               old_filename="",
                               filename="", message="None", titles=titles, descs=descs, ratings=ratings, urls=urls)

@app.route(f'{base_url}/display_favorites')
def display_favorites():
    skey = session.get('session_key')
    archived_login_data = pullLogins()
    for a,b in enumerate(archived_login_data):
        if b["loginData"]["session_key"] == skey:
            if b["loginData"]["saved_recipes"] != "":
                return render_template('display_favorite_recipes.html', favorite_list=json.loads(b["loginData"]["saved_recipes"]), errMsg=0)
    return render_template('display_favorite_recipes.html', favorite_list=[],errMsg=1)

@app.route(f'{base_url}/view_recipe/<url>')
def view_recipe(url):
    skey = session.get("session_key")
    if skey == None:
        skey = "-1"
    print("Session key:")
    print(skey)
    return render_template('recipe_view.html', url=url, session_key=skey)


@app.route(f'{base_url}/sendFavorite',methods=['POST', 'GET'])
#@app.route('/getFav',methods=['POST', 'GET'])
def getFav():
    newRecipe = []
    print("Favorite!!!")
    if request.method == "POST":
        print("Request favorite: ", request.form)
        # TODO: MAKE IT ITERATE THROUGH THE request.form BECAUSE THAT WORKS
        favorite_data = request.form.getlist('array1[]')
        print(">>",favorite_data)
        print("Popped favorite item", request.form.getlist('array1[]'))
        archived_login_data = pullLogins()
        print(archived_login_data)
        for y,z in enumerate(archived_login_data):
            print(z['loginData']['session_key'])
            if z['loginData']['session_key'] == favorite_data[1]:
                current_ref = db.reference("/loginInfo",url="https://ripesight-default-rtdb.firebaseio.com/")
                pass_key = z['passwordKey']
                new_ref_data = ref.get()
                print("new_ref_data before aug", new_ref_data)
                
                
                new_saved_recipe = []
                
                if z['loginData']['saved_recipes'] != "":
                    new_saved_recipe = json.loads(z['loginData']['saved_recipes'])
                new_saved_recipe.append(favorite_data[0])
                
                new_ref_data['loginInfo'][pass_key]['saved_recipes'] = json.dumps(new_saved_recipe)
                print("new_ref_data after", new_ref_data)
                
                ref.update(new_ref_data)
        
        ## INSERT COOL AI STUFF HERE ##
        # Returns newRecipe, a list of the title first and then ingredients
        #newRecipe = recipe_ingredients # Replace this with some formula to get recipe list based on ingredients
    return ""



@app.route(f'{base_url}/login')
def login():
    return render_template('login.html',session_key=-1,msg="-1")

@app.route(f'{base_url}/create_account')
def create_account():
    return render_template('create_account.html',msg="-1")

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

