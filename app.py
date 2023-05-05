"""Poke the Eyes application."""
from flask import Flask, request, render_template,redirect, flash, session, jsonify
import requests
#from flask_debugtoolbar import DebugToolBarExtension
from models import db, connect_db, Pokemon, Type, TypeToTypeRelation,PokemonTypes
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///poketheeyes')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','mul ggoraba')

#debug= DebugToolBarExtension(app)
connect_db(app)
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET','POST'])
def homepage():
    name = request.form.get('name',None)
    pokemon = None
    if name != None:
        #search if the pokemon is in the database
        pokemon = Pokemon.query.filter(Pokemon.name == name).first()
        if pokemon == None:
            # if pokemon does not exist, try to fetch from the server.
            res = requests.get(f'https://pokeapi.co/api/v2/pokemon/{name}')
            if res.status_code == 200:
                # if the data was successfully recieved, create pokemon data and set it to pokemon
                results = res.json()
                pokemon = Pokemon(id = results['id'], name = results['name'],imagePath = results['sprites']['front_default'])
                db.session.add(pokemon)
                db.session.commit()
                for tpe in results['types']:
                    pkType = PokemonTypes(pokemon_id = results['id'],pokemon_type = tpe['type']['name'])
                    db.session.add(pkType)
                    db.session.commit()
    if name != None:
        if pokemon == None:
            #if pokemon is still none after all, return it is not there.
            flash(f'pokemon you are looking for, {name}, does not exist :(')
        else:
            #pokemon was found. calculate all the possible relations
            pkTypes = [x.pokemon_type for x in PokemonTypes.query.filter(PokemonTypes.pokemon_id==pokemon.id).all()]
            a,b = TypeToTypeRelation.CalculateRelation(pkTypes)
            relAtk,relDef,atkMult, defMult = FindBestTypes(a,b)
        return render_template('main.html',pokemon = pokemon, relAtk = relAtk, relDef=relDef, atkMult= atkMult,defMult=defMult)
    return render_template('main.html', pokemon= None)
def FindBestTypes(relAtk,relDef):
    #iterate over all relation attack to find set of highest values
    atkSet=[]
    atkVal=min(relAtk.values())
    for tp, val in relAtk.items():
        if val == atkVal:
            atkSet.append(tp)
    defSet=[]
    defVal=max(relDef.values())
    for tp, val in relDef.items():
        if val == defVal:
            defSet.append(tp)
    return atkSet,defSet, atkVal, defVal
    

def reset():
    db.drop_all()
    db.create_all()

def populateTypes():
    allTypes = dict()
    currentAvailTypeIDs =[x.id for x in Type.query.all()]
    for i in range(19):
        if i in currentAvailTypeIDs:
            print(f'type({i}) already exists')
            continue
        res = requests.get(f'https://pokeapi.co/api/v2/type/{i}')
        if res.status_code != 200:
            print(f'something went wrong while fetching data from the type API (index:{i})')
            continue
        result = res.json()
        dmg_rel = result['damage_relations']
        rel = { 'doubleTo':[x['name'] for x in dmg_rel['double_damage_to']],
                    'doubleFrom':[x['name'] for x in dmg_rel['double_damage_from']],
                    'halfTo':[x['name'] for x in dmg_rel['half_damage_to']],
                    'halfFrom':[x['name'] for x in dmg_rel['half_damage_from']],
                    'zeroTo':[x['name'] for x in dmg_rel['no_damage_to']],
                    'zeroFrom':[x['name'] for x in dmg_rel['no_damage_from']] }
        allTypes[result['name']] = rel
        newType = Type(id = i,name=result['name'])
        db.session.add(newType)
        db.session.commit()
    
    for name,rels in allTypes.items():
        print(f'from:{name},rels:{rels}')
        for typeOther in allTypes.keys():
            dmgTo = 1
            dmgFrom = 1
            if typeOther in rels['doubleTo']:
                dmgTo = 2
            elif typeOther in rels['halfTo']:
                dmgTo = 0.5
            elif typeOther in rels['zeroTo']:
                dmgTo = 0
            if typeOther in rels['doubleFrom']:
                dmgFrom = 2
            elif typeOther in rels['halfFrom']:
                dmgFrom = 0.5
            elif typeOther in rels['zeroFrom']:
                dmgFrom = 0
                
            print(f'from:{name}, to:{typeOther}, dmgTo:{dmgTo}, dmgFrom:{dmgFrom}')
            newRel = TypeToTypeRelation(type_from=name,type_to=typeOther,attack=dmgTo,defense=dmgFrom)
            db.session.add(newRel)
            db.session.commit()
    types = Type.query.all()
    #return render_template('types.html', types = types)

