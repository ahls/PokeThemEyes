"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
def connect_db(app):
    db.app = app
    db.init_app(app)

class Pokemon(db.Model):
    __tablename__ = "pokemons"

    id = db.Column(db.Integer,
                    primary_key = True)
    name = db.Column(db.String(20))
    imagePath = db.Column(db.Text)
    def __repr__(self):
        return f'pokemon:{self.name}({self.id}), imgPath:{self.imagePath}'

class Type(db.Model):
    __tablename__ = "types"
    
    id = db.Column(db.Integer,
                    primary_key = True)
    name = db.Column(db.String(10), unique = True)
    color = db.Column(db.String(10))

class PokemonTypes(db.Model):
    __tablename__ = "pokemontypes"

    pokemon_id = db.Column(db.Integer,db.ForeignKey(Pokemon.id,ondelete="CASCADE"),primary_key =True)
    pokemon_type = db.Column(db.String(10), db.ForeignKey(Type.name, ondelete="CASCADE"), primary_key =True)

class TypeToTypeRelation(db.Model):
    __tablename__ = "typerelations"
    
    type_from = db.Column(db.String(10), db.ForeignKey(Type.name, ondelete="CASCADE"), primary_key =True)
    type_to = db.Column(db.String(10), db.ForeignKey(Type.name, ondelete="CASCADE"), primary_key =True)
    attack = db.Column(db.Float)
    defense = db.Column(db.Float)

    @classmethod
    def CalculateRelation(cls,pokeTypes):
        '''returns calculated type against the given poketypes'''
        allTypes = Type.query.all()
        typeRelationAtk = dict()
        typeRelationDef = dict()
        for eachType in allTypes:
            typeRelationAtk[eachType.name] = 1
            typeRelationDef[eachType.name] = 1
        pokeTypeQuery = TypeToTypeRelation.query.filter(TypeToTypeRelation.type_from.in_(pokeTypes)).all()
        for pokeTypeRelations in pokeTypeQuery:
            typeRelationAtk[pokeTypeRelations.type_to] *= pokeTypeRelations.attack
            typeRelationDef[pokeTypeRelations.type_to] *= pokeTypeRelations.defense
        return typeRelationAtk, typeRelationDef