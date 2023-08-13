from re import S
from wtforms import BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
import sqlite3
import random
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime,timedelta

#pip3 freeze > requirements.txt
#pip3 install -r requirements.txt

app = Flask(__name__)
app.config['SECRET_KEY'] = '!019@S-asoid[as0d^'
#For SQL Alchemy Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///purchase.db' 
# app.config['SQLALCHEMY_BINDS'] = {
#     'scoreboard':'sqlite:///scoreboard.db',
#     'moneyboard':'sqlite:///moneyboard.db'
# }

#--------- Create Database to keep track of purchases by users -------- 
purchase = SQLAlchemy(app) #database to keep track of the purchases
class UserPurchases(purchase.Model):
    id = purchase.Column('purchase_id', purchase.Integer,  primary_key = True)
    dateandtime = purchase.Column(purchase.String(100))
    username = purchase.Column(purchase.String(100))
    amount = purchase.Column(purchase.String(100))

    def __init__(self, dateandtime, username, amount):
        self.dateandtime = dateandtime
        self.username = username
        self.amount = amount

if not database_exists('sqlite:///purchase.db'):
    purchase.create_all() #Create the purchase data base
#--------- Create Database to keep track of purchases by users -------- 

#------- Create Database for the amount of wins of each users --------
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scoreboard.db' #For SQL Alchemy Database
scoreboard = SQLAlchemy(app)
class UserScoreboard(scoreboard.Model):
    # id = scoreboard.Column('rank', scoreboard.Integer,  primary_key = True)
    username = scoreboard.Column(scoreboard.String(100), primary_key = True)
    wins = scoreboard.Column(scoreboard.String(100))

    def __init__(self, wins, username):
        self.username = username
        self.wins = wins

if not database_exists('sqlite:///scoreboard.db'):
    scoreboard.create_all() #Create the score data base
#------- Create Database for the amount of wins of each users --------


#------- Create Database for the amount of money gained of each users --------
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moneyboard.db' #For SQL Alchemy Database
moneyboard = SQLAlchemy(app)
class MondayBoard(moneyboard.Model):
    username = moneyboard.Column(moneyboard.String(100), primary_key = True)
    moneygained = moneyboard.Column(moneyboard.String(100))

    def __init__(self, moneygained, username):
        self.username = username
        self.moneygained = moneygained

if not database_exists('sqlite:///moneyboard.db'):
    moneyboard.create_all() #Create the money data base
#------- Create Database for the amount of money gained of each users --------









# ------------LOG IN AND REGISTERING HERE------------
class LoginForm(FlaskForm):
    
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])
    login = SubmitField("login")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    address = StringField("Address", validators=[validators.Length(min=3, max=50), validators.DataRequired(message="Please Fill This Field")])
    email = EmailField('Email', [validators.DataRequired(message="Please Fill This Field"), validators.Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[
        validators.DataRequired(message="Please Fill This Field"),
        validators.EqualTo(fieldname="confirmpassword", message="Your Passwords Do Not Match")
    ])
    confirmpassword = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")])
    register = SubmitField("Register")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods = ['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        name = str(form.name.data)
        username = form.username.data
        address = form.address.data
        email = form.email.data
        password = form.password.data
        confirmpassword = form.confirmpassword.data
        #How much token money the player has when register:
        playertokens = 10000
        conwins = sqlite3.connect("scoreboard.db")
        curwins = conwins.cursor()

        conmoney = sqlite3.connect("moneyboard.db")
        curmoney = conmoney.cursor()

        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            #Check whether there is already a SQL UserInfo table
            listOfTables = cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='UserInfo'; """).fetchall()
            if listOfTables != []:
                #If there is alredy a SQL UserInfo Table, then insert user information  in the table
                #check whether user already exist:
                checkUsername = cur.execute(f"SELECT username from UserInfo WHERE username='{username}';")
                checkUsername = cur.fetchone()
                if not checkUsername:
                    if password == confirmpassword:
                        #Hash the passwords
                        password = generate_password_hash(password)
                        confirmpassword = password
                        curwins.execute("INSERT into user_scoreboard(username, wins) values (?, ?)", (username, "0"))
                        conwins.commit()
                        curmoney.execute("INSERT into monday_board(username, moneygained) values (?, ?)", (username, "0"))
                        conmoney.commit()
                        cur.execute("INSERT into UserInfo (name, username, email, address, password, confirmpassword, playertokens) values (?,?,?,?,?,?,?)", (name, username, email, address,password, confirmpassword, playertokens))
                        con.commit()
                    else:
                        flash("Password mismatch. Please re-enter.", 'error')
                        return redirect(url_for('register'))
                else:
                    flash("username has already been taken! Try another one.", 'error')
                    return redirect(url_for('register'))
            else: 
                #Create the UserInfo Table
                table = '''CREATE TABLE UserInfo(id INTEGER PRIMARY KEY AUTOINCREMENT, name char(1000), username char(1000), email char(1000), address char(1000), password char(1000), confirmpassword char(1000), playertokens INTEGER)'''
                password = generate_password_hash(password)
                confirmpassword = password
                cur.execute(table)
                cur.execute("INSERT into UserInfo (name, username, email, address, password, confirmpassword, playertokens) values (?,?,?,?,?,?,?)", (name, username, email, address,password, confirmpassword, playertokens))
                con.commit()
                curwins.execute("INSERT into user_scoreboard(username, wins) values (?, ?)", (username, "0"))
                conwins.commit()
                curmoney.execute("INSERT into monday_board(username, moneygained) values (?, ?)", (username, "0"))
                conmoney.commit()
                
        flash("Successfully Registered! You are granted $10000 king coins! Log in now.",'error')
        if form.is_submitted():
            return redirect(url_for('login'))
    return render_template("register.html", regform = form)
    con.close()
# doublecheckusernamewithlogin = {}

@app.route("/login", methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == "POST":
        # username = str(form.username.data)
        username = request.form['username']
        password = request.form['password']
        # password = form.password.data
        #user this in users entering the room
        temp = {username: username}
        # doublecheckusernamewithlogin.update(temp)
        # print(doublecheckusernamewithlogin)
        # password = str(form.password.data)

        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute("SELECT username FROM UserInfo")
        if form.is_submitted(): 
            #Check whether username and password are correctly matched...
            # statement = f"SELECT username from UserInfo WHERE username='{username}' AND password = '{password}';"
            # cur.execute(statement)

            cur.execute(f"SELECT password from UserInfo WHERE username='{username}';")
            #Get the Hashed password from the data base where the username is crossponded and unHash it.
            getPassword = cur.fetchone()
            print(type(getPassword))

            if (type(getPassword) is type(None)):
                flash("No user exist! Please Sign up!",'error')
                return redirect(url_for('login')) 
            
            getPassword = getPassword[0]
            print(username, "Hashed Password: ", getPassword)

            if not check_password_hash(getPassword, password):
                flash ("Incorrect Username or Password!",'error')
            else:
                session['username'] = username
                return redirect(url_for('home')) 
            con.close()

    return render_template("login.html", logform = form)
# ------------LOG IN AND REGISTERING HERE------------ #


# ------------CREATE OR JOIN BREAKOUT ROOM HERE------------ #
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

class BuyTokensForm(FlaskForm):
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    amountoftokens = IntegerField("Amount of tokens to purchase: ", validators=[validators.NumberRange(min=0, max=100000000000), validators.DataRequired(message="Please Fill This Field")])
    submit = SubmitField("Purchase")

@app.route("/buytokens", methods = ['POST', 'GET'])
def buytokens():
    form = BuyTokensForm()
    if (request.method == "POST"):
        username = str(form.username.data)
        amountoftokens = form.amountoftokens.data
        if(type(amountoftokens) is type(None) or type(amountoftokens) is type(str) ):
            flash("Must input an integer value for the amount you would like to purchase!",'error')
            return redirect(url_for('buytokens'))
        #10 tokens = 0.032 dollar
        # conversion = float(amountoftokens)*0.01
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        checkUsername = cur.execute(f"SELECT username from UserInfo WHERE username='{username}';")
        checkUsername = cur.fetchone()
        if not checkUsername:
            flash("Username does not exist! Please sign up or re-enter!", 'error')
            return redirect(url_for('index'))
        # elif doublecheckusernamewithlogin.get(username) != username:
        #     flash("Username does not match the one you login with! Please re-check!")
        #     return redirect(url_for('login'))
        else:
            if form.is_submitted(): 
                cur.execute(f"SELECT playertokens from UserInfo WHERE username='{username}';")
                curusertoken = cur.fetchone()
                #turn tuple into a integer
                curusertoken = curusertoken[0]
                #NEED TO WORK ON WHAT IF THE USER IS BETTING MORE TOKENS THAN THEY HAVE. Set up a Buy Tokens Page:
                finaltokencount = int(curusertoken) + int(amountoftokens)
                cur.execute(f"UPDATE UserInfo SET playertokens = '{finaltokencount}' WHERE username = '{username}';")
                con.commit()
                flash("Purchase success!", 'error')
                now = datetime.now()
                purchasedateandtime = str(now.strftime("%d/%m/%Y %H:%M:%S"))
                # print(purchasedateandtime)
                conpurchase = sqlite3.connect("purchase.db")
                curpurchase = conpurchase.cursor()
                
                curpurchase.execute("INSERT into user_purchases(dateandtime, username, amount) values (?, ?, ?)", (purchasedateandtime, username, amountoftokens))
                conpurchase.commit()
                # storetopurchasedatabase = UserPurchases(purchasedateandtime, str(username), str(amountoftokens))
                # purchase.session.add(storetopurchasedatabase) #add the purchase to the purchase history database
                # purchase.session.commit()
                return redirect(url_for('login'))
    return render_template("buytokens.html", form = form)

@app.route("/home", methods = ['POST', 'GET'])
def home():
    if (request.method == "POST"):
        #User log in checks here:
        username = request.form['username']
        password = request.form['password']

        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(f"SELECT password from UserInfo WHERE username='{username}';")
            #Get the Hashed password from the data base where the username is crossponded and unHash it.
        getPassword = cur.fetchone()
        if (type(getPassword) is type(None)):
            flash("No user exist! Please Sign up!",'error')
            return redirect(url_for('login')) 
        getPassword = getPassword[0]
        print(username, "Hashed Password: ", getPassword)

        if not check_password_hash(getPassword, password):
            flash ("Incorrect Username or Password!",'error')
            return redirect(url_for('login')) 

        session['username'] = username
        return render_template("home.html", username = username)
    else:
        flash("Please log in first!",'error')
        return redirect(url_for('login'))

#Get user's info.
@app.route("/myinfo", methods = ['POST', 'GET'])
def myinfo():
    username = session.get('username')
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    #Get current amount of tokens of the player
    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{username}';")
    userTOKEN = cur.fetchone()
        #turn tuple into a integer 
    if (type(userTOKEN) is type(None)):
            flash("Please Log in!",'error')
            return redirect(url_for('login')) 
    userTOKEN = userTOKEN[0]
         #Get current ID of the player
    cur.execute(f"SELECT id from UserInfo WHERE username='{username}';")
    userID = cur.fetchone()
    userID = userID[0]

    cur.execute(f"SELECT address from UserInfo WHERE username='{username}';")
    userADDRESS = cur.fetchone()
    userADDRESS = userADDRESS[0]

    cur.execute(f"SELECT email FROM UserInfo WHERE username='{username}';")
    userEMAIL = cur.fetchone()
    userEMAIL = userEMAIL[0]

    #fetch the purchase data of a user from the purchase SQLAlchemy database

    con2 = sqlite3.connect("purchase.db")
    cur2 = con2.cursor()
    cur2.execute(f"SELECT dateandtime, amount FROM user_purchases WHERE username = '{username}'")
    allpurchasehistory = cur2.fetchall()
    print(type(allpurchasehistory))
    allpurchasehistory = list(allpurchasehistory)
    return render_template("myinfo.html", username = username, userTOKEN = userTOKEN, userID = userID, userADDRESS = userADDRESS, userEMAIL = userEMAIL, allpurchasehistory = allpurchasehistory)

@app.route("/scoreboard", methods = ['POST', 'GET'])
def scoreboard():
    con = sqlite3.connect("scoreboard.db")
    con.row_factory = sqlite3.Row
    cur =  con.cursor()
    cur.execute("select * from user_scoreboard ORDER BY wins DESC")
    rows = cur.fetchall()
    return render_template("scoreboard.html", rows = rows)


@app.route("/moneyboard", methods = ['POST', 'GET'])
def moneyboard():
    con = sqlite3.connect("moneyboard.db")
    con.row_factory = sqlite3.Row
    cur =  con.cursor()
    cur.execute("select * from monday_board ORDER BY moneygained DESC")
    rows = cur.fetchall()
    return render_template("moneyboard.html", rows = rows)


#Dictionary that stores users temporary bets.
usersBetsTempDictionary = {}
 #Count dictionary for the number of users in a session (room).
numberOfUsersDictionary = {}

#Players store the players inside the array for the Blackjack game
playersBlackJackArray = []

@app.route("/blackJack", methods = ['POST', 'GET'])
def chess():
    # form = RoomForm()
    if (request.method == "POST"):
        # username = request.form['username']
        # room = form.room.data
        username = session.get('username') # PASS THE USERNAME THAT WAS USED TO LOGGED IN TO HERE.
        print(username)
        room = request.form['room']
        tokens = request.form['tokens']
        
        if (type(tokens) is type(None) or tokens.isnumeric() == False):
                flash("Must input an integer value for the amount you would like to bet!",'error')
                return redirect(url_for('blackJack'))

        # print(doublecheckusernamewithlogin.get(username))
        # print(username)
        #Store the amount the user has temporarily bet.
        usersBet = {username: tokens}
        usersBetsTempDictionary.update(usersBet)
        #Connect database.
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        #Check whether the user's username exist 
        checkUsername = cur.execute(f"SELECT username from UserInfo WHERE username='{username}';")
        checkUsername = cur.fetchone()
        if not checkUsername:
            flash("Username does not exist! Please sign up or re-enter!",'error')
            return redirect(url_for('home'))
        #check whether the user inputted username match the one they logged in with.
        # elif doublecheckusernamewithlogin.get(username) != username:
        #     flash("Username does not match the one you login with! Please re-check!")
        #     return redirect(url_for('login'))
        else:
            #Get the current token count of the user
            cur.execute(f"SELECT playertokens from UserInfo WHERE username='{username}';")
            curusertoken = cur.fetchone()
            #turn tuple into a integer
            curusertoken = curusertoken[0]
            finaltokencount = int(curusertoken) - int(tokens)
            
            if (finaltokencount < 0):
                flash("Insufficient amount to bet! Please buy more tokens!",'error')
                return redirect(url_for('home'))
            else:
                #Update tokens in the data base based on the user's $bet amount
                cur.execute(f"UPDATE UserInfo SET playertokens = '{finaltokencount}' WHERE username = '{username}';")
                con.commit()
                
                #Count the number of users in the room. If it is greater than 2, another more users can't join...
                # Store the users to each room dictionary.
                if (str(room) not in numberOfUsersDictionary):
                    numberOfUsersDictionary[str(room)] = list()
                    numberOfUsersDictionary[str(room)].append(username)
                else:
                    numberOfUsersDictionary[str(room)].append(username)
                temp = numberOfUsersDictionary[str(room)]
                numberOfusers = len(temp)
                # session['username'] = username
                session['room'] = room
                session['tokens'] = tokens

                if (numberOfusers < 3):
                    # doublecheckusernamewithlogin.pop(username)
                    print(username)
                    print(temp)
                    #Players store the players inside the array for the Blackjack game
                    playersBlackJackArray.append(str(username))
                    return render_template('chess.html', session = session)
                else:
                    print(username)
                    numberOfUsersDictionary[str(room)].remove(username)
                    temp = numberOfUsersDictionary[str(room)]
                    print(temp)
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{curusertoken}' WHERE username = '{username}';")
                    con.commit()
                    flash("Room is full! Try enter another one.",'error')
                    return redirect(url_for('home'))
    else:
        flash("Please log in first!",'error')
        return redirect(url_for('login'))

# ------------CREATE OR JOIN BREAKOUT ROOM HERE------------ #


#------ BLACK JACK HERE------- #

class Player():
    def __init__(self, name, score, cards, stay):
        self.name = name
        self.score = score
        self.cards = cards
        self.stay = stay
    
    def distribute_cards(self):
        while len(self.cards) != 2:
            #One bug that needs to be fixed: what if user gets two 11s?
            self.cards.append(random.randint(1, 11))
            if (len(self.cards)) == 2:
                return self.cards

    def hit(self, newcard):
        self.cards.append(newcard)
    
    def stay(self):
        self.stay = 1

    def reset(self):
        self.cards = []
        self.stay = 0
        # self.score = 0
    
    def resetScore(self):
        self.score = 0

# ------------SESSION SERVER HERE------------ #
UserInRoomsDict = {} #Dictionary where the key is the room and the value is the current users in that room
# temparrayroom = []
UserScoreTrackerDict = {}
UserScore = 0
temparrayroom = []

TotalGameCountArrayDict = {}
TotalGameCountArray = []



@socketio.on('join', namespace='/blackJack')
def join(message):
    room = session.get('room')
    username = str(session.get('username'))
    join_room(room)
    emit('status', {'msg':  str(session.get('username')) + ' has entered the room.' + " Bet amount: $" + str(session.get('tokens'))}, room=room)
    #Whoever enters the room gets stored into the temporary array.

    # print(temparrayroom)
    roomvalue = str(room)
    # usersintheroom = []
    
    if not (roomvalue in UserInRoomsDict):
        tempdic = {roomvalue: []}
        UserInRoomsDict.update(tempdic)
        temparrayroom = UserInRoomsDict.get(roomvalue)
    
    temparrayroom = UserInRoomsDict.get(roomvalue)
    temparrayroom.append(username)
    tempdica = {roomvalue: temparrayroom}
    UserInRoomsDict.update(tempdica)
    print(UserInRoomsDict)

    if(len(temparrayroom) == 2):
        # temparrayroom.clear()
        # print(temparrayroom)
        # temparrayroom.clear()
        
        print("done!")
        global playerA
        global playerB
        global playerAcards
        global playerBcards

        #NEED TO FIX THIS SHHIT
        RoomUsersArray = []
        RoomUsersArray = UserInRoomsDict[roomvalue]
        # print(UserInRoomsDict.get(str(room)))
        # print(RoomUsersArray)
        #Add to Score Dictionary the scores of each user for tracking purposes:
        tempdict2 = {RoomUsersArray[0]: UserScore}
        tempdict3 = {RoomUsersArray[1]: UserScore}
        UserScoreTrackerDict.update(tempdict2)
        UserScoreTrackerDict.update(tempdict3)

        playerAcards = []
        playerBcards = []
        playerA = Player(RoomUsersArray[0], 0, playerAcards, 0)
        playerB = Player(RoomUsersArray[1], 0, playerBcards, 0)
        

        Ainitialcards = playerA.distribute_cards()
        AinitialcardsFirst = Ainitialcards[0]
        AinitialcardsSecond = Ainitialcards[1]
       
        Binitialcards = playerB.distribute_cards()
        BinitialcardsFirst = Binitialcards[0]
        BinitialcardsSecond = Binitialcards[1]
        
        playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
        playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
        emit('startGame', {'msg': "\n--------------Game Begins!--------------\n"}, room = room)
        emit('startGame', {'msg': RoomUsersArray[0] + " has cards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n" +
        RoomUsersArray[1] + " has cards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n", 
        'AinitialcardsFirst': AinitialcardsFirst,
        'AinitialcardsSecond': AinitialcardsSecond,
        'BinitialcardsFirst':BinitialcardsFirst,
        'BinitialcardsSecond': BinitialcardsSecond
        }, room = room)
    else:
        emit('startGame', {'msg': "\nWaiting for another player to join...\n"}, room = room)

@socketio.on('gameover', namespace='/blackjack')
def gameover(message):
    room = session.get('room')
    username = session.get('username')
    AmountOfUsers = len(numberOfUsersDictionary[str(room)])
    print(AmountOfUsers)
    if (AmountOfUsers == 1):
        # print("HERE AMOUNT")
        numberOfUsersDictionary[str(room)].remove(username)
        TotalGameCountArrayDict.pop(str(room))
    else:
        # print("HERE AMOUNT 2")
        numberOfUsersDictionary[str(room)].remove(username)
        UserScoreTrackerDict.pop(str(username))
        session.clear()
        if (TotalGameCountArrayDict.get(str(room) is not None)):
            TotalGameCountArrayDict.pop(str(room))
    # if (TotalGameCountArrayDict.get(str(room) is not None)):
    if (UserInRoomsDict.get(str(room)) is not None):
        UserInRoomsDict.pop(str(room))
    leave_room(room)
    print(UserInRoomsDict)
    print(TotalGameCountArrayDict)
    session.clear()

@socketio.on('left', namespace='/blackJack')
def left(message):
    room = session.get('room')
    username = session.get('username')
    tempusername = username
    #Connect to databse
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    #Give the exited user's money to the other player who's also in the room. 
    #If however, the user is alone, he can keep his money. However, if he is with someone else, his money goes to the other person.
    if (numberOfUsersDictionary[str(room)] is not None):
        Users = numberOfUsersDictionary[str(room)]
    # print(Users)
    AmountOfUsers = len(numberOfUsersDictionary[str(room)])
    print("#Users", AmountOfUsers)
    if (AmountOfUsers == 1):
        #get the amount the user has temporarily betted.
        tempBet = int(usersBetsTempDictionary[username])
        numberOfUsersDictionary[str(room)].remove(username)
        # print("money bet: ", tempBet)
        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{username}';")
        curusertoken = cur.fetchone()
        curusertoken = curusertoken[0]
        finaltokencount = tempBet + curusertoken
        # print("final token count: ", finaltokencount)
        UserInRoomsDict.pop(str(room))
        cur.execute(f"UPDATE UserInfo SET playertokens = '{finaltokencount}' WHERE username = '{tempusername}';")
        con.commit()
    else:
        theotheruser = ""
        tempBetExitUser = int(usersBetsTempDictionary[tempusername])
        # print("Exit User money bet: ", tempBetExitUser)
        # print("Users that is leaving: ", tempusername)
        Users.remove(str(tempusername))
        theotheruser = Users[0]
        tempBetStayUser = int(usersBetsTempDictionary[theotheruser])
        print("Stay User money bet: ", tempBetStayUser)
        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{theotheruser}';")
        curusertoken = cur.fetchone()
        curusertoken = curusertoken[0]
        finaltokencount = tempBetExitUser + curusertoken
        print("final token count: ", finaltokencount)
        cur.execute(f"UPDATE UserInfo SET playertokens = '{finaltokencount}' WHERE username = '{theotheruser}';")
        con.commit()
        #UserInRoomsDict.pop(str(room))
        #print(UserInRoomsDict)
        if (UserScoreTrackerDict.get(str(username)) is not None):
            UserScoreTrackerDict.pop(str(username))
        if (TotalGameCountArrayDict.get(str(room)) is not None):
            TotalGameCountArrayDict.pop(str(room))
        session.clear()
    #UserInRoomsDict.pop(str(room))
    print(UserInRoomsDict)
    leave_room(room)
    session.clear()
    emit('status', {'msg': str(username) + ' has left the room.'}, room=room)


@socketio.on('text', namespace='/blackJack')
def text(message):
    room = session.get('room')
    #prints the name of the user in the chat room who texts
    print(session.get('username'))
    emit('message', {'msg': str(session.get('username')) + ' : ' + str(message['msg'])}, room=room)


@socketio.on('hit', namespace='/blackJack')
def hit(message):
    room = session.get('room')
    playerwhoHits = session.get('username')
    RoomUsersArray = UserInRoomsDict.get(str(room))
    print(RoomUsersArray)
    # print("here")
    if (len(RoomUsersArray) == 2):
        playerAnewcard = RoomUsersArray[0] + "'s turn"
        playerBnewcard =  RoomUsersArray[1] + "'s turn"
        if (str(playerwhoHits) == RoomUsersArray[0]):
            # Pass the value of the new card from python to javascript using emit.
            playerAnewcard = random.randint(1, 11)
            playerA.hit(playerAnewcard)
            # emit('hitGame', {'cardA': playerAnewcard}, room = room) # Pass the value of the new card from python to javascript using emit. (ABOVE)
            print(playerAnewcard)
            playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
            playerBcardsOut = ' '.join(str(e) for e in playerB.cards)

            emit('hitGame', {'msg':RoomUsersArray[0] + " hitted! " + "\ncards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
       
        if (str(playerwhoHits) == RoomUsersArray[1]):
            # Pass the value of the new card from python to javascript using emit.
            playerBnewcard = random.randint(1, 11)
            playerB.hit(playerBnewcard)
            # emit('hitGame', {'cardB': playerBnewcard}, room = room) # Pass the value of the new card from python to javascript using emit. (ABOVE)
            print(playerBnewcard)

            playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
            playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
            emit('hitGame', {'msg':RoomUsersArray[1] + " hitted! " + "\ncards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n", 'playerBnewcard': playerBnewcard, 'playerAnewcard': playerAnewcard}, room = room)
        
        #Check win or lose from hitting....
        if (sum(playerA.cards) > 21):
            # playerAnewcard = RoomUsersArray[0]  + " loses"
            # playerBnewcard = RoomUsersArray[1]  + " wins"
            playerAnewcard = "x"
            playerBnewcard = "x"
            GameOver = 0
            keyfordicdic = str(room)
            TotalGameCountArray = TotalGameCountArrayDict.get(keyfordicdic)
            print("HERE IS THE INITIAL ARRAY FOR GAME COUNT", TotalGameCountArray)
            if (TotalGameCountArray is None):
                TotalGameCountArray = []
                # TotalGameCountArray.append(1)
                tempdicdic = {keyfordicdic: TotalGameCountArray}
                TotalGameCountArrayDict.update(tempdicdic)
            TotalGameCountArray.append(1)
            tempwinner = RoomUsersArray[1] + " wins!" + " <#" + str(len(TotalGameCountArray) + 1) + " game>"
            emit('hitGame', {'msg':RoomUsersArray[1] + " wins! " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard
            , 'tempwinner':tempwinner}, room = room)
            #playerB.score += 1
            
            #Update user's score based on their usernames and output it.
            playerAscore = UserScoreTrackerDict.get(RoomUsersArray[0])
            playerBscore = UserScoreTrackerDict.get(RoomUsersArray[1])
            playerBscore += 1
            tempdic = {RoomUsersArray[1]: playerBscore}
            UserScoreTrackerDict.update(tempdic)

        
            tempdicdic = {keyfordicdic: TotalGameCountArray}
            TotalGameCountArrayDict.update(tempdicdic)
            TotalGameCountArray = TotalGameCountArrayDict.get(room)
            print(TotalGameCountArrayDict)

            print(TotalGameCountArray)
            print(len(TotalGameCountArray))
            whowins = ""

            conwins = sqlite3.connect("scoreboard.db")
            curwins = conwins.cursor()

            con = sqlite3.connect("users.db")
            cur = con.cursor()

            conmoney = sqlite3.connect("moneyboard.db")
            curmoney = conmoney.cursor()
            
            if (len(TotalGameCountArray) == 21):
                if (playerAscore > playerBscore):
                    
                    whowins = RoomUsersArray[0]
                    #get the amount the user has temporarily betted.
                    winner = str(RoomUsersArray[0])
                    loser = str(RoomUsersArray[1])

                    curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                    userswins = curwins.fetchone()
                    usertotalwins = str(userswins[0])
                    if (usertotalwins is None):
                        usertotalwins = "1"
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()
                    else:
                        usertotalwins = int(usertotalwins) + 1
                        usertotalwins = str(usertotalwins)
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()
                    
                    tempBetwinner = int(usersBetsTempDictionary[winner])
                    tempBetloser = int(usersBetsTempDictionary[loser])

                    curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                    usermoney = curmoney.fetchone()
                    usertotalmoney = str(usermoney[0])
                    usertotalmoney = int(usertotalmoney) + tempBetwinner
                    usertotalmoney = str(usertotalmoney)
                    curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                    conmoney.commit()

                    print(tempBetwinner)
                    print(tempBetloser)
                    #for winner:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    winnerfinaltokencount = tempBetwinner + curusertoken + tempBetwinner
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                    con.commit()

                    #for loser:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                    con.commit()
                    
                elif(playerAscore < playerBscore):
                    whowins = RoomUsersArray[1]
                    winner = str(RoomUsersArray[1])
                    loser = str(RoomUsersArray[0])

                    tempBetwinner = int(usersBetsTempDictionary[winner])
                    tempBetloser = int(usersBetsTempDictionary[loser])

                    curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                    usermoney = curmoney.fetchone()
                    usertotalmoney = str(usermoney[0])
                    usertotalmoney = int(usertotalmoney) + tempBetwinner
                    usertotalmoney = str(usertotalmoney)
                    curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                    conmoney.commit()

                    curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                    userswins = curwins.fetchone()
                    usertotalwins = str(userswins[0])
                    if (usertotalwins is None):
                        usertotalwins = "1"
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()
                    else:
                        usertotalwins = int(usertotalwins) + 1
                        usertotalwins = str(usertotalwins)
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()
                    

                    print(tempBetwinner)
                    print(tempBetloser)
                    #for winner:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    winnerfinaltokencount = tempBetwinner + curusertoken + tempBetwinner
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                    con.commit()

                    #for loser:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                    con.commit()
                    
                GameOver = 1
                    #Todo: Give player A's money to player B
                print('GAME FINISHED')
            

            emit('stayGame', {'msg':"Score: " + RoomUsersArray[0] + " <" + str(playerAscore) + "> " + " - v.s. - " +  RoomUsersArray[1] + " <" + str(playerBscore)  + "> " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,
            'playerAscore': playerAscore, 'playerBscore':playerBscore, 'GameOver': GameOver, 'whowins':whowins
            }, room = room)

            # tempwinner = "#" + len(TotalGameCountArray) + " game!"
            emit('hitGame', {'msg':"\n--------------Another Game!--------------\n" , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
            # playerAcards = []
            # playerBcards = []
            playerAcards.clear()
            playerBcards.clear()
            playerA.reset()
            playerB.reset()

            Ainitialcards = playerA.distribute_cards()
            AinitialcardsFirst = Ainitialcards[0]
            AinitialcardsSecond = Ainitialcards[1]
       
            Binitialcards = playerB.distribute_cards()
            BinitialcardsFirst = Binitialcards[0]
            BinitialcardsSecond = Binitialcards[1]
        

            # playerAcards = playerA.cards
            # playerBcards = playerB.cards
            playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
            playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
            emit('startGame', {'msg': RoomUsersArray[0] + " has cards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n" +
        RoomUsersArray[1] + " has cards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,
        
        'AinitialcardsFirst': AinitialcardsFirst,
        'AinitialcardsSecond': AinitialcardsSecond,
        'BinitialcardsFirst':BinitialcardsFirst,
        'BinitialcardsSecond': BinitialcardsSecond}, room = room)

        if (sum(playerB.cards) > 21):
            # playerAnewcard = RoomUsersArray[0]  + " wins"
            # playerBnewcard = RoomUsersArray[1]  + " loses"
            playerAnewcard = "x"
            playerBnewcard = "x"  
            GameOver = 0
            keyfordicdic = str(room)
            TotalGameCountArray = TotalGameCountArrayDict.get(keyfordicdic)
            if (TotalGameCountArray is None):
                TotalGameCountArray = []
                # TotalGameCountArray.append(1)
                tempdicdic = {keyfordicdic: TotalGameCountArray}
                TotalGameCountArrayDict.update(tempdicdic)

            TotalGameCountArray.append(1)       
            tempwinner = RoomUsersArray[0] + " wins!" + " <#" + str(len(TotalGameCountArray) + 1) + " game>"
            emit('hitGame', {'msg':RoomUsersArray[0] + " wins! " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard
            , 'tempwinner':tempwinner}, room = room)
            #Update user's score based on their usernames and output it.
            playerAscore = UserScoreTrackerDict.get(RoomUsersArray[0])
            playerBscore = UserScoreTrackerDict.get(RoomUsersArray[1])
            playerAscore += 1
            tempdic = {RoomUsersArray[0]: playerAscore}
            UserScoreTrackerDict.update(tempdic)


            tempdicdic = {keyfordicdic: TotalGameCountArray}
            TotalGameCountArrayDict.update(tempdicdic)
            TotalGameCountArray = TotalGameCountArrayDict.get(room)
            print(TotalGameCountArrayDict)
            print(TotalGameCountArray)
            print(len(TotalGameCountArray))
            whowins = ""
            #Connect to databse
            conwins = sqlite3.connect("scoreboard.db")
            curwins = conwins.cursor()

            con = sqlite3.connect("users.db")
            cur = con.cursor()

            conmoney = sqlite3.connect("moneyboard.db")
            curmoney = conmoney.cursor()

            if (len(TotalGameCountArray) == 21):
                
                if (playerAscore > playerBscore):
                    whowins = RoomUsersArray[0]
                    #get the amount the user has temporarily betted.
                    winner = str(RoomUsersArray[0])
                    loser = str(RoomUsersArray[1])
                    tempBetwinner = int(usersBetsTempDictionary[winner])
                    tempBetloser = int(usersBetsTempDictionary[loser])
                    
                    curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                    userswins = curwins.fetchone()
                    usertotalwins = str(userswins[0])
                    if (usertotalwins is None):
                        usertotalwins = "1"
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()
                    else:
                        usertotalwins = int(usertotalwins) + 1
                        usertotalwins = str(usertotalwins)
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()

                    curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                    usermoney = curmoney.fetchone()
                    usertotalmoney = str(usermoney[0])
                    usertotalmoney = int(usertotalmoney) + tempBetwinner
                    usertotalmoney = str(usertotalmoney)
                    curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                    conmoney.commit()

                    print(tempBetwinner)
                    print(tempBetloser)
                    #for winner:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                    con.commit()
                    
                    #for loser:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                    con.commit()

                elif(playerAscore < playerBscore):
                    whowins = RoomUsersArray[1]
                    winner = str(RoomUsersArray[1])
                    loser = str(RoomUsersArray[0])
                    tempBetwinner = int(usersBetsTempDictionary[winner])
                    tempBetloser = int(usersBetsTempDictionary[loser])

                    curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                    userswins = curwins.fetchone()
                    usertotalwins = str(userswins[0])
                    if (usertotalwins is None):
                        usertotalwins = "1"
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()
                    else:
                        usertotalwins = int(usertotalwins) + 1
                        usertotalwins = str(usertotalwins)
                        curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                        conwins.commit()

                    curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                    usermoney = curmoney.fetchone()
                    usertotalmoney = str(usermoney[0])
                    usertotalmoney = int(usertotalmoney) + tempBetwinner
                    usertotalmoney = str(usertotalmoney)
                    curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                    conmoney.commit()

                    print(tempBetwinner)
                    print(tempBetloser)
                    #for winner:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                    con.commit()
                    
                    #for loser:
                    cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                    curusertoken = cur.fetchone()
                    curusertoken = curusertoken[0]
                    loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                    cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                    con.commit()
                GameOver = 1
                    #Todo: Give player A's money to player B
                print('GAME FINISHED')


            emit('stayGame', {'msg':"Score: " + RoomUsersArray[0] + " <" + str(playerAscore) + "> " + " - v.s. - " +  RoomUsersArray[1] + " <" + str(playerBscore)  + "> " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,
            'playerAscore': playerAscore, 'playerBscore':playerBscore, 'GameOver': GameOver, 'whowins':whowins}, room = room)
            
            # tempwinner = "#" + len(TotalGameCountArray) + " game!"
            emit('hitGame', {'msg':"\n--------------Another Game!--------------\n" , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
            # playerAcards = []
            # playerBcards = []
            playerAcards.clear()
            playerBcards.clear()
            playerA.reset()
            playerB.reset()
            Ainitialcards = playerA.distribute_cards()
            AinitialcardsFirst = Ainitialcards[0]
            AinitialcardsSecond = Ainitialcards[1]
       
            Binitialcards = playerB.distribute_cards()
            BinitialcardsFirst = Binitialcards[0]
            BinitialcardsSecond = Binitialcards[1]
            # playerAcards = playerA.cards
            # playerBcards = playerB.cards
            playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
            playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
            emit('startGame', {'msg': RoomUsersArray[0] + " has cards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n" +
        RoomUsersArray[1] + " has cards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n" , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,
        'AinitialcardsFirst': AinitialcardsFirst,
        'AinitialcardsSecond': AinitialcardsSecond,
        'BinitialcardsFirst':BinitialcardsFirst,
        'BinitialcardsSecond': BinitialcardsSecond}, room = room)
    else:
        playerAnewcard = "Please Wait..."
        playerBnewcard = "Please Wait..."
        emit('hitGame', {'msg': "\nCan't Hit right now! Waiting for another player to join...\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)


@socketio.on('stay', namespace='/blackJack')
def stay(message):
    room = session.get('room')
    playerwhoStays = session.get('username')
    RoomUsersArray = UserInRoomsDict.get(str(room))
    playerBnewcard =  ""
    playerAnewcard = ""
    if (len(RoomUsersArray) == 2):
        if (str(playerwhoStays) == RoomUsersArray[0]):
            playerBnewcard =  RoomUsersArray[1] + "'s turn"
            playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
            playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
            emit('stayGame', {'msg':RoomUsersArray[0] + " stayed! " + "\ncards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n",'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
            playerA.stay = 1
        if (str(playerwhoStays) == RoomUsersArray[1]):
            playerAnewcard = RoomUsersArray[0] + "'s turn"
            playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
            playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
            emit('stayGame', {'msg':RoomUsersArray[1] + " stayed! " + "\ncards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n",'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
            playerB.stay = 1
            # if (sum(playerB.cards) > 22):
            #     emit('stayGame', {'msg':RoomUsersArray[0] + " wins! "}, room = room)
            # if (playerAStay == 1):
            #     #See who wins.
            #     if(sum(playerB.cards) > sum(playerA.cards) and sum(playerB.cards) < 22):
            #          emit('stayGame', {'msg':RoomUsersArray[1] + " wins! "}, room = room)
        
        print("here before checking...")
        print("playerAcards sum - ", sum(playerA.cards))
       
        if (playerA.stay == 1 and playerB.stay == 1):
            #Check who wins.
            playerAnewcard = ""
            playerBnewcard = ""
            if(sum(playerA.cards) > sum(playerB.cards) and sum(playerA.cards) < 22):
                # playerAnewcard = RoomUsersArray[0]  + " wins"
                # playerBnewcard = RoomUsersArray[1]  + " loses"
                playerAnewcard = "x"
                playerBnewcard = "x"
                GameOver = 0
                keyfordicdic = str(room)
                TotalGameCountArray = TotalGameCountArrayDict.get(keyfordicdic)
                if (TotalGameCountArray is None):
                    TotalGameCountArray = []
                    # TotalGameCountArray.append(1)
                    tempdicdic = {keyfordicdic: TotalGameCountArray}
                    TotalGameCountArrayDict.update(tempdicdic)

                TotalGameCountArray.append(1)
                tempwinner = RoomUsersArray[0] + " wins!" + " <#" + str(len(TotalGameCountArray) + 1) + " game>"
                emit('stayGame', {'msg':RoomUsersArray[0] + " wins! ",'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard, 'tempwinner':tempwinner}, room = room)
                #Update user's score based on their usernames and output it.
                playerAscore = UserScoreTrackerDict.get(RoomUsersArray[0])
                playerBscore = UserScoreTrackerDict.get(RoomUsersArray[1])
                playerAscore += 1
                tempdic = {RoomUsersArray[0]: playerAscore}
                UserScoreTrackerDict.update(tempdic)

                
                tempdicdic = {keyfordicdic: TotalGameCountArray}
                TotalGameCountArrayDict.update(tempdicdic)
                TotalGameCountArray = TotalGameCountArrayDict.get(room)
                print(TotalGameCountArrayDict)
                print(TotalGameCountArray)
                
                print(len(TotalGameCountArray))
                whowins = ""
                #Connect to databse

                conwins = sqlite3.connect("scoreboard.db")
                curwins = conwins.cursor()

                con = sqlite3.connect("users.db")
                cur = con.cursor()

                conmoney = sqlite3.connect("moneyboard.db")
                curmoney = conmoney.cursor()

                if (len(TotalGameCountArray) == 21):
                    if (playerAscore > playerBscore):

                        whowins = RoomUsersArray[0]
                        #get the amount the user has temporarily betted.
                        winner = str(RoomUsersArray[0])
                        loser = str(RoomUsersArray[1])
                        tempBetwinner = int(usersBetsTempDictionary[winner])
                        tempBetloser = int(usersBetsTempDictionary[loser])

                        curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                        userswins = curwins.fetchone()
                        usertotalwins = str(userswins[0])
                        if (usertotalwins is None):
                            usertotalwins = "1"
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        else:
                            usertotalwins = int(usertotalwins) + 1
                            usertotalwins = str(usertotalwins)
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        
                        curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                        usermoney = curmoney.fetchone()
                        usertotalmoney = str(usermoney[0])
                        usertotalmoney = int(usertotalmoney) + tempBetwinner
                        usertotalmoney = str(usertotalmoney)
                        curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                        conmoney.commit()

                        #for winner:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                        con.commit()
                        
                        #for loser:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                        con.commit()
                    elif(playerAscore < playerBscore):
                        whowins = RoomUsersArray[1]
                        winner = str(RoomUsersArray[1])
                        loser = str(RoomUsersArray[0])
                        tempBetwinner = int(usersBetsTempDictionary[winner])
                        tempBetloser = int(usersBetsTempDictionary[loser])

                        curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                        userswins = curwins.fetchone()
                        usertotalwins = str(userswins[0])
                        if (usertotalwins is None):
                            usertotalwins = "1"
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        else:
                            usertotalwins = int(usertotalwins) + 1
                            usertotalwins = str(usertotalwins)
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()

                        curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                        usermoney = curmoney.fetchone()
                        usertotalmoney = str(usermoney[0])
                        usertotalmoney = int(usertotalmoney) + tempBetwinner
                        usertotalmoney = str(usertotalmoney)
                        curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                        conmoney.commit()

                        #for winner:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                        con.commit()
                        #for loser:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                        con.commit()
                    
                    GameOver = 1
                    #Todo: Give player A's money to player B
                    print('GAME FINISHED')

                emit('stayGame', {'msg':"Score: " + RoomUsersArray[0] + " <" + str(playerAscore) + "> " + " - v.s. - " +  RoomUsersArray[1] + " <" + str(playerBscore)  + "> " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,'playerAscore': playerAscore, 'playerBscore':playerBscore, 'GameOver':GameOver, 'whowins':whowins}, room = room)

                
                # tempwinner = "#" + len(TotalGameCountArray) + " game!"
                emit('hitGame', {'msg':"\n--------------Another Game!--------------\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
                playerAcards.clear()
                playerBcards.clear()
                playerA.reset()
                playerB.reset()
                Ainitialcards = playerA.distribute_cards()
                AinitialcardsFirst = Ainitialcards[0]
                AinitialcardsSecond = Ainitialcards[1]
       
                Binitialcards = playerB.distribute_cards()
                BinitialcardsFirst = Binitialcards[0]
                BinitialcardsSecond = Binitialcards[1]
                # playerAcards = playerA.cards
                # playerBcards = playerB.cards
                playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
                playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
                emit('startGame', {'msg': RoomUsersArray[0] + " has cards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n" +
        RoomUsersArray[1] + " has cards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,
        'AinitialcardsFirst': AinitialcardsFirst,
        'AinitialcardsSecond': AinitialcardsSecond,
        'BinitialcardsFirst':BinitialcardsFirst,
        'BinitialcardsSecond': BinitialcardsSecond}, room = room)
            if(sum(playerA.cards) < sum(playerB.cards) and sum(playerA.cards) < 22):
                # playerAnewcard = RoomUsersArray[0]  + " loses"
                # playerBnewcard = RoomUsersArray[1]  + " wins"
                playerAnewcard = "x"
                playerBnewcard = "x"
                GameOver = 0
                keyfordicdic = str(room)
                TotalGameCountArray = TotalGameCountArrayDict.get(keyfordicdic)
                if (TotalGameCountArray is None):
                    TotalGameCountArray = []
                    # TotalGameCountArray.append(1)
                    tempdicdic = {keyfordicdic: TotalGameCountArray}
                    TotalGameCountArrayDict.update(tempdicdic)
                
                TotalGameCountArray.append(1)
                tempwinner = RoomUsersArray[1] + " wins!" + " <#" + str(len(TotalGameCountArray) + 1) + " game>"
                emit('stayGame', {'msg':RoomUsersArray[1] + " wins! ",'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard, 'tempwinner':tempwinner}, room = room)
                #Update user's score based on their usernames and output it.
                playerAscore = UserScoreTrackerDict.get(RoomUsersArray[0])
                playerBscore = UserScoreTrackerDict.get(RoomUsersArray[1])
                playerBscore += 1
                tempdic = {RoomUsersArray[1]: playerBscore}
                UserScoreTrackerDict.update(tempdic)

            
                tempdicdic = {keyfordicdic: TotalGameCountArray}
                TotalGameCountArrayDict.update(tempdicdic)
                TotalGameCountArray = TotalGameCountArrayDict.get(room)
                print(TotalGameCountArrayDict)
                print(TotalGameCountArray)
                print(len(TotalGameCountArray))
                whowins = ""
                #Connect to databse

                conwins = sqlite3.connect("scoreboard.db")
                curwins = conwins.cursor()

                con = sqlite3.connect("users.db")
                cur = con.cursor()

                conmoney = sqlite3.connect("moneyboard.db")
                curmoney = conmoney.cursor()

                if (len(TotalGameCountArray) == 21):
                    if (playerAscore > playerBscore):
                        whowins = RoomUsersArray[0]
                        #get the amount the user has temporarily betted.
                        winner = str(RoomUsersArray[0])
                        loser = str(RoomUsersArray[1])
                        tempBetwinner = int(usersBetsTempDictionary[winner])
                        tempBetloser = int(usersBetsTempDictionary[loser])

                        curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                        userswins = curwins.fetchone()
                        usertotalwins = str(userswins[0])
                        if (usertotalwins is None):
                            usertotalwins = "1"
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        else:
                            usertotalwins = int(usertotalwins) + 1
                            usertotalwins = str(usertotalwins)
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()

                        curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                        usermoney = curmoney.fetchone()
                        usertotalmoney = str(usermoney[0])
                        usertotalmoney = int(usertotalmoney) + tempBetwinner
                        usertotalmoney = str(usertotalmoney)
                        curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                        conmoney.commit()

                        print(tempBetwinner)
                        print(tempBetloser)
                        #for winner:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                        con.commit()
                        #for loser:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                        con.commit()
                    elif(playerAscore < playerBscore):
                        whowins = RoomUsersArray[1]
                        winner = str(RoomUsersArray[1])
                        loser = str(RoomUsersArray[0])
                        tempBetwinner = int(usersBetsTempDictionary[winner])
                        tempBetloser = int(usersBetsTempDictionary[loser])
                        curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                        userswins = curwins.fetchone()
                        usertotalwins = str(userswins[0])
                        if (usertotalwins is None):
                            usertotalwins = "1"
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        else:
                            usertotalwins = int(usertotalwins) + 1
                            usertotalwins = str(usertotalwins)
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        
                        curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                        usermoney = curmoney.fetchone()
                        usertotalmoney = str(usermoney[0])
                        usertotalmoney = int(usertotalmoney) + tempBetwinner
                        usertotalmoney = str(usertotalmoney)
                        curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                        conmoney.commit()

                        print(tempBetwinner)
                        print(tempBetloser)
                        #for winner:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                        con.commit()
                        #for loser:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                        con.commit()
                    
                    GameOver = 1
                    #Todo: Give player A's money to player B
                    print('GAME FINISHED')

                emit('stayGame', {'msg':"Score: " + RoomUsersArray[0] + " <" + str(playerAscore) + "> " + " - v.s. - " +  RoomUsersArray[1] + " <" + str(playerBscore)  + "> " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,'playerAscore': playerAscore, 'playerBscore':playerBscore, 'GameOver':GameOver, 'whowins':whowins}, room = room)
                
                
                # tempwinner = "#" + len(TotalGameCountArray) + " game!"
                emit('hitGame', {'msg':"\n--------------Another Game!--------------\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
                playerAcards.clear()
                playerBcards.clear()
                playerA.reset()
                playerB.reset()
                Ainitialcards = playerA.distribute_cards()
                AinitialcardsFirst = Ainitialcards[0]
                AinitialcardsSecond = Ainitialcards[1]
       
                Binitialcards = playerB.distribute_cards()
                BinitialcardsFirst = Binitialcards[0]
                BinitialcardsSecond = Binitialcards[1]
                # playerAcards = playerA.cards
                # playerBcards = playerB.cards
                playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
                playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
                emit('startGame', {'msg': RoomUsersArray[0] + " has cards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n" +
        RoomUsersArray[1] + " has cards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard, 
        'AinitialcardsFirst': AinitialcardsFirst,
        'AinitialcardsSecond': AinitialcardsSecond,
        'BinitialcardsFirst':BinitialcardsFirst,
        'BinitialcardsSecond': BinitialcardsSecond}, room = room)
            if(sum(playerA.cards) == sum(playerB.cards) and sum(playerA.cards) < 22):
                # playerAnewcard = RoomUsersArray[0]  + " ties"
                # playerBnewcard = RoomUsersArray[1]  + " ties"
                GameOver = 0
                keyfordicdic = str(room)
                TotalGameCountArray = TotalGameCountArrayDict.get(keyfordicdic)
                if (TotalGameCountArray is None):
                    TotalGameCountArray = []
                    # TotalGameCountArray.append(1)
                    tempdicdic = {keyfordicdic: TotalGameCountArray}
                    TotalGameCountArrayDict.update(tempdicdic)
                TotalGameCountArray.append(1)
                tempwinner = RoomUsersArray[1] + RoomUsersArray[0] + " ties! " + " <#" + str(len(TotalGameCountArray) + 1) + " game>"
                playerAnewcard = "x"
                playerBnewcard = "x"
                emit('stayGame', {'msg':RoomUsersArray[1] + " and " + RoomUsersArray[0] + " ties! ",'playerBnewcard': playerBnewcard,'playerAnewcard': playerAnewcard, 'tempwinner':tempwinner}, room = room)
                #Update user's score based on their usernames and output it.
                playerAscore = UserScoreTrackerDict.get(RoomUsersArray[0])
                playerBscore = UserScoreTrackerDict.get(RoomUsersArray[1])
                
                tempdicdic = {keyfordicdic: TotalGameCountArray}
                TotalGameCountArrayDict.update(tempdicdic)
                TotalGameCountArray = TotalGameCountArrayDict.get(room)
                print(TotalGameCountArrayDict)
                print(TotalGameCountArray)
                print(len(TotalGameCountArray))

                whowins = ""
                conwins = sqlite3.connect("scoreboard.db")
                curwins = conwins.cursor()

                #Connect to databse
                con = sqlite3.connect("users.db")
                cur = con.cursor()

                conmoney = sqlite3.connect("moneyboard.db")
                curmoney = conmoney.cursor()
                if (len(TotalGameCountArray) == 21):
                    if (playerAscore > playerBscore):
                        whowins = RoomUsersArray[0]
                        #get the amount the user has temporarily betted.
                        winner = str(RoomUsersArray[0])
                        loser = str(RoomUsersArray[1])
                        tempBetwinner = int(usersBetsTempDictionary[winner])
                        tempBetloser = int(usersBetsTempDictionary[loser])

                        curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                        userswins = curwins.fetchone()
                        usertotalwins = str(userswins[0])
                        if (usertotalwins is None):
                            usertotalwins = "1"
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        else:
                            usertotalwins = int(usertotalwins) + 1
                            usertotalwins = str(usertotalwins)
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        
                        curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                        usermoney = curmoney.fetchone()
                        usertotalmoney = str(usermoney[0])
                        usertotalmoney = int(usertotalmoney) + tempBetwinner
                        usertotalmoney = str(usertotalmoney)
                        curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                        conmoney.commit()

                        print(tempBetwinner)
                        print(tempBetloser)
                        #for winner:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                        con.commit()

                        #for loser:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                        con.commit()
                        
                    elif(playerAscore < playerBscore):
                        whowins = RoomUsersArray[1]
                        winner = str(RoomUsersArray[1])
                        loser = str(RoomUsersArray[0])
                        tempBetwinner = int(usersBetsTempDictionary[winner])
                        tempBetloser = int(usersBetsTempDictionary[loser])

                        curwins.execute(f"SELECT wins from user_scoreboard WHERE username='{winner}';")
                        userswins = curwins.fetchone()
                        usertotalwins = str(userswins[0])
                        if (usertotalwins is None):
                            usertotalwins = "1"
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        else:
                            usertotalwins = int(usertotalwins) + 1
                            usertotalwins = str(usertotalwins)
                            curwins.execute(f"UPDATE user_scoreboard SET wins = '{usertotalwins}' WHERE username = '{winner}';")
                            conwins.commit()
                        
                        curmoney.execute(f"SELECT moneygained from monday_board WHERE username='{winner}';")
                        usermoney = curmoney.fetchone()
                        usertotalmoney = str(usermoney[0])
                        usertotalmoney = int(usertotalmoney) + tempBetwinner
                        usertotalmoney = str(usertotalmoney)
                        curmoney.execute(f"UPDATE monday_board SET moneygained = '{usertotalmoney}' WHERE username = '{winner}';")
                        conmoney.commit()

                        #for winner:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{winner}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        winnerfinaltokencount = tempBetwinner + curusertoken + tempBetloser
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{winnerfinaltokencount}' WHERE username = '{winner}';")
                        con.commit()

                        #for loser:
                        cur.execute(f"SELECT playertokens from UserInfo WHERE username='{loser}';")
                        curusertoken = cur.fetchone()
                        curusertoken = curusertoken[0]
                        loserfinaltokencount = tempBetloser + curusertoken - tempBetwinner
                        cur.execute(f"UPDATE UserInfo SET playertokens = '{loserfinaltokencount}' WHERE username = '{loser}';")
                        con.commit()
                   
                    GameOver = 1
                    #Todo: Give player A's money to player B
                    print('GAME FINISHED')

                emit('stayGame', {'msg':"Score: " + RoomUsersArray[0] + " <" + str(playerAscore) + "> " + " - v.s. - " +  RoomUsersArray[1] + " <" + str(playerBscore)  + "> " , 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,'playerAscore': playerAscore, 'playerBscore':playerBscore, 'GameOver':GameOver, 'whowins':whowins}, room = room)

                
                # tempwinner = "#" + len(TotalGameCountArray) + " game!"
                emit('hitGame', {'msg':"\n--------------Another Game!--------------\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard}, room = room)
                playerAcards.clear()
                playerBcards.clear()
                playerA.reset()
                playerB.reset()
                Ainitialcards = playerA.distribute_cards()
                AinitialcardsFirst = Ainitialcards[0]
                AinitialcardsSecond = Ainitialcards[1]
       
                Binitialcards = playerB.distribute_cards()
                BinitialcardsFirst = Binitialcards[0]
                BinitialcardsSecond = Binitialcards[1]
                # playerAcards = playerA.cards
                # playerBcards = playerB.cards
                playerAcardsOut = ' '.join(str(e) for e in playerA.cards)
                playerBcardsOut = ' '.join(str(e) for e in playerB.cards)
                emit('startGame', {'msg': RoomUsersArray[0] + " has cards: [" + playerAcardsOut + "] count: <" + str(sum(playerA.cards)) + ">\n" +
        RoomUsersArray[1] + " has cards: [" + playerBcardsOut + "] count: <" + str(sum(playerB.cards)) + ">\n", 'playerAnewcard': playerAnewcard, 'playerBnewcard': playerBnewcard,
        'AinitialcardsFirst': AinitialcardsFirst,
        'AinitialcardsSecond': AinitialcardsSecond,
        'BinitialcardsFirst':BinitialcardsFirst,
        'BinitialcardsSecond': BinitialcardsSecond}, room = room)

    else:
        playerAnewcard = "Please Wait..."
        playerBnewcard = "Please Wait..."
        emit('stayGame', {'msg': "\nCan't stay right now! Waiting for another player to join...\n",'playerBnewcard': playerBnewcard,'playerAnewcard': playerAnewcard,}, room = room)

# ------------SESSION SERVER HERE------------ #

if __name__ == '__main__':
    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    socketio.run(app, port=port)
    #app.run(use_reloader=False, debug=True, port=port) 
