#!/usr/bin/python3
# coding: utf-8
import re
from image import ImageGenerator
from constants import ViewEdges
from constants import DistNode
from constants import NodeType
from constants import Personnage


class GraphParameters:
    node = ''
    edges = []
    distance = ''


class GraphPage:
    image = ImageGenerator()
    lignes = image.get_lignes_graphe_complet()

    _HEADERS = """<html>
    <head>
        <title>Graphe La Fleur au Fusil</title>
        <style type="text/css">
            .formflex {
                display: flex;
                align-items: center;
                column-gap: 40px;
                justify-content: center;
            }
            .fieldgrid {
                display: grid;
                grid-template-columns: 1fr 1fr;
            }
        </style>
    </head>
    """

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
                    print(nom_graph)
                if node_selected == nom_graph:
                    selected = ' selected'
                option_persos.append(f"""<option value="{nom_graph}"{selected}>{label}</option>""")
        return option_persos

    def _build_graph_svg(self, parameters: GraphParameters):
        node = parameters.node
        edges = parameters.edges
        distance = parameters.distance
        all_edges = [ViewEdges.VIEW_FAMILLE, ViewEdges.VIEW_ENTENTE, ViewEdges.VIEW_NEUTRAL, ViewEdges.VIEW_OPPOSITION,
                     ViewEdges.VIEW_GROUPES]
        if not edges:
            edges = all_edges

        svg: str
        if node == 'All' and set(all_edges).issubset(edges):
            with open("./tmp/gnTdc.svg", encoding='utf8') as file:
                svg = file.read()
        else:
            self.image.build_svg(node, edges, distance)
            with open("./tmp/gnTdcMini.svg", encoding='utf8') as file:
                svg = file.read()

        # on corrige le chemin des images
        svg = svg.replace('./site/', '')
        return svg

    def _build_character_selector(self, node_selected: str) -> str:
        options_persos = self.build_list_options_persos(node_selected, self.lignes)
        return f"""<div>
                    <label for="personnage">Personnage :</label><br>
                    <select name="node" onchange="this.form.submit()">
                        <option value="All">All</option>
                        {options_persos}
                    </select>
                </div>"""

    @staticmethod
    def _build_egdes_selector(edges_selected) -> str:
        famille_selected = 'checked' if edges_selected == [] or ViewEdges.VIEW_FAMILLE in edges_selected else ''
        entente_selected = 'checked' if edges_selected == [] or ViewEdges.VIEW_ENTENTE in edges_selected else ''
        neutral_selected = 'checked' if edges_selected == [] or ViewEdges.VIEW_NEUTRAL in edges_selected else ''
        opposition_selected = 'checked' if edges_selected == [] or ViewEdges.VIEW_OPPOSITION in edges_selected else ''
        groupes_selected = 'checked' if edges_selected == [] or ViewEdges.VIEW_GROUPES in edges_selected else ''
        return f"""<div>
            <fieldset>
                <legend>Quels liens afficher ?</legend>
                <div class=fieldgrid>
                    <div>
                        <input type="checkbox" id="entente" name="edges" value="{ViewEdges.VIEW_ENTENTE}"
                          {entente_selected}/>
                        <label for="entente">Entente</label><br />
                    </div>

                    <div>
                        <input type="checkbox" id="famille" name="edges" value="{ViewEdges.VIEW_FAMILLE}"
                          {famille_selected}/>
                        <label for="famille">Famille</label><br />
                    </div>

                    <div>
                        <input type="checkbox" id="neutre" name="edges" value="{ViewEdges.VIEW_NEUTRAL}"
                          {neutral_selected}/>
                        <label for="neutre">Neutre</label><br />
                    </div>

                    <div>
                        <input type="checkbox" id="groupes" name="edges" value="{ViewEdges.VIEW_GROUPES}"
                          {groupes_selected}/>
                        <label for="groupes">Groupes</label>
                    </div>

                    <div>
                        <input type="checkbox" id="opposition" name="edges" value="{ViewEdges.VIEW_OPPOSITION}"
                          {opposition_selected}/>
                        <label for="opposition">Opposition</label>
                    </div>
                </div>
            </fieldset>
        </div>"""

    @staticmethod
    def _build_distance_selector(distance_selected: str) -> str:
        dist_one_selected = 'checked' if distance_selected == DistNode.DIST_ONE else ''
        dist_two_selected = 'checked' if distance_selected == '' or distance_selected == DistNode.DIST_TWO else ''
        return f"""<div>
            <fieldset>
                <legend>Quel degré de distance ?</legend>
                <input type="radio" id="distone" name="distance" value="{DistNode.DIST_ONE}"
                    {dist_one_selected}/>
                <label for="distone">Degré 1</label><br />

                <input type="radio" id="disttwo" name="distance" value="{DistNode.DIST_TWO}"
                    {dist_two_selected}/>
                <label for="disttwo">Degré 2</label><br />
            </fieldset>
        </div>"""

    def build_graph_page(self, parameters: GraphParameters) -> bytes:
        return f"""<!DOCTYPE html>
           {self._HEADERS}
            <body>
                <form method = 'GET' action=".">
                    <div class=formflex>
                        {self._build_character_selector(parameters.node)}
                        {self._build_egdes_selector(parameters.edges)}
                        {self._build_distance_selector(parameters.distance)}
                    </div>
                    <br>
                    <div class=formflex>
                        <button type="submit">Afficher</button>
                    </div>
                </form>
            <hr />
            {self._build_graph_svg(parameters)}
            </body>
            </html>
        """.replace("\\'", "'").encode('utf-8')
