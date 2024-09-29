#!/usr/bin/python3
# coding: utf-8
from image import ImageGenerator
from image import ViewEdges

class GraphParameters:
    node = ''
    edges = []


class GraphPage:
    image = ImageGenerator()
    lignes = image.get_lignes_graphe_complet()

    _HEADERS = """<html>
    <head>
        <title>Graphe La Fleur au Fusil</title>
        <style type="text/css">
            .formgrid {
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

    def _build_graph_svg(self, parameters: GraphParameters):
        node = parameters.node
        edges = parameters.edges

        svg: str
        if node == 'All' and edges == [ViewEdges.VIEW_FAMILLE, ViewEdges.VIEW_ENTENTE,
                                       ViewEdges.VIEW_NEUTRAL, ViewEdges.VIEW_OPPOSITION]:
            with open("./tmp/gnTdc.svg", encoding='utf8') as file:
                svg = file.read()
        else:
            self.image.build_svg(node, edges)
            with open("./tmp/gnTdcMini.svg", encoding='utf8') as file:
                svg = file.read()

        # on corrige le chemin des images
        svg = svg.replace('./site/', '')
        return svg

    def _build_character_selector(self, node_selected: str) -> str:
        options_persos = self.image.build_list_options_persos(node_selected, self.lignes)
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

    def build_graph_page(self, parameters: GraphParameters) -> bytes:
        return f"""<!DOCTYPE html>
           {self._HEADERS}
            <body>
                <form method = 'GET' action=".">
                    <div class=formgrid>
                        {self._build_character_selector(parameters.node)}
                        {self._build_egdes_selector(parameters.edges)}
                    </div>
                    <br>
                    <div class=formgrid>
                        <button type="submit">Afficher</button>
                    </div>
                </form>
            <hr />
            {self._build_graph_svg(parameters)}
            </body>
            </html>
        """.replace("\\'", "'").encode('utf-8')
