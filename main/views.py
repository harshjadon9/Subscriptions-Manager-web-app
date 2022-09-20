from django.shortcuts import render, redirect
from django.http import JsonResponse
from dotenv import load_dotenv, find_dotenv
from urllib import response
from pathlib import Path
import pyrebase
import json
import os


## Todos
# Removing redundant codes ( eg. Cookies validator )
# data Validation on server end
# firebase error handing



# defining and fetching firebase API credentials
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
config={
        "apiKey": str(os.getenv('apiKey')),
        "authDomain": str(os.getenv('authDomain')),
        "databaseURL": str(os.getenv('databaseURL')),
        "projectId": str(os.getenv('projectId')),
        "storageBucket": str(os.getenv('storageBucket')),
        "messagingSenderId": str(os.getenv('messagingSenderId')),
        "appId": str(os.getenv('appId'))
}


# Initialising database,auth and firebase for further use
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
db=firebase.database()


# The '/' (index) configuration
def index(request):
    #check for valid cookies[token]
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        email=user['users'][0]['email']
    except:
        # no Token found, redirect to login page
        return redirect(login)
    sub_list=[]
    total = 0
    # fetching data from the firebase, on valid login
    try:
        all_subs = db.child(email.replace('.','_')).get()
        for sub in all_subs.each():
            # print(user.key()) => Morty
            sub_s={}
            if sub.val()[4] == "Yearly":
                sub.val()[5] = round((int(sub.val()[5])/12), 2)
            sub_s["id"] = sub.key()
            sub_s["payload"] = sub.val()
            sub_list.append(sub_s)
            total+=int(sub.val()[5])
    except:
        pass
    # print(sub_list)
    return render(request, 'index.html', {'subs':sub_list,'total': total, "email":email})

## { Authentication Section }

# Login Page
def login(request):
	return render(request, 'login.html')

# Login user, Pushing the credentials to the Firebase
def postsignIn(request):
    email=request.POST.get('email')
    pasw=request.POST.get('pass')
    try:
        user=authe.sign_in_with_email_and_password(email,pasw)
    except Exception as e:
            error_json = e.args[1]
            # print(error_json)
            error = json.loads(error_json)['error']['message']
            return JsonResponse({'error': error}, status=401)

    # login and return Token for sessions
    return JsonResponse({'token': user['idToken']}, status=200)

# Sign-up Page
def signup(request):
    return render(request,"signup.html")
 

# Create user, pushing the credentials to the Firebase
def postsignUp(request):
    email = request.POST.get('email')
    passs = request.POST.get('pass')
    try:
        user=authe.create_user_with_email_and_password(email,passs)
    except Exception as e:
        error_json = e.args[1]
        #print(error_json)
        error = json.loads(error_json)['error']['message']
        return JsonResponse({'error': error}, status=403)

    # login and return Token for sessions
    return JsonResponse({'token': user['idToken']}, status=200)

## { Authentication Section end }
    

# add new expense
def add(request):
    # checking for login cookies[token]
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        email=user['users'][0]['email']
    except:
        # redirect to login page
        return redirect(login)
    id = request.GET.get('id')

    # fetching email ID
    if(id!=None):
        sub = db.child(email.replace('.','_')).child(id).get()
        return render(request, 'add.html', {"payload":sub.val(), "id":id})
    return render(request, 'add.html')

def add_submit(request):
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        #print(user)
    except:
        return JsonResponse({'error': "no token"}, status=403)
    # print(name, note, date, amount )
    ## Getting request data to pushing
    email=user['users'][0]['email']
    name=request.POST.get('sub')
    note=request.POST.get('note')
    color=request.POST.get('color')
    recur=request.POST.get('recur')
    date=request.POST.get('date')
    amount=request.POST.get('amount')
    data = [
        name,
        note,
        date,
        color,
        recur,
        amount,
    ]
    mode=request.POST.get('mode')


    # adding the expense
    if mode=="add":
        db.child(email.replace('.','_')).push(data, token)
    # updating the expense
    elif mode=="update":
        id = request.POST.get('id')
        db.child(email.replace('.','_')).child(id).update(
            {
                0:name,
                1:note,
                2:date,
                3:color,
                4:recur,
                5:amount
                }
            )
    # 200 code return
    return JsonResponse({'msg': "done"}, status=200)
    

# Delete the expense
def delete(request):
    id=request.POST.get('subscription')
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        email=user['users'][0]['email']
    except:
        return JsonResponse({'error': "no token"}, status=403)
    # print(email, id)

    #  delete request
    db.child(email.replace('.','_')).child(id).remove()
    return JsonResponse({'msg': "no error"}, status=200)

