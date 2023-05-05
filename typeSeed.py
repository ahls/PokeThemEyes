"""Poke the Eyes application."""
from flask import Flask, request, render_template,redirect, flash, session, jsonify
import requests
#from flask_debugtoolbar import DebugToolBarExtension
from models import db, connect_db, Pokemon, Type, TypeToTypeRelation,PokemonTypes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///poketheeyes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'hehe123'

#debug= DebugToolBarExtension(app)
connect_db(app)
with app.app_context():
    db.create_all()

