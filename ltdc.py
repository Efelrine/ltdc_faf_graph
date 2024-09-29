#!/usr/bin/python3
# coding: utf-8
import unidecode
import requests
import re

from graphviz import Digraph
from cookie import Cookie
from constants import *


class Edge:
    first_node = ''
    second_node = ''
    color = ''
    dirType = ''


def to_nom_graph(nom):
    """
    Converti un nom au format nom graph.
    :param nom: le nom a convertir
    :return:  le nom graph
    """
    nom_graph_tmp = unidecode.unidecode(nom)
    nom_graph = ''
    for a in nom_graph_tmp:
        if a.isalpha():
            nom_graph += a
    return nom_graph


def get_link_list(string):
    """
    :param string: la string a parser
    :return: la liste des liens "<a>" contenue dans la string
    """
    links_tmp = re.findall(r'<a href="([^"]*)"[^<]*</a>', string)
    links = []
    for link in links_tmp:
        links.append("https://louiki.elyseum.fr" + link)
    return links


def retreive_main_table(url):
    """
    Récupère le tableau principal d'une page
    :param url: l'url de la page
    :return: la liste double des lignes et cellule du tableau
    """
    page = requests.get(url, headers=Cookie.cookie).text
    table = page.split("<table class=\"wikitable sortable\">")
    table.pop(0)
    table = table[0].split("</table>")
    # On nettoie les fins de cellule et fin de ligne.
    table = table[0].split("<tr>")
    table.pop(0)
    # La 1ère ligne est la ligne de titre du tableau
    table.pop(0)

    tmp_table = []
    for row in table:
        row = row.replace("\n</td>\n", "").replace("\n</td></tr>\n", "")
        row = row.split("<td>")
        row.pop(0)
        tmp_table.append(row)
    return tmp_table


def retreive_groupes():
    """
    :return: un tableau des groupes
    """
    tableau_groupes = retreive_main_table("https://louiki.elyseum.fr/gn_ltdc/index.php/Graphe_Groupes")
    groupes = []
    for p in tableau_groupes:
        groupe = Groupe()
        groupe.lien = get_link_list(p[0])[0]
        groupe.nom = p[1]
        groupe.nom_graph = to_nom_graph(p[1])
        groupe.groupe = get_link_list(p[2])
        groupe.entente = get_link_list(p[3])
        groupe.neutre = get_link_list(p[4])
        groupe.opposition = get_link_list(p[5])
        groupes.append(groupe)
    return groupes


def retreive_personnages():
    """
    :return: un tableau des personnages
    """
    tableau_personnages = retreive_main_table("https://louiki.elyseum.fr/gn_ltdc/index.php/Graphe_Personnages")
    personnages = []
    for p in tableau_personnages:
        perso = Personnage()
        perso.lien = get_link_list(p[0])[0]
        perso.nom = p[1]
        perso.nom_graph = to_nom_graph(p[1])
        perso.groupe = get_link_list(p[2])
        perso.asso = get_link_list(p[3])
        perso.famille = get_link_list(p[4])
        perso.entente = get_link_list(p[5])
        perso.neutre = get_link_list(p[6])
        perso.opposition = get_link_list(p[7])
        perso.joueur = p[9]
        personnages.append(perso)
    return personnages


def add_nodes_types_shape(dot, entries):
    """
    Ajoute les entrées au graph
    :param dot: le graph
    :param entries: une liste d'entrée a ajouter dans le graph
    """
    for e in entries:
        color = Color.WHITE
        if isinstance(e, Personnage):
            if 'PNJ' in e.joueur:
                color = Color.PNJ_COLOR
            elif 'Absent' in e.joueur:
                color = Color.ABSENT_COLOR
        dot.node(e.nom_graph, e.nom, href=e.lien, style='filled',
                 shape=NodeType.node_shapes.get(e.__class__),
                 peripheries=NodeType.node_peripheries.get(e.__class__), fillcolor=color)


def add_edges(dot, edges_map):
    """
    Ajoute les arrêtes du graphe.
    :param dot: le graph
    :param edges_map: le dictionnaire des edges
    """
    for e in edges_map.items():
        edge = e[1]
        dot.edge(edge.first_node, edge.second_node, color=edge.color, dir=edge.dirType)


def build_link_to_nom_graph_dict(*entries_list):
    """
    Construit le dictionnaire des liens -> nom_graph
    :param entries_list: un tableau de liste d'entrée
    :return: le dictionnaire construit
    """
    link_to_nom_graph = {}
    for el in entries_list:
        for e in el:
            link_to_nom_graph[e.lien] = e.nom_graph
    return link_to_nom_graph


def create_edge(edges_map, link_to_nomgraph, first_node, second_node_link, color, dir_arrow=''):
    """
    Créé un lien(edge) dans le dictionnaire
    :param edges_map: le dictionnaire des liens
    :param link_to_nomgraph: le dictionnaire de lien nom graph
    :param first_node: le premier noeud
    :param second_node_link: le lien du second noeud
    :param color: la couleur
    :param dir_arrow: (optionel) la direction de la flêche.
    """
    if second_node_link in link_to_nomgraph:
        second_node = link_to_nomgraph.get(second_node_link)
        edge = Edge()
        edge.color = color
        if first_node < second_node:
            edge.first_node = first_node
            edge.second_node = second_node
            if dir_arrow == ArrowDir.NONE:
                edge.dirType = dir_arrow
            else:
                edge.dirType = ArrowDir.FORWARD
        else:
            edge.first_node = second_node
            edge.second_node = first_node
            if dir_arrow == ArrowDir.NONE:
                edge.dirType = dir_arrow
            else:
                edge.dirType = ArrowDir.BACK
        key = edge.first_node + edge.second_node + edge.color
        if key in edges_map:
            edge = edges_map[key]
            if edge.dirType != ArrowDir.NONE:
                edge.dirType = ArrowDir.BOTH
        else:
            edges_map[key] = edge
    else:
        print("Erreur : aucune page pour le lien '" + second_node_link + "' pour l'entitée '" + first_node + "'")


def build_edges_dict_groupes(edges_map, link_to_nomgraph, groupes):
    """
    Complète le dictionnaire des arrêtes
    :param edges_map: dictionnaire des arrêtes
    :param link_to_nomgraph: dictionnaire lien vers nom_graph
    :param groupes: ensemble des groupes
    """
    for e in groupes:
        for node in e.entente:
            create_edge(edges_map, link_to_nomgraph, e.nom_graph, node, Color.ENTENTE_COLOR)
        for node in e.neutre:
            create_edge(edges_map, link_to_nomgraph, e.nom_graph, node, Color.NEUTRAL_COLOR)
        for node in e.opposition:
            create_edge(edges_map, link_to_nomgraph, e.nom_graph, node, Color.OPPOSITION_COLOR)
        for node in e.groupe:
            create_edge(edges_map, link_to_nomgraph, e.nom_graph, node, Color.BLACK, ArrowDir.NONE)


def build_edges_dict(link_to_nomgraph, personnages, groupes):
    """
    Construit le dictionnaire des arrêtes
    :param link_to_nomgraph: dictionnaire lien vers nom_graph
    :param personnages: ensemble des persoonages
    :param groupes: ensemble des groupes
    :return: le dictionnaire construit
    """
    edges_map = {}
    build_edges_dict_groupes(edges_map, link_to_nomgraph, groupes)
    build_edges_dict_groupes(edges_map, link_to_nomgraph, personnages)
    for e in personnages:
        for node in e.asso:
            create_edge(edges_map,  link_to_nomgraph, e.nom_graph, node, Color.BLACK, ArrowDir.NONE)
        for node in e.famille:
            create_edge(edges_map,  link_to_nomgraph, e.nom_graph, node, Color.FAMILLE_COLOR)
    return edges_map


def main():
    """
    Main
    """
    print("Content-type: text/html\r\n\r\n")

    personnages = retreive_personnages()
    groupes = retreive_groupes()

    link_to_nomgraph = build_link_to_nom_graph_dict(personnages, groupes)
    edges_map = build_edges_dict(link_to_nomgraph, personnages, groupes)

    dot = Digraph(name='GrapheTdCPersos', filename='./tmp/gnTdc', comment='La fleur au Fusil', engine='sfdp')
    add_nodes_types_shape(dot, personnages)
    add_nodes_types_shape(dot, groupes)

    add_edges(dot, edges_map)

    dot.save()
    dot.format = 'svg'
    dot.render(directory='.').replace('\\', '/')

    print("done")


main()
