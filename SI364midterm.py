###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CsrfProtect
from wtforms import StringField, SubmitField, RadioField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy
import requests
import json

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True
CsrfProtect(app)
## All app.config values
app.config['SECRET_KEY'] = 'Token keeps saying missing idk what else to try'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///jakedegmidterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)

######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_user(user_name):
    u = User.query.filter_by(username = user_name).first()
    if u:
        return u
    else:
        u = User(username = user_name)
        db.session.add(u)
        db.session.commit()
        return u

def get_or_create_party(user_name, party_name):
    u = User.query.filter_by(username = user_name).first()
    p = Party.query.filter_by(userID = u.userID, name = party_name).first()
    if p:
        return p
    else:
        p = Party(name = party_name, userID = u.userID)
        db.session.add(p)
        db.session.commit()
        return p

##################
##### MODELS #####
##################

class User(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))

class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    pokemonID = db.Column(db.Integer,primary_key=True)
    idNumber = db.Column(db.Integer)
    name = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    partyID = db.Column(db.Integer, db.ForeignKey('party.partyID'))

class Party(db.Model):
    __tablename__ = 'party'
    partyID = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'))

class Battle(db.Model):
    __tablename__ = 'battle'
    battleID = db.Column(db.Integer,primary_key=True)
    winnerUser = db.Column(db.String(64))
    winnerParty = db.Column(db.Integer)
    loserUser = db.Column(db.String(64))
    loserParty = db.Column(db.Integer)

###################
###### FORMS ######
###################

class UserForm(FlaskForm):
    username = StringField("Please enter your username:",validators=[Required(message="Username required")])
    party = RadioField("Which party would you like to view/edit?", validators=[Required(message="Party number required")], choices=[('1', 'Party 1'), ('2', 'Party 2'),('3', 'Party 3'),('4', 'Party 4'),('5','Party 5')])
    name = StringField("Please enter the name of the Pokemon you would like to add:",validators=[Required(message="Pokemon name required")])
    nickname = StringField("Please enter the nickname you would like to give this Pokemon (if you want to nickname it):")
    def validate_nickname(form, field):
        st = field.data
        if not st.isalpha() and len(st) > 0:
            raise ValidationError('Nickname must contain only letters')
    submit = SubmitField('Submit')

class BattleForm(FlaskForm):
    winnerUser = StringField("Please enter the username of the winner.",validators=[Required(message="Winner username required")])
    winnerParty = StringField("Please enter the party # of the winner.",validators=[Required(message="Winner party # required")])
    loserUser = StringField("Please enter the username of the loser.",validators=[Required(message="Loser username required")])
    loserParty = StringField("Please enter the party # of the winner.",validators=[Required(message="Loser party # required")])
    submit = SubmitField('Submit')

#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def home():
    errors2 = [];
    if request.method == 'GET':
        form = UserForm()
        return render_template("index.html", form = form)
    if request.method == 'POST':
        form = UserForm(request.form)
        if form.validate_on_submit():
            user1 = form.username.data
            party1 = form.party.data
            name = form.name.data
            nickname = form.nickname.data
            if len(nickname) == 0:
                nickname = name
            payload = ""
            search = "https://pokeapi.co/api/v2/pokemon/" + name.lower() + "/"
            response = requests.request("GET", search, data=payload)
            data = json.loads(response.text)
            print(data)
            if 'id' in data.keys():
                u = get_or_create_user(user1)
                p = get_or_create_party(user1, party1)
                inParty = Pokemon.query.filter_by(partyID=p.partyID).all()
                if len(inParty) < 6:
                    poke = Pokemon.query.filter_by(name=name.lower()).first()
                    if poke:
                        temp = True
                        flash("Pokemon has already been added to a party.")
                        return redirect(url_for('see_all_pokemon'))
                    else:
                        poke = Pokemon(partyID=p.partyID, idNumber=data["id"], name=name.lower(), nickname=nickname)
                        db.session.add(poke)
                        db.session.commit()
                else:
                    errors2.append("This party already has 6 Pokemon!")
            else:
                errors2.append("Pokemon not found in database")
    errors = [v for v in form.errors.values()] #Taken from past assignment
    errors3 = errors + errors2
    if len(errors3) > 0:
        flash("!!! ERRORS PRESENT - " + str(errors3))
    return render_template('index.html', form = form)

@app.route('/battle')
def battle():
    if request.method == 'GET':
        form = BattleForm()
        return render_template("battle.html", form = form)

@app.route('/battleGet')
def battleGet():
    form = BattleForm(request.form)
    winner = request.args.get('winnerUser')
    loser = request.args.get('loserUser')
    winner2 = request.args.get('winnerParty')
    loser2 = request.args.get('loserParty')
    battle1 = Battle(winnerUser=winner, loserUser=loser, winnerParty=winner2, loserParty=loser2)
    db.session.add(battle1)
    db.session.commit()
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('battleGet.html',user1=winner, user1party=winner2, user2=loser, user2party=loser2)


#u = request.args.get('username')

@app.route("/allBattles")
def see_all_battles():
    battles = Battle.query.all()
    return render_template('battles.html',battles=battles)

@app.route("/allPkmn")
def see_all_pokemon():
    pokemon = Pokemon.query.all()
    return render_template('pokemon.html',pokemon=pokemon)

@app.route("/allUsers")
def see_all_users():
    users = User.query.all()
    return render_template('users.html',users=users)

@app.route("/allParties")
def see_all_parties():
    users = User.query.all()
    parties = Party.query.all()
    pokemon = Pokemon.query.all()
    return render_template('parties.html',users=users,parties=parties,pokemon=pokemon)

## Code to run the application...
if __name__ == '__main__':
    db.create_all()
    app.run()
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
