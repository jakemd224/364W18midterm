###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
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

def get_or_create_pokemon(pokemon_name, party_id):
    p = Pokemon.query.filter_by(name = party_name).first()
    if p:
        return p
    else:
        p = Pokemon(name = pokemon_name, partyID = party_id)
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
    password = db.Column(db.String(64))

class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    pokemonID = db.Column(db.Integer,primary_key=True)
    idNumber = db.Column(db.Integer)
    name = db.Column(db.String(64))
    partyID = db.Column(db.Integer, db.ForeignKey('party.partyID'))

class Party(db.Model):
    __tablename__ = 'party'
    partyID = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'))


###################
###### FORMS ######
###################

class UserForm(FlaskForm):
    username = StringField("Please enter your username:")
    submit = SubmitField('Submit')

class PartyForm(FlaskForm):
    party = RadioField("Which party would you like to view/edit?", validators=[Required], choices=[('1', 'Party 1'), ('2', 'Party 2'),('3', 'Party 3'),('4', 'Party 4'),('5','Party 5')])
    submit = SubmitField('Submit')

class PkmnForm(FlaskForm):
    name = StringField("Please enter the name of the Pokemon you would like to add:",validators=[Required()])
    nickname = StringField("Please enter the nickname you would like to give this Pokemon:")
    submit = SubmitField('Submit')

#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def home():
    form = UserForm()
    return render_template('index.html',form=form)

@app.route('/partySelect', methods=['POST'])
def party_select():
    form = PartyForm()
    u = request.args.get('username')
    user = get_or_create_user(u)
    return render_template('parties.html',form=form)

@app.route('/party', methods=['GET', 'POST'])
def party_info():
    if request.method == 'GET':
        form = PkmnForm()
        p = request.args.get('party')
        party = get_or_create_party(p, user)
        pokemon = Pokemon.query.filter_by(partyID = party.partyID).all()
        return render_template('party.html', pokemon=pokemon, form=form)
    if request.method == 'POST':



@app.route("/allPkmn")
def see_all_pokemon():
    pokemon = Pokemon.query.all()
    return render_template('pokemon.html',pokemon=pokemon)

@app.route("/allUsers")
def see_all_users():
    users = User.query.all()
    return render_template('users.html',users=users)

## Code to run the application...
if __name__ == '__main__':
    db.create_all()
    app.run()
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
