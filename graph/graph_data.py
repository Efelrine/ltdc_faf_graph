#!/usr/bin/python3
# coding: utf-8

import re


from constants import *
from json import JSONEncoder
from graph_page import GraphParameters


class NodeData:
    id: str
    label: str
    link: str
    color: str
    shape: str


class EdgeData:
    source: str
    target: str
    color: str
    direction: str


class Data:
    nodes: list[NodeData]
    links: list[EdgeData]


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class GraphDataBuilder:

    @staticmethod
    def get_full_graph() -> list[str]:
        """
        Récupère la liste des lignes du graphe complet
        :return:  la liste des lignes du graphe complet
        """
        lines: list[str] = []
        with open('./tmp/gnTdc', encoding='utf8') as f:
            lines = f.readlines()
        return lines

    @staticmethod
    def add_linked_nodes_by_edges(first_node, second_node, nodes, groupe_nodes, temp):
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

    @staticmethod
    def add_linked_nodes(nodes: list[str], full_graph: list[str], view_edges: list[str], groups=[]):
        """
        Ajoute à une liste de nodes les autres nodes liés à ceux dans la liste
        :param nodes: la liste des nodes à partir desquels compléter la liste
        :param full_graph: les lignes du fichier graphe complet
        :param view_edges: le type d'arrêtes à visualiser
        :param groups: la liste des nodes correspondant aux groupes
        """

        new_nodes = []
        groups_set = set(groups)

        for line in full_graph:
            if '->' in line:
                e = re.findall(r'([a-zA-Z]+) -> ([a-zA-Z]+) \[color="([^\"]*)"', line)
                first_node = e[0][0]
                second_node = e[0][1]
                color = e[0][2]
                if (color == Color.ENTENTE_COLOR and ViewEdges.VIEW_ENTENTE in view_edges
                        or color == Color.FAMILLE_COLOR and ViewEdges.VIEW_FAMILLE in view_edges
                        or color == Color.NEUTRAL_COLOR and ViewEdges.VIEW_NEUTRAL in view_edges
                        or color == Color.OPPOSITION_COLOR and ViewEdges.VIEW_OPPOSITION in view_edges
                        or color == Color.BLACK and ViewEdges.VIEW_GROUPES in view_edges):
                    if first_node not in groups_set and second_node not in groups_set:
                        if first_node not in new_nodes and second_node in nodes:
                            new_nodes.append(first_node)
                        if second_node not in new_nodes and first_node in nodes:
                            new_nodes.append(second_node)
        nodes.extend(new_nodes)

    @staticmethod
    def get_perso_ids(full_graph: list[str]) -> list[str]:
        """
        Récupère la liste des nodes de perso dans le fichier graphe complet
        :param full_graph: les lignes du graphe complet
        :return:  la liste des nodes de persos
        """
        nodes = []
        for line in full_graph:
            if 'shape=' + NodeType.node_shapes.get(Personnage) in line:
                n = re.findall(r'([a-zA-Z]+) \[', line)
                nom_graph = n[0]
                nodes.append(nom_graph)
        return nodes

    @staticmethod
    def get_group_ids(full_graph: list[str]) -> list[str]:
        """
        Récupère la liste des nodes de groupes dans le fichier dot
        :param full_graph: les lignes du fichier dot
        :return:  la liste des nodes de groupes
        """
        groupes = []
        for line in full_graph:
            if 'shape=' + NodeType.node_shapes.get(Groupe) in line:
                n = re.findall(r'([a-zA-Z]+) \[', line)
                nom_graph = n[0]
                groupes.append(nom_graph)
        return groupes

    @staticmethod
    def build_nodes_data(nodes: list[str], node_selected: str, full_graph: list[str]) -> list[NodeData]:
        """
        Ajoute les nodes et leurs attributs au graphe
        :param nodes: la liste des nodes
        :param node_selected: le node sélectionné
        :param full_graph: les lignes du fichier dot
        :return: la liste des NodeDatas selectionnée
        """
        nodes_data: list[NodeData] = []
        for line in full_graph:
            if 'peripheries' in line:
                n = re.findall(r'([a-zA-Z]+) \[label=("([^\"]*)"|([^ ]*)) fillcolor=("([^\"]*)"|([^ ]*)) '
                               r'href=("([^\"]*)"|([^ ]*)) peripheries=([1-2]) shape=([^ ]*) style=filled]', line)
                if n[0][0] in nodes:
                    node = NodeData()
                    nodes_data.append(node)
                    node.id = n[0][0]
                    if n[0][2]:
                        node.label = n[0][2]
                    elif n[0][3]:
                        node.label = n[0][3]
                    if n[0][5]:
                        node.color = n[0][5]
                    elif n[0][6]:
                        node.color = n[0][6]
                    if n[0][8]:
                        node.link = n[0][8]
                    elif n[0][9]:
                        node.link = n[0][9]
                    node.shape = n[0][11]
        return nodes_data

    @staticmethod
    def build_edges_data(nodes: list[str], view_edges: list[str], full_graph: list[str]) -> list[EdgeData]:
        """
        Ajoute les arrêtes et leurs attributs au graphe
        :param nodes: la liste des nodes
        :param view_edges: le type d'arrêtes à visualiser
        :param full_graph: les lignes du fichier dot
        """
        edges_data: list[EdgeData] = []
        for line in full_graph:
            if '->' in line:
                e = re.findall(r'([a-zA-Z]+) -> ([a-zA-Z]+) \[color=("([^\"]*)"|([^ ]*)) dir=([^ ]*)\]', line)
                if e[0][0] in nodes and e[0][1] in nodes:
                    edge = EdgeData()
                    edge.source = e[0][0]
                    edge.target = e[0][1]
                    if e[0][3]:
                        edge.color = e[0][3]
                    elif e[0][4]:
                        edge.color = e[0][4]
                    edge.direction = e[0][5]
                    print(f"source {edge.source}, target {edge.target} : match {edge.color == Color.ENTENTE_COLOR} and {ViewEdges.VIEW_ENTENTE in view_edges}  ")
                    if (edge.color == Color.ENTENTE_COLOR and ViewEdges.VIEW_ENTENTE in view_edges
                            or edge.color == Color.FAMILLE_COLOR and ViewEdges.VIEW_FAMILLE in view_edges
                            or edge.color == Color.NEUTRAL_COLOR and ViewEdges.VIEW_NEUTRAL in view_edges
                            or edge.color == Color.OPPOSITION_COLOR and ViewEdges.VIEW_OPPOSITION in view_edges
                            or edge.color == Color.BLACK and ViewEdges.VIEW_GROUPES in view_edges):
                        print("coucou")
                        edges_data.append(edge)
        return edges_data

    def build_graph_data(self, graph_parameters: GraphParameters) -> str:
        return self._build_graph_data(graph_parameters.node, graph_parameters.edges)

    def _build_graph_data(self, node_selected, view_edges=[ViewEdges.VIEW_ALL]) -> str:
        full_graph = self.get_full_graph()
        groups = self.get_group_ids(full_graph)

        nodes: list[str] = []
        if node_selected == 'All':
            nodes = self.get_perso_ids(full_graph)
            if ViewEdges.VIEW_ALL in view_edges:
                nodes += groups
        else:
            nodes.append(node_selected)

            # noeuds à degré 1
            self.add_linked_nodes(nodes, full_graph, view_edges)
            # noeuds à degré 2
            self.add_linked_nodes(nodes, full_graph, view_edges, groups)

        graph_data = Data()
        graph_data.nodes = self.build_nodes_data(nodes, node_selected, full_graph)
        graph_data.links = self.build_edges_data(nodes, view_edges, full_graph)

        return MyEncoder().encode(graph_data)


