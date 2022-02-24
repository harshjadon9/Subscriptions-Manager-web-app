from urllib import response
from django.shortcuts import render
import pyrebase
from django.shortcuts import redirect
import json
from django.http import JsonResponse
from dotenv import load_dotenv
import os
load_dotenv()

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


def index(request):
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        email=user['users'][0]['email']
    except:
        print("Token bhul gaya")
        return redirect(login)
    sub_list=[]
    total = 0
    try:
        all_subs = db.child(email.replace('.','_')).get()
        for sub in all_subs.each():
            # print(user.key()) # Morty
            sub_s={}
            if sub.val()[4] == "Yearly":
                sub.val()[5] = round((int(sub.val()[5])/12), 2)
            sub_s["id"] = sub.key()
            sub_s["payload"] = sub.val()
            sub_list.append(sub_s)
            total+=int(sub.val()[5])
    except:
        pass
    print(sub_list)
    return render(request, 'index.html', {'subs':sub_list,'total': total, "email":email})

def add(request):
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        email=user['users'][0]['email']
    except:
        print("Token bhul gaya")
        return redirect(login)
    id = request.GET.get('id')
    if(id!=None):
        sub = db.child(email.replace('.','_')).child(id).get()
        return render(request, 'add.html', {"payload":sub.val(), "id":id})
    return render(request, 'add.html')

def add_submit(request):
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        print(user)
    except:
        return JsonResponse({'error': "no token"}, status=403)
    # print(name, note, date, amount )
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
    if mode=="add":
        db.child(email.replace('.','_')).push(data, token)
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
    return JsonResponse({'msg': "done"}, status=200)
    

def delete(request):
    id=request.POST.get('subscription')
    try:
        token = request.COOKIES['token']
        user=authe.get_account_info(token)
        email=user['users'][0]['email']
    except:
        return JsonResponse({'error': "no token"}, status=403)
    print(email, id)
    db.child(email.replace('.','_')).child(id).remove()
    return JsonResponse({'msg': "no error"}, status=200)

def login(request, *arg):
	return render(request, 'login.html', {'err':arg})

def postsignIn(request):
    email=request.POST.get('email')
    pasw=request.POST.get('pass')
    try:
        # if there is no error then signin the user with given email and password
        user=authe.sign_in_with_email_and_password(email,pasw)
    except Exception as e:
            error_json = e.args[1]
            print(error_json)
            error = json.loads(error_json)['error']['message']
            return JsonResponse({'error': error}, status=401)
    return JsonResponse({'token': user['idToken']}, status=200)

def signup(request, *err):
    for arg in err:
        print (arg)
    return render(request,"signup.html", {'err':err})
 
def postsignUp(request):
    email = request.POST.get('email')
    passs = request.POST.get('pass')
    name = request.POST.get('name')
    #  try:
        # creating a user with the given email and password
    try:
        user=authe.create_user_with_email_and_password(email,passs)
        uid = user['localId']
        idtoken = request.session['uid']
        print(uid)
    except Exception as e:
            error_json = e.args[1]
            print(error_json)
            error = json.loads(error_json)['error']['message']
            return JsonResponse({'error': error}, status=403)
    return JsonResponse({'token': user['idToken']}, status=200)


    