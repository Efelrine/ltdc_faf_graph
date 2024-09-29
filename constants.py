class Color:
    # vert
    CHOSEN_COLOR = '#98fb98'
    # vert
    ENTENTE_COLOR = '#013d03'
    # rouge sombre
    OPPOSITION_COLOR = '#590202'
    # jaune
    FAMILLE_COLOR = '#9c9405'
    # dark blue
    NEUTRAL_COLOR = '#00008b'
    # bleu pastel
    PNJ_COLOR = '#add8e6'
    # gris
    ABSENT_COLOR = '#808080'
    WHITE = "#ffffff"
    BLACK = "#000000"


class ArrowDir:
    FORWARD = 'forward'
    BACK = 'back'
    BOTH = 'both'
    NONE = 'none'


class Entry:
    lien = ''
    nom = ''
    nom_graph = ''


class Groupe(Entry):
    entente = []
    neutre = []
    opposition = []
    groupe = []


class Personnage(Groupe):
    famille = []
    asso = []
    joueur = 'PJ'


class ViewEdges:
    VIEW_ALL = 'A'
    VIEW_FAMILLE = 'F'
    VIEW_ENTENTE = 'E'
    VIEW_NEUTRAL = 'N'
    VIEW_OPPOSITION = 'O'
    VIEW_GROUPES = 'G'


class NodeType:
    node_peripheries = {
        Personnage: '1',
        Groupe: '1'
    }
    node_shapes = {
        Personnage: 'box',
        Groupe: 'ellipse'
    }
