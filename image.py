#!/usr/bin/python3
# coding: utf-8
import re

from graphviz import Digraph
from constants import *


ENGINE = 'sfdp'


class Edge:
    first_node = ''
    second_node = ''
    label = ''
    fillcolor = ''
    dir = ''


class Node:
    nom_graph = ''
    label = ''
    fillcolor = ''
    link = ''
    peripheries = ''
    shape = ''
    fixed_size = 'false'


class ImageGenerator:
    def get_lignes_graphe_complet(self):
        """
        Récupère la liste des lignes du graphe complet
        :return:  la liste des lignes du graphe complet
        """
        fichier = open('./tmp/gnTdc', encoding='utf8')
        lignes = fichier.readlines()
        fichier.close()
        return lignes

    def add_linked_nodes_by_edges(self, first_node, second_node, nodes, groupe_nodes, temp):
        """
        Ajoute à une liste de nodes les autres nodes liés à ceux dans la liste
        :param first_node: premier node à tester
        :param second_node: second node à tester
        :param nodes: la liste des nodes à partir desquels compléter la liste
        :param groupe_nodes: la liste des nodes correspondant aux groupes
        :param temp: liste temporaire de nodes
        """
        if first_node not in groupe_nodes and second_node not in groupe_nodes:
            if first_node not in nodes and second_node not in temp and second_node in nodes:
                temp.append(first_node)
                nodes.append(first_node)
            elif first_node in nodes and first_node not in temp and second_node not in nodes:
                temp.append(second_node)
                nodes.append(second_node)

    def add_linked_nodes(self, nodes, lignes, view_edges, groupe_nodes=[]):
        """
        Ajoute à une liste de nodes les autres nodes liés à ceux dans la liste
        :param nodes: la liste des nodes à partir desquels compléter la liste
        :param lignes: les lignes du fichier graphe complet
        :param view_edges: le type d'arrêtes à visualiser
        :param groupe_nodes: la liste des nodes correspondant aux groupes
        """
        temp = []
        for l in lignes:
            if '->' in l:
                e = re.findall(r'([a-zA-Z]+) -> ([a-zA-Z]+) \[color="([^\"]*)"', l)
                first_node = e[0][0]
                second_node = e[0][1]
                color = e[0][2]
                if color == Color.ENTENTE_COLOR:
                    if ViewEdges.VIEW_ENTENTE in view_edges:
                        self.add_linked_nodes_by_edges(first_node, second_node, nodes, groupe_nodes, temp)
                elif color == Color.FAMILLE_COLOR:
                    if ViewEdges.VIEW_FAMILLE in view_edges:
                        self.add_linked_nodes_by_edges(first_node, second_node, nodes, groupe_nodes, temp)
                elif color == Color.NEUTRAL_COLOR:
                    if ViewEdges.VIEW_NEUTRAL in view_edges:
                        self.add_linked_nodes_by_edges(first_node, second_node, nodes, groupe_nodes, temp)
                elif color == Color.OPPOSITION_COLOR:
                    if ViewEdges.VIEW_OPPOSITION in view_edges:
                        self.add_linked_nodes_by_edges(first_node, second_node, nodes, groupe_nodes, temp)
                else:
                    if ViewEdges.VIEW_GROUPES in view_edges:
                        self.add_linked_nodes_by_edges(first_node, second_node, nodes, groupe_nodes, temp)

    def build_list_options_persos(self, node_selected, lignes):
        """
        Récupère la map des nodes de persos et leur label dans le graphe complet
        :param node_selected: noeud selectionné
        :param lignes: les lignes du fichier dot
        :return:  la map des nodes de persos
        """
        option_persos = []
        label = ''
        for l in lignes:
            selected = ''
            if 'peripheries=' + NodeType.node_peripheries.get(Personnage) + \
                    ' shape=' + NodeType.node_shapes.get(Personnage) in l:
                n = re.findall(r'([a-zA-Z]+) \[label=("([^\"]*)"|([^ ]*))', l)
                nom_graph = n[0][0]
                if n[0][2]:
                    label = n[0][2]
                elif n[0][3]:
                    label = n[0][3]
                if node_selected == nom_graph:
                    selected = ' selected'
                option_persos.append(f"""<option value="{nom_graph}"{selected}>{label}</option>""")
        return option_persos

    def build_list_options_persos2(self, lignes):
        """
        Récupère la map des nodes de persos et leur label dans le graphe complet
        :param lignes: les lignes du fichier dot
        :return:  la map des nodes de persos
        """
        option_persos = []
        label = ''
        for l in lignes:
            if 'peripheries=' + NodeType.node_peripheries.get(Personnage) + \
                    ' shape=' + NodeType.node_shapes.get(Personnage) in l:
                n = re.findall(r'([a-zA-Z]+) \[label=("([^\"]*)"|([^ ]*))', l)
                nom_graph = n[0][0]
                if n[0][2]:
                    label = n[0][2]
                elif n[0][3]:
                    label = n[0][3]
                option_persos.append(f"""<option value="{nom_graph}">{label}</option>""")
        return option_persos

    def get_perso_nodes(self, lignes):
        """
        Récupère la liste des nodes de perso dans le fichier graphe complet
        :param lignes: les lignes du graphe complet
        :return:  la liste des nodes de persos
        """
        nodes = []
        for l in lignes:
            if 'shape=' + NodeType.node_shapes.get(Personnage) in l:
                n = re.findall(r'([a-zA-Z]+) \[', l)
                nom_graph = n[0]
                nodes.append(nom_graph)
        return nodes

    def get_groupe_nodes(self, lignes):
        """
        Récupère la liste des nodes de groupes dans le fichier dot
        :param lignes: les lignes du fichier dot
        :return:  la liste des nodes de groupes
        """
        groupes = []
        for l in lignes:
            if 'shape=' + NodeType.node_shapes.get(Groupe) in l:
                n = re.findall(r'([a-zA-Z]+) \[', l)
                nom_graph = n[0]
                groupes.append(nom_graph)
        return groupes

    def add_nodes_to_graph(self, dot, nodes, node_selected, lignes):
        """
        Ajoute les nodes et leurs attributs au graphe
        :param dot: le graphe à créer
        :param nodes: la liste des nodes
        :param node_selected: le node sélectionné
        :param lignes: les lignes du fichier dot
        """
        for l in lignes:
            if 'peripheries' in l:
                n = re.findall(r'([a-zA-Z]+) \[label=("([^\"]*)"|([^ ]*)) fillcolor=("([^\"]*)"|([^ ]*)) '
                               r'href=("([^\"]*)"|([^ ]*)) peripheries=([1-2]) shape=([^ ]*) style=filled\]', l)
                if n[0][0] in nodes:
                    node = Node()
                    node.nom_graph = n[0][0]
                    if n[0][2]:
                        node.label = n[0][2]
                    elif n[0][3]:
                        node.label = n[0][3]
                    if n[0][5]:
                        node.fillcolor = n[0][5]
                    elif n[0][6]:
                        node.fillcolor = n[0][6]
                    if n[0][8]:
                        node.link = n[0][8]
                    elif n[0][9]:
                        node.link = n[0][9]
                    node.peripheries = n[0][10]
                    node.shape = n[0][11]
                    node.label = f"""<<table border="0" cellborder="0" cellspacing="0">
  <tr><td href=".?node={node.nom_graph}">{node.label}</td></tr>
  <tr><td href="{node.link}"><img src="./site/resources/icons/loupe.png"/></td></tr>
</table>>"""
                    if node.nom_graph == node_selected:
                        dot.node(node.nom_graph, node.label, style='filled', fillcolor=Color.CHOSEN_COLOR,
                                 peripheries=node.peripheries, shape=node.shape,
                                 fixedsize=node.fixed_size, height='1', width='2,5', id=node.nom_graph)
                    else:
                        dot.node(node.nom_graph, node.label, style='filled', fillcolor=node.fillcolor,
                                 peripheries=node.peripheries, shape=node.shape, id=node.nom_graph)

    def add_edges_to_graph(self, dot, nodes, view_edges, lignes):
        """
        Ajoute les arrêtes et leurs attributs au graphe
        :param dot: le graphe à créer
        :param nodes: la liste des nodes
        :param view_edges: le type d'arrêtes à visualiser
        :param lignes: les lignes du fichier dot
        """
        for l in lignes:
            if '->' in l:
                e = re.findall(r'([a-zA-Z]+) -> ([a-zA-Z]+) \[color=("([^\"]*)"|([^ ]*)) dir=([^ ]*)\]', l)
                if e[0][0] in nodes and e[0][1] in nodes:
                    edge = Edge()
                    edge.first_node = e[0][0]
                    edge.second_node = e[0][1]
                    if e[0][3]:
                        edge.fillcolor = e[0][3]
                    elif e[0][4]:
                        edge.fillcolor = e[0][4]
                    edge.dir = e[0][5]
                    if edge.fillcolor == Color.ENTENTE_COLOR:
                        if ViewEdges.VIEW_ENTENTE in view_edges:
                            dot.edge(edge.first_node, edge.second_node, color=edge.fillcolor, dir=edge.dir)
                    elif edge.fillcolor == Color.FAMILLE_COLOR:
                        if ViewEdges.VIEW_FAMILLE in view_edges:
                            dot.edge(edge.first_node, edge.second_node, color=edge.fillcolor, dir=edge.dir)
                    elif edge.fillcolor == Color.NEUTRAL_COLOR:
                        if ViewEdges.VIEW_NEUTRAL in view_edges:
                            dot.edge(edge.first_node, edge.second_node, color=edge.fillcolor, dir=edge.dir)
                    elif edge.fillcolor == Color.OPPOSITION_COLOR:
                        if ViewEdges.VIEW_OPPOSITION in view_edges:
                            dot.edge(edge.first_node, edge.second_node, color=edge.fillcolor, dir=edge.dir)
                    else:
                        if ViewEdges.VIEW_GROUPES in view_edges:
                            dot.edge(edge.first_node, edge.second_node, color=edge.fillcolor, dir=edge.dir)

    def build_svg(self, node_selected, view_edges=[ViewEdges.VIEW_ALL]):
        lignes = self.get_lignes_graphe_complet()
        groupe_nodes = self.get_groupe_nodes(lignes)

        nodes = []
        if node_selected == 'All':
            nodes = self.get_perso_nodes(lignes)
            if ViewEdges.VIEW_ALL in view_edges:
                nodes += groupe_nodes
        else:
            nodes.append(node_selected)
            # noeuds à degré 1
            self.add_linked_nodes(nodes, lignes, view_edges)
            # noeuds à degré 2
            self.add_linked_nodes(nodes, lignes, view_edges, groupe_nodes)

        dot = Digraph(name='GrapheTdC', filename='./tmp/gnTdcMini',
                      comment='La fleur au Fusil Mini', engine=ENGINE)
        dot.attr(rankdir='LR')

        self.add_nodes_to_graph(dot, nodes, node_selected, lignes)
        self.add_edges_to_graph(dot, nodes, view_edges, lignes)

        dot.save()
        dot.format = 'svg'
        dot.render(directory='.').replace('\\', '/')
        return dot


