
import heapq
from collections import deque
from typing import Dict, List, Optional
import time
from agent import Agent, Environment, Sensor, Actuator, Percept, Action



# GRAPHE DES ZONES
class GrapheInondations:
    """Réseau de zones géographiques avec niveaux d'eau et risques."""
    
    def __init__(self):
        self.graphe = {}  # {zone: {zone_voisine: infos}}
        self.infos_zones = {}  # {zone: {population, niveau_eau, ...}}
        self.heuristiques = {}  # {zone: distance_euclidienne_au_refuge}
        
    def ajouter_zone(self, zone: str, population: int, niveau_eau: int, 
                     lat: float = 0, lon: float = 0):
        """Ajoute une zone avec ses caractéristiques."""
        if zone not in self.graphe:
            self.graphe[zone] = {}
        
        urgence = min(int(niveau_eau/10 + population/100), 10)
        self.infos_zones[zone] = {
            'population': population,
            'niveau_eau': niveau_eau,
            'coords': (lat, lon),
            'urgence': urgence
        }
    
    def ajouter_connexion(self, zone1: str, zone2: str, distance: float, 
                         risque: int, temps: int):
        """Ajoute connexion bidirectionnelle. Coût = distance + 2×risque + 0.5×temps"""
        cout = distance + 2 * risque + 0.5 * temps
        info = {'cout': cout, 'distance': distance, 'risque': risque, 'temps': temps}
        self.graphe[zone1][zone2] = info
        self.graphe[zone2][zone1] = info
    
    def obtenir_cout(self, zone1: str, zone2: str) -> float:
        """Retourne le coût entre deux zones."""
        return self.graphe.get(zone1, {}).get(zone2, {}).get('cout', float('inf'))


def construire_graphe() -> GrapheInondations:
    """Construit le réseau de 12 zones."""
    g = GrapheInondations()
    
    # 12 zones
    zones = [
        ("Centre_Secours", 20, 10, 0, 0),
        ("Zone_Residentielle_Nord", 500, 45, -2, 3),
        ("Zone_Residentielle_Sud", 300, 30, -2, -3),
        ("Zone_Industrielle", 50, 25, -4, -2),
        ("Centre_Ville", 800, 40, -1, 0),
        ("Hopital", 200, 35, -1, 1),
        ("Ecole_Primaire", 150, 55, -3, 4),
        ("Pont_Principal", 0, 65, -2, 1),
        ("Berges_Riviere", 0, 80, -3, 2),
        ("Refuge_Colline", 0, 5, -5, 5),
        ("Station_Pompage", 30, 40, -4, 0),
        ("Zone_Agricole", 100, 35, -6, 3)
    ]
    for z in zones:
        g.ajouter_zone(*z)
    
    # 17 connexions
    connexions = [
        ("Centre_Secours", "Zone_Residentielle_Nord", 5, 7, 10),
        ("Centre_Secours", "Zone_Residentielle_Sud", 4, 5, 8),
        ("Centre_Secours", "Centre_Ville", 3, 6, 6),
        ("Zone_Residentielle_Nord", "Ecole_Primaire", 2, 8, 5),
        ("Zone_Residentielle_Nord", "Pont_Principal", 3, 9, 7),
        ("Zone_Residentielle_Sud", "Zone_Industrielle", 4, 4, 9),
        ("Zone_Residentielle_Sud", "Centre_Ville", 2, 6, 5),
        ("Centre_Ville", "Hopital", 1, 5, 3),
        ("Centre_Ville", "Pont_Principal", 2, 7, 5),
        ("Hopital", "Refuge_Colline", 6, 2, 12),
        ("Ecole_Primaire", "Refuge_Colline", 5, 3, 10),
        ("Pont_Principal", "Berges_Riviere", 1, 10, 3),
        ("Berges_Riviere", "Refuge_Colline", 4, 9, 10),
        ("Zone_Industrielle", "Station_Pompage", 3, 6, 7),
        ("Station_Pompage", "Zone_Agricole", 5, 5, 11),
        ("Zone_Agricole", "Refuge_Colline", 7, 4, 15),
        ("Pont_Principal", "Station_Pompage", 2, 8, 5),
    ]
    for c in connexions:
        g.ajouter_connexion(*c)
    
    # Heuristiques (distance euclidienne au refuge)
    refuge = g.infos_zones["Refuge_Colline"]['coords']
    for zone, infos in g.infos_zones.items():
        coords = infos['coords']
        dist = ((coords[0] - refuge[0])**2 + (coords[1] - refuge[1])**2)**0.5
        g.heuristiques[zone] = dist * 2
    
    return g



# FORMULATION DU PROBLÈME
class ProblemeRecherche:
    """Définit le problème : état initial, but, actions, coûts."""
    
    def __init__(self, graphe: GrapheInondations, initial: str, but: str):
        self.graphe = graphe
        self.etat_initial = initial
        self.etat_but = but
        
    def actions(self, etat: str) -> List[str]:
        """Zones atteignables depuis l'état."""
        return list(self.graphe.graphe.get(etat, {}).keys())
    
    def resultat(self, etat: str, action: str) -> str:
        """Applique l'action (déplacement vers zone)."""
        return action
    
    def test_but(self, etat: str) -> bool:
        """Vérifie si le but est atteint."""
        return etat == self.etat_but
    
    def cout_action(self, etat: str, action: str) -> float:
        """Coût de l'action."""
        return self.graphe.obtenir_cout(etat, action)
    
    def heuristique(self, etat: str) -> float:
        """Estimation du coût restant (pour A*)."""
        return self.graphe.heuristiques.get(etat, 0)



# NŒUD DE RECHERCHE
class Noeud:
    """Nœud dans l'arbre de recherche."""
    
    def __init__(self, etat: str, parent=None, action: str = None, cout: float = 0):
        self.etat = etat
        self.parent = parent
        self.action = action
        self.cout_chemin = cout
        self.profondeur = 0 if not parent else parent.profondeur + 1
    
    def __lt__(self, other):
        return self.cout_chemin < other.cout_chemin
    
    def chemin(self) -> List[str]:
        """Reconstruit le chemin depuis la racine."""
        chemin = []
        n = self
        while n:
            chemin.append(n.etat)
            n = n.parent
        return list(reversed(chemin))


def developper(noeud: Noeud, pb: ProblemeRecherche) -> List[Noeud]:
    """Génère les successeurs d'un nœud."""
    return [Noeud(pb.resultat(noeud.etat, a), noeud, a, 
                  noeud.cout_chemin + pb.cout_action(noeud.etat, a))
            for a in pb.actions(noeud.etat)]



# ALGORITHMES DE RECHERCHE
class Stats:
    """Statistiques de recherche."""
    def __init__(self):
        self.noeuds_explores = 0
        self.temps = 0
        self.chemin = []
        self.cout = 0
        self.succes = False


def bfs(pb: ProblemeRecherche) -> Stats:
    """Recherche en largeur (FIFO)."""
    stats = Stats()
    debut = time.time()
    
    n = Noeud(pb.etat_initial)
    if pb.test_but(n.etat):
        stats.chemin, stats.succes = n.chemin(), True
        stats.temps = time.time() - debut
        return stats
    
    frontiere = deque([n])
    atteints = {pb.etat_initial}
    
    while frontiere:
        n = frontiere.popleft()
        stats.noeuds_explores += 1
        
        for enfant in developper(n, pb):
            if enfant.etat not in atteints:
                if pb.test_but(enfant.etat):
                    stats.chemin = enfant.chemin()
                    stats.cout = enfant.cout_chemin
                    stats.succes = True
                    stats.temps = time.time() - debut
                    return stats
                frontiere.append(enfant)
                atteints.add(enfant.etat)
    
    stats.temps = time.time() - debut
    return stats


def dfs(pb: ProblemeRecherche, limite: int = 50) -> Stats:
    """Recherche en profondeur (LIFO)."""
    stats = Stats()
    debut = time.time()
    
    frontiere = [Noeud(pb.etat_initial)]
    explores = set()
    
    while frontiere:
        n = frontiere.pop()
        if n.etat in explores:
            continue
        
        stats.noeuds_explores += 1
        explores.add(n.etat)
        
        if pb.test_but(n.etat):
            stats.chemin = n.chemin()
            stats.cout = n.cout_chemin
            stats.succes = True
            stats.temps = time.time() - debut
            return stats
        
        if n.profondeur < limite:
            for enfant in reversed(developper(n, pb)):
                if enfant.etat not in explores:
                    frontiere.append(enfant)
    
    stats.temps = time.time() - debut
    return stats


def ucs(pb: ProblemeRecherche) -> Stats:
    """Recherche à coût uniforme (file de priorité sur g)."""
    stats = Stats()
    debut = time.time()
    
    n = Noeud(pb.etat_initial)
    frontiere = [(n.cout_chemin, 0, n)]
    atteints = {pb.etat_initial: 0}
    cpt = 0
    
    while frontiere:
        _, _, n = heapq.heappop(frontiere)
        stats.noeuds_explores += 1
        
        if pb.test_but(n.etat):
            stats.chemin = n.chemin()
            stats.cout = n.cout_chemin
            stats.succes = True
            stats.temps = time.time() - debut
            return stats
        
        for enfant in developper(n, pb):
            if enfant.etat not in atteints or enfant.cout_chemin < atteints[enfant.etat]:
                atteints[enfant.etat] = enfant.cout_chemin
                cpt += 1
                heapq.heappush(frontiere, (enfant.cout_chemin, cpt, enfant))
    
    stats.temps = time.time() - debut
    return stats


def a_star(pb: ProblemeRecherche) -> Stats:
    """Recherche A* (file de priorité sur f = g + h)."""
    stats = Stats()
    debut = time.time()
    
    n = Noeud(pb.etat_initial)
    f = n.cout_chemin + pb.heuristique(n.etat)
    frontiere = [(f, 0, n)]
    atteints = {pb.etat_initial: 0}
    cpt = 0
    
    while frontiere:
        _, _, n = heapq.heappop(frontiere)
        stats.noeuds_explores += 1
        
        if pb.test_but(n.etat):
            stats.chemin = n.chemin()
            stats.cout = n.cout_chemin
            stats.succes = True
            stats.temps = time.time() - debut
            return stats
        
        for enfant in developper(n, pb):
            if enfant.etat not in atteints or enfant.cout_chemin < atteints[enfant.etat]:
                atteints[enfant.etat] = enfant.cout_chemin
                f = enfant.cout_chemin + pb.heuristique(enfant.etat)
                cpt += 1
                heapq.heappush(frontiere, (f, cpt, enfant))
    
    stats.temps = time.time() - debut
    return stats



# ARCHITECTURE AGENT (PEAS)
class CapteurInondation(Sensor):
    """Capteur : perçoit l'état de l'environnement."""
    
    def sense(self, env: 'EnvironnementInondation', agent: Agent) -> Percept:
        if not hasattr(agent, 'zone_actuelle'):
            return {}
        
        zone = agent.zone_actuelle
        return {
            'zone_actuelle': zone,
            'zones_voisines': list(env.graphe.graphe.get(zone, {}).keys()),
            'niveau_eau': env.graphe.infos_zones[zone]['niveau_eau'],
            'urgence': env.graphe.infos_zones[zone]['urgence']
        }

class ActionneurSecours(Actuator):
    """Actionneur : exécute les déplacements."""
    
    def act(self, env: 'EnvironnementInondation', agent: 'AgentSecours', 
            action: Action) -> None:
        if action and action in env.graphe.graphe.get(agent.zone_actuelle, {}):
            cout = env.graphe.obtenir_cout(agent.zone_actuelle, action)
            agent.performance -= cout
            print(f"🚁 {agent.name}: {agent.zone_actuelle} → {action} (coût: {cout:.1f})")
            agent.zone_actuelle = action


class EnvironnementInondation(Environment):
    """Environnement : réseau de zones avec inondations."""
    
    def __init__(self, graphe: GrapheInondations, zone_but: str):
        super().__init__()
        self.graphe = graphe
        self.zone_but = zone_but
        self.capteur = CapteurInondation()
        self.actionneur = ActionneurSecours()
        
    def get_percepts(self, agent: Agent) -> Percept:
        return self.capteur.sense(self, agent)
    
    def apply_action(self, agent: Agent, action: Action) -> None:
        self.actionneur.act(self, agent, action)
    
    def is_done(self) -> bool:
        return all(hasattr(a, 'zone_actuelle') and a.zone_actuelle == self.zone_but 
                   for a in self.agents)


class AgentSecours(Agent):
    """Agent basé sur l'utilité : planifie avec A* puis exécute."""
    def __init__(self, name: str, graphe: GrapheInondations, 
                 depart: str, but: str, strategie: str = 'A*'):
        super().__init__(name)
        self.graphe = graphe
        self.zone_actuelle = depart
        self.zone_but = but
        self.strategie = strategie
        
        # Planification initiale
        self.plan = self._planifier()
        self.index = 0
        
        print(f"🤖 {name} - Plan: {' → '.join(self.plan)}")
        
    def _planifier(self) -> List[str]:
        """Planifie le chemin optimal."""
        pb = ProblemeRecherche(self.graphe, self.zone_actuelle, self.zone_but)
        
        algos = {'BFS': bfs, 'DFS': dfs, 'UCS': ucs, 'A*': a_star}
        stats = algos.get(self.strategie.upper(), a_star)(pb)
        
        return stats.chemin if stats.succes else []
    
    def program(self, percept: Percept) -> Optional[Action]:
        """Programme de l'agent : suit le plan."""
        if not percept or percept.get('zone_actuelle') == self.zone_but:
            return None
        
        if self.index < len(self.plan) - 1:
            self.index += 1
            return self.plan[self.index]
        
        return None



# FONCTIONS UTILITAIRES
def comparer_algos(graphe: GrapheInondations, depart: str, arrivee: str):
    """Compare les 4 algorithmes."""
    print(f"\n{'='*70}\n📊 COMPARAISON : {depart} → {arrivee}\n{'='*70}")
    
    pb = ProblemeRecherche(graphe, depart, arrivee)
    algos = {'BFS': bfs, 'DFS': dfs, 'UCS': ucs, 'A*': a_star}
    resultats = {}
    
    for nom, algo in algos.items():
        stats = algo(pb)
        resultats[nom] = stats
        if stats.succes:
            print(f"{nom:4} → Coût: {stats.cout:.1f} | Nœuds: {stats.noeuds_explores} | "
                  f"Temps: {stats.temps*1000:.2f}ms")
    
    # Meilleur algo
    optimal = min(r.cout for r in resultats.values() if r.succes)
    meilleur = min(resultats.items(), 
                   key=lambda x: (not x[1].succes, x[1].cout, x[1].noeuds_explores))
    print(f"\n💡 Recommandé: {meilleur[0]} (optimal: {abs(meilleur[1].cout - optimal) < 0.01})")



# PROGRAMME PRINCIPAL


def main():
    print("\n🌊 AGENT DE SURVEILLANCE DES INONDATIONS")
    print("="*70)
    
    # Construction
    graphe = construire_graphe()
    print(f"✓ Graphe: 12 zones, 17 connexions")
    
    # Comparaison algorithmes
    comparer_algos(graphe, "Centre_Secours", "Refuge_Colline")
    
    # Simulation Agent-Environnement
    print(f"\n{'='*70}\n🤖 SIMULATION AGENT-ENVIRONNEMENT\n{'='*70}")
    
    env = EnvironnementInondation(graphe, "Refuge_Colline")
    agent = AgentSecours("Équipe_Alpha", graphe, "Centre_Secours", "Refuge_Colline", 'A*')
    env.agents.append(agent)
    
    env.run(steps=20)
    
    print(f"\n✅ Mission terminée")
    print(f"   Position: {agent.zone_actuelle}")
    print(f"   Performance: {agent.performance:.2f}")
    print("="*70)


if __name__ == "__main__":
    main()