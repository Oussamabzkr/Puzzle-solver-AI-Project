import tkinter as tk
from tkinter import ttk
import time

# =========================================================================
# Pseudo-codes (DFS, BFS, UCS, A*, IDA*) en Français
# =========================================================================
CODE_DFS = [
    "01. pile.ajouter( (Départ, [Départ]) )",
    "02. Tant que pile n'est pas vide :",
    "03.   courant, chemin = pile.retirer_dernier() [POP]",
    "04.   Si courant == Objectif : SUCCÈS",
    "05.   Si courant non visité :",
    "06.     Visités.ajouter(courant)",
    "07.     Pour chaque voisin (Haut, Droite, Gauche, Bas) :",
    "08.       Si voisin valide et non visité :",
    "09.         nouveau_chemin = chemin + [voisin]",
    "10.         pile.ajouter( (voisin, nouveau_chemin) ) [PUSH]"
]

CODE_BFS = [
    "01. file.ajouter( (Départ, [Départ]) )",
    "02. Tant que file n'est pas vide :",
    "03.   courant, chemin = file.retirer_premier() [POP]",
    "04.   Si courant == Objectif : SUCCÈS",
    "05.   Si courant non visité :",
    "06.     Visités.ajouter(courant)",
    "07.     Pour chaque voisin (Haut, Droite, Gauche, Bas) :",
    "08.       Si voisin valide et non visité :",
    "09.         nouveau_chemin = chemin + [voisin]",
    "10.         file.ajouter( (voisin, nouveau_chemin) ) [PUSH]"
]

CODE_UCS = [
    "01. file_priorite.ajouter( (Départ, [Départ], cout=0) )",
    "02. Tant que file_priorite n'est pas vide :",
    "03.   courant, chemin, cout = extraire_min_cout() [POP]",
    "04.   Si courant == Objectif : SUCCÈS",
    "05.   Si courant non visité :",
    "06.     Visités.ajouter(courant)",
    "07.     Pour chaque voisin (Haut, Droite, Gauche, Bas) :",
    "08.       Si voisin valide et non visité :",
    "09.         nv_cout = cout + poids(voisin)",
    "10.         file_priorite.ajouter( (voisin, nv_chemin, nv_cout) ) [PUSH & TRI]"
]

CODE_ASTAR = [
    "01. file_priorite.ajouter( (Départ, [Départ], g=0, f=h(Départ)) )",
    "02. Tant que file n'est pas vide :",
    "03.   courant, chemin, g, f = extraire_min_f() [POP]",
    "04.   Si courant == Objectif : SUCCÈS",
    "05.   Si courant non visité :",
    "06.     Visités.ajouter(courant)",
    "07.     Pour chaque voisin (Haut, Droite, Gauche, Bas) :",
    "08.       Si voisin valide et non visité :",
    "09.         nv_g = g + poids(voisin)",
    "10.         nv_f = nv_g + distance_manhattan(voisin, Objectif)",
    "11.         file_priorite.ajouter( (voisin, nv_chemin, nv_g, nv_f) ) [TRI]"
]

CODE_IDASTAR = [
    "01. seuil = h(Départ)",
    "02. Boucle Infinie :",
    "03.   res, chemin = Recherche(Départ, g=0, seuil)",
    "04.   Si res == SUCCÈS : Objectif atteint",
    "05.   Si res == INFINI : Échec",
    "06.   seuil = res",
    "07. ",
    "08. Fonction Recherche(noeud, g, seuil) :",
    "09.   f = g + h(noeud)",
    "10.   Si f > seuil : retourner f",
    "11.   Si noeud == Objectif : SUCCÈS",
    "12.   min_f = INFINI",
    "13.   Pour chaque voisin non visité :",
    "14.     res = Recherche(voisin, g+cout, seuil)",
    "15.     min_f = min(min_f, res)",
    "16.   retourner min_f"
]

class VisualisateurAlgorithmes(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulateur d'Algorithmes (DFS / BFS / UCS / A* / IDA*) - Heuristique & Coûts")
        self.geometry("1480x850") 
        self.configure(bg="#f1f5f9")
        
        self.canvas_size = 400
        # Changement de la taille par défaut à 9
        self.taille_grille = 9
        
        self.historique = []
        self.index_historique = -1
        self.en_cours = False
        self.temps_calcul_ms = 0.0 
        
        self.position_depart = (1, 1)
        self.position_cible = (self.taille_grille-2, self.taille_grille-2)
        self.obstacles = set()
        
        self.poids_cases = {} 
        self.outil_actuel = "obstacle" 
        
        self.generer_obstacles_par_defaut()
        self.creer_layout()
        self.compiler_historique() 
        self.restaurer_etat_index()

    def creer_layout(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        separateur_principal = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#94a3b8", sashwidth=8)
        separateur_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==================== COLONNE GAUCHE ====================
        cadre_gauche = tk.Frame(separateur_principal, bg="#cbd5e1")
        separateur_principal.add(cadre_gauche, minsize=540, stretch="always")
        
        # -- Options : Algo et Taille --
        cadre_top_options = tk.Frame(cadre_gauche, bg="#cbd5e1")
        cadre_top_options.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)
        
        cadre_algorithme = tk.LabelFrame(cadre_top_options, text=" ⚙️ Algorithme ", bg="#f8fafc", font=("Arial", 9, "bold"))
        cadre_algorithme.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.combo_algo = ttk.Combobox(cadre_algorithme, values=[
            "DFS (Pile - LIFO)", 
            "BFS (File - FIFO)", 
            "UCS (Coût Uniforme)", 
            "A* (Heuristique Manhattan)",
            "IDA* (Heuristique Manhattan)"
        ], state="readonly", font=("Arial", 9))
        self.combo_algo.set("IDA* (Heuristique Manhattan)")
        self.combo_algo.pack(fill=tk.X, padx=5, pady=5)
        self.combo_algo.bind("<<ComboboxSelected>>", self.changer_parametres)
        
        cadre_taille = tk.LabelFrame(cadre_top_options, text=" 📏 Taille ", bg="#f8fafc", font=("Arial", 9, "bold"))
        cadre_taille.pack(side=tk.LEFT, fill=tk.X, padx=(5, 0))
        self.spin_taille = tk.Spinbox(cadre_taille, from_=5, to=40, width=5, command=self.changer_parametres, font=("Arial", 10))
        self.spin_taille.delete(0, tk.END)
        self.spin_taille.insert(0, str(self.taille_grille))
        self.spin_taille.pack(padx=5, pady=4)
        self.spin_taille.bind("<Return>", lambda e: self.changer_parametres())

        # -- Outils --
        cadre_edition = tk.LabelFrame(cadre_gauche, text=" 🧱 Outils ", bg="#f8fafc", font=("Arial", 10, "bold"))
        cadre_edition.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)
        
        disposition_outils = tk.Frame(cadre_edition, bg="#f8fafc")
        disposition_outils.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(disposition_outils, text="📍 Départ", bg="#10b981", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=lambda: self.definir_outil("start")).pack(side=tk.LEFT, padx=3)
        tk.Button(disposition_outils, text="🎯 Objectif", bg="#ef4444", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=lambda: self.definir_outil("goal")).pack(side=tk.LEFT, padx=3)
        tk.Button(disposition_outils, text="🧱 Mur", bg="#64748b", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=lambda: self.definir_outil("obstacle")).pack(side=tk.LEFT, padx=3)
        
        # Outil de Poids (Coût) pour UCS / A* / IDA*
        cadre_poids = tk.Frame(disposition_outils, bg="#e2e8f0", padx=2, pady=2)
        cadre_poids.pack(side=tk.LEFT, padx=5)
        tk.Button(cadre_poids, text="⚖️ Poids", bg="#8b5cf6", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=lambda: self.definir_outil("poids")).pack(side=tk.LEFT)
        self.spin_poids = tk.Spinbox(cadre_poids, from_=1, to=99, width=3, font=("Arial", 10, "bold"))
        self.spin_poids.delete(0, tk.END)
        self.spin_poids.insert(0, "5")
        self.spin_poids.pack(side=tk.LEFT, padx=3)
        
        tk.Button(cadre_poids, text="🗑️ Vider Prix", bg="#f43f5e", fg="white", font=("Arial", 8, "bold"), relief=tk.FLAT, command=self.effacer_tous_poids).pack(side=tk.LEFT, padx=3)

        self.lbl_outil_actif = tk.Label(disposition_outils, text="Outil Actif: Mur", bg="#f8fafc", fg="#2563eb", font=("Arial", 9, "bold"))
        self.lbl_outil_actif.pack(side=tk.RIGHT, padx=5)

        # -- Contrôles & VITESSE --
        cadre_controle = tk.LabelFrame(cadre_gauche, text=" 🕹️ Contrôle & Vitesse ", bg="#f8fafc", font=("Arial", 10, "bold"))
        cadre_controle.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM) 
        
        disposition_boutons = tk.Frame(cadre_controle, bg="#f8fafc")
        disposition_boutons.pack(fill=tk.X, padx=5, pady=2)
        self.bouton_retour = tk.Button(disposition_boutons, text="⏮ Arrière", bg="#6366f1", fg="white", font=("Arial", 9, "bold"), command=self.etape_arriere)
        self.bouton_retour.pack(side=tk.LEFT, padx=3, pady=2)
        self.bouton_demarrer = tk.Button(disposition_boutons, text="▶ Auto", bg="#10b981", fg="white", font=("Arial", 9, "bold"), command=self.lancer_animation_auto)
        self.bouton_demarrer.pack(side=tk.LEFT, padx=3, pady=2)
        self.bouton_pause = tk.Button(disposition_boutons, text="⏸ Pause", bg="#f59e0b", fg="white", font=("Arial", 9, "bold"), command=self.mettre_en_pause, state=tk.DISABLED)
        self.bouton_pause.pack(side=tk.LEFT, padx=3, pady=2)
        self.bouton_avancer = tk.Button(disposition_boutons, text="Avant ⏭", bg="#3b82f6", fg="white", font=("Arial", 9, "bold"), command=self.etape_avant)
        self.bouton_avancer.pack(side=tk.LEFT, padx=3, pady=2)
        self.bouton_reinitialiser = tk.Button(disposition_boutons, text="🔄 Vider (Algorithme)", bg="#ef4444", fg="white", font=("Arial", 9, "bold"), command=self.reinitialiser_grille)
        self.bouton_reinitialiser.pack(side=tk.RIGHT, padx=3, pady=2)
        
        self.glissiere_vitesse = tk.Scale(cadre_controle, from_=1, to=500, orient=tk.HORIZONTAL, label="Vitesse d'animation (ms)", bg="#f8fafc", highlightthickness=0, font=("Arial", 9, "bold"), fg="#1e293b")
        self.glissiere_vitesse.set(10)
        self.glissiere_vitesse.pack(fill=tk.X, padx=10, pady=0)

        self.lbl_stats = tk.Label(cadre_controle, text="📊 Nœuds explorés: 0  |  ⏱️ Temps calcul: 0.00 ms", bg="#e2e8f0", fg="#0f172a", font=("Arial", 10, "bold"), pady=5)
        self.lbl_stats.pack(fill=tk.X, padx=5, pady=5)

        # -- Canvas --
        cadre_canevas = tk.Frame(cadre_gauche, bg="#f8fafc", bd=2, relief=tk.GROOVE)
        cadre_canevas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5) 
        self.canvas = tk.Canvas(cadre_canevas, width=self.canvas_size, height=self.canvas_size, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(expand=True)
        self.canvas.bind("<B1-Motion>", self.clic_grille_edition)
        self.canvas.bind("<Button-1>", self.clic_grille_edition)

        # ==================== COLONNE DROITE ====================
        pane_droit = tk.PanedWindow(separateur_principal, orient=tk.VERTICAL, bg="#cbd5e1", sashwidth=8)
        separateur_principal.add(pane_droit, minsize=500, stretch="always")
        
        # 1. Le Code
        cadre_code = tk.LabelFrame(pane_droit, text=" 📝 Exécution de l'Algorithme ", bg="#f8fafc", font=("Arial", 10, "bold"))
        pane_droit.add(cadre_code, minsize=200, stretch="always")
        self.listbox_code = tk.Listbox(cadre_code, font=("Consolas", 11, "bold"), bg="#1e293b", fg="#e2e8f0", selectbackground="#3b82f6", selectforeground="white", highlightthickness=0)
        self.listbox_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
        # 2. Le Milieu (Structure et Visités)
        pane_milieu = tk.PanedWindow(pane_droit, orient=tk.HORIZONTAL, bg="#94a3b8", sashwidth=8)
        pane_droit.add(pane_milieu, minsize=300, stretch="always")
        
        self.lbl_cadre_structure = tk.LabelFrame(pane_milieu, text=" 💾 Structure (Push/Pop/Tri) ", bg="#f8fafc", fg="#7c3aed", font=("Arial", 9, "bold"))
        pane_milieu.add(self.lbl_cadre_structure, minsize=200, stretch="always")
        scroll_struct = tk.Scrollbar(self.lbl_cadre_structure)
        scroll_struct.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_structure = tk.Text(self.lbl_cadre_structure, font=("Consolas", 10), bg="#ffffff", fg="#5b21b6", highlightthickness=0, yscrollcommand=scroll_struct.set)
        self.txt_structure.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_struct.config(command=self.txt_structure.yview)
        
        cadre_visites = tk.LabelFrame(pane_milieu, text=" 👁️ Nœuds VISITÉS ", bg="#f8fafc", fg="#dc2626", font=("Arial", 9, "bold"))
        pane_milieu.add(cadre_visites, minsize=200, stretch="always")
        scroll_visites = tk.Scrollbar(cadre_visites)
        scroll_visites.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_visites = tk.Text(cadre_visites, font=("Consolas", 10), bg="#ffffff", fg="#991b1b", highlightthickness=0, yscrollcommand=scroll_visites.set)
        self.txt_visites.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_visites.config(command=self.txt_visites.yview)
        
        # 3. Le Chemin
        cadre_chemin = tk.LabelFrame(pane_droit, text=" 📍 Chemin avec Flèches ", bg="#f8fafc", fg="#d97706", font=("Arial", 10, "bold"))
        pane_droit.add(cadre_chemin, minsize=80, stretch="always")
        self.txt_chemin = tk.Text(cadre_chemin, font=("Consolas", 10, "bold"), bg="#ffffff", fg="#854d0e", highlightthickness=0)
        self.txt_chemin.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Tags Highlights
        self.txt_structure.tag_configure("hl_push", background="#d8b4fe", foreground="black", font=("Consolas", 10, "bold"))
        self.txt_structure.tag_configure("hl_pop", background="#fca5a5", foreground="#7f1d1d", font=("Consolas", 10, "bold")) 
        self.txt_visites.tag_configure("hl_visite", background="#93c5fd", foreground="black", font=("Consolas", 10, "bold"))
        
        self.mettre_a_jour_code_affichage()

    def mettre_a_jour_code_affichage(self):
        self.listbox_code.delete(0, tk.END)
        algo_selectionne = self.combo_algo.get()
        if algo_selectionne.startswith("DFS"): code = CODE_DFS
        elif algo_selectionne.startswith("BFS"): code = CODE_BFS
        elif algo_selectionne.startswith("UCS"): code = CODE_UCS
        elif algo_selectionne.startswith("IDA*"): code = CODE_IDASTAR
        else: code = CODE_ASTAR 
        
        for ligne in code:
            self.listbox_code.insert(tk.END, ligne)

    # ==================== LOGIQUE ====================
    def changer_parametres(self, event=None):
        try:
            nt = int(self.spin_taille.get())
            if 5 <= nt <= 40:
                self.taille_grille = nt
                
                # Correction du glitch : Réajuster les positions si elles sortent de la grille
                if self.position_depart[0] >= nt or self.position_depart[1] >= nt:
                    self.position_depart = (1, 1)
                if self.position_cible[0] >= nt or self.position_cible[1] >= nt:
                    self.position_cible = (nt - 2, nt - 2)
                    
                # Éviter que le départ et l'objectif se superposent après ajustement
                if self.position_depart == self.position_cible:
                    self.position_cible = (nt - 1, nt - 1)
                
                # Nettoyer les obstacles et les poids qui se retrouvent hors limites
                self.obstacles = {obs for obs in self.obstacles if obs[0] < nt and obs[1] < nt}
                self.poids_cases = {pos: p for pos, p in self.poids_cases.items() if pos[0] < nt and pos[1] < nt}
                
        except ValueError:
            pass
        self.mettre_a_jour_code_affichage()
        self.mettre_en_pause()
        self.compiler_historique()
        self.restaurer_etat_index()

    def generer_obstacles_par_defaut(self):
        self.obstacles.clear()
        limite = min(12, self.taille_grille)
        for i in range(4, limite): self.obstacles.add((i, 5))

    def effacer_tous_poids(self):
        self.poids_cases.clear()
        self.compiler_historique()
        self.restaurer_etat_index()

    def definir_outil(self, outil):
        self.outil_actuel = outil
        noms = {"start": "Départ", "goal": "Objectif", "obstacle": "Mur", "poids": "Poids (Coût)"}
        self.lbl_outil_actif.config(text=f"Outil Actif: {noms[outil]}")

    def clic_grille_edition(self, event):
        if self.en_cours: return
        largeur_reelle = self.canvas.winfo_width()
        hauteur_reelle = self.canvas.winfo_height()
        if largeur_reelle <= 1: largeur_reelle = self.canvas_size
        if hauteur_reelle <= 1: hauteur_reelle = self.canvas_size
        
        tc_w = largeur_reelle / self.taille_grille
        tc_h = hauteur_reelle / self.taille_grille
        tc = min(tc_w, tc_h) 
        
        offset_x = (largeur_reelle - (tc * self.taille_grille)) / 2
        offset_y = (hauteur_reelle - (tc * self.taille_grille)) / 2

        c = int((event.x - offset_x) // tc)
        r = int((event.y - offset_y) // tc)
        
        if 0 <= r < self.taille_grille and 0 <= c < self.taille_grille:
            if self.outil_actuel == "start" and (r, c) != self.position_cible and (r, c) not in self.obstacles:
                self.position_depart = (r, c)
            elif self.outil_actuel == "goal" and (r, c) != self.position_depart and (r, c) not in self.obstacles:
                self.position_cible = (r, c)
            elif self.outil_actuel == "obstacle" and (r, c) != self.position_depart and (r, c) != self.position_cible:
                if (r, c) in self.obstacles: 
                    self.obstacles.remove((r, c))
                else: 
                    self.obstacles.add((r, c))
                    if (r, c) in self.poids_cases: del self.poids_cases[(r, c)]
            elif self.outil_actuel == "poids" and (r, c) != self.position_depart and (r, c) != self.position_cible and (r, c) not in self.obstacles:
                try:
                    val = int(self.spin_poids.get())
                    if val <= 1:
                        if (r, c) in self.poids_cases: del self.poids_cases[(r, c)]
                    else:
                        self.poids_cases[(r, c)] = val
                except ValueError:
                    pass
            self.compiler_historique()
            self.restaurer_etat_index()

    def get_voisins(self, pos):
        r, c = pos
        res = []
        for dr, dc in [(-1, 0), (0, 1), (0, -1), (1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.taille_grille and 0 <= nc < self.taille_grille and (nr, nc) not in self.obstacles:
                res.append((nr, nc))
        return res

    def heuristique_manhattan(self, noeud):
        r1, c1 = noeud
        r2, c2 = self.position_cible
        return abs(r1 - r2) + abs(c1 - c2)

    def compiler_historique(self):
        temps_debut = time.perf_counter() 
        self.historique = []
        algo_actuel = self.combo_algo.get()
        est_dfs = algo_actuel.startswith("DFS")
        est_bfs = algo_actuel.startswith("BFS")
        est_ucs = algo_actuel.startswith("UCS")
        est_astar = algo_actuel.startswith("A*")
        est_idastar = algo_actuel.startswith("IDA*")
        
        noeuds_visites = []
        
        if est_idastar:
            seuil = self.heuristique_manhattan(self.position_depart)
            structure_donnees = [(self.position_depart, [self.position_depart], 0, seuil)]
            
            def save_state_ida(line, curr, path, hl_push=False, hl_pop=None, hl_v=False, msg=None):
                stack_copy = [ (s[0], list(s[1]), s[2], s[3]) for s in structure_donnees ]
                self.historique.append({
                    "line": line,
                    "stack": stack_copy,
                    "visited": list(noeuds_visites),
                    "path": list(path),
                    "curr": curr,
                    "hl_push": hl_push,
                    "hl_pop_node": hl_pop,
                    "hl_v": hl_v,
                    "msg": msg or f"IDA* Seuil (f max): {seuil}"
                })

            def recherche(chemin, g, seuil_courant):
                courant = chemin[-1]
                f = g + self.heuristique_manhattan(courant)
                
                save_state_ida(9, courant, chemin)
                save_state_ida(10, courant, chemin)
                
                if courant not in noeuds_visites:
                    noeuds_visites.append(courant)
                    
                if f > seuil_courant:
                    return f, None
                    
                save_state_ida(11, courant, chemin)
                if courant == self.position_cible:
                    return "SUCCESS", chemin
                    
                min_f = float('inf')
                save_state_ida(12, courant, chemin)
                
                save_state_ida(13, courant, chemin)
                for voisin in self.get_voisins(courant):
                    if voisin not in chemin: 
                        nv_g = g + self.poids_cases.get(voisin, 1)
                        nv_f = nv_g + self.heuristique_manhattan(voisin)
                        
                        structure_donnees.append((voisin, chemin + [voisin], nv_g, nv_f))
                        save_state_ida(14, courant, chemin, hl_push=True)
                        
                        res_f, res_chemin = recherche(chemin + [voisin], nv_g, seuil_courant)
                        
                        popped = structure_donnees.pop()
                        save_state_ida(15, courant, chemin, hl_pop=popped[0])
                        
                        if res_f == "SUCCESS":
                            return "SUCCESS", res_chemin
                        if res_f < min_f:
                            min_f = res_f
                            
                save_state_ida(16, courant, chemin)
                return min_f, None

            while True:
                save_state_ida(2, self.position_depart, [], msg=f"Nouvelle itération - Seuil = {seuil}")
                save_state_ida(3, self.position_depart, [])
                
                res, chemin_final = recherche([self.position_depart], 0, seuil)
                
                save_state_ida(4, self.position_depart, [])
                if res == "SUCCESS":
                    save_state_ida(4, self.position_cible, chemin_final, msg=f"SUCCESS (Seuil final: {seuil})")
                    break
                    
                save_state_ida(5, self.position_depart, [])
                if res == float('inf'):
                    save_state_ida(5, None, [], msg="FAIL (Objectif inatteignable)")
                    break
                    
                save_state_ida(6, self.position_depart, [])
                seuil = res

        else:
            if est_astar:
                h_depart = self.heuristique_manhattan(self.position_depart)
                structure_donnees = [(self.position_depart, [self.position_depart], 0, h_depart)]
            elif est_ucs:
                structure_donnees = [(self.position_depart, [self.position_depart], 0)]
            else:
                structure_donnees = [(self.position_depart, [self.position_depart])]
                
            def save_state(line, curr_node, path_so_far, hl_push=False, hl_pop_node=None, hl_visited=False, msg=None):
                stack_copy = []
                for item in structure_donnees:
                    if est_astar:
                        stack_copy.append((item[0], list(item[1]), item[2], item[3]))
                    elif est_ucs:
                        stack_copy.append((item[0], list(item[1]), item[2]))
                    else:
                        stack_copy.append((item[0], list(item[1])))
                self.historique.append({
                    "line": line, "stack": stack_copy, "visited": list(noeuds_visites), "path": list(path_so_far),
                    "curr": curr_node, "hl_push": hl_push, "hl_pop_node": hl_pop_node, "hl_v": hl_visited, "msg": msg
                })

            save_state(1, self.position_depart, [], hl_push=True)
            
            while structure_donnees:
                save_state(2, None, [])
                if est_astar:
                    structure_donnees.sort(key=lambda x: x[3])
                    noeud_courant, chemin_actuel, cout_g_actuel, cout_f_actuel = structure_donnees.pop(0)
                elif est_ucs:
                    structure_donnees.sort(key=lambda x: x[2])
                    noeud_courant, chemin_actuel, cout_actuel = structure_donnees.pop(0)
                elif est_dfs:
                    noeud_courant, chemin_actuel = structure_donnees.pop()
                else:
                    noeud_courant, chemin_actuel = structure_donnees.pop(0)
                
                save_state(3, noeud_courant, chemin_actuel, hl_pop_node=noeud_courant)
                
                save_state(4, noeud_courant, chemin_actuel)
                if noeud_courant == self.position_cible:
                    save_state(4, noeud_courant, chemin_actuel, msg="SUCCESS")
                    break
                
                save_state(5, noeud_courant, chemin_actuel)
                if noeud_courant not in noeuds_visites:
                    noeuds_visites.append(noeud_courant)
                    save_state(6, noeud_courant, chemin_actuel, hl_visited=True)
                    
                    save_state(7, noeud_courant, chemin_actuel)
                    for voisin in self.get_voisins(noeud_courant):
                        save_state(8, noeud_courant, chemin_actuel)
                        if voisin not in noeuds_visites:
                            nouveau_chemin = list(chemin_actuel)
                            nouveau_chemin.append(voisin)
                            
                            cout_voisin = self.poids_cases.get(voisin, 1)
                            
                            if est_astar:
                                nv_g = cout_g_actuel + cout_voisin
                                nv_f = nv_g + self.heuristique_manhattan(voisin)
                                save_state(9, noeud_courant, chemin_actuel)
                                save_state(10, noeud_courant, chemin_actuel)
                                structure_donnees.append((voisin, nouveau_chemin, nv_g, nv_f))
                                save_state(11, noeud_courant, chemin_actuel, hl_push=True)
                            elif est_ucs:
                                nouveau_cout = cout_actuel + cout_voisin
                                save_state(9, noeud_courant, chemin_actuel)
                                structure_donnees.append((voisin, nouveau_chemin, nouveau_cout))
                                save_state(10, noeud_courant, chemin_actuel, hl_push=True)
                            else:
                                save_state(9, noeud_courant, chemin_actuel)
                                structure_donnees.append((voisin, nouveau_chemin))
                                save_state(10, noeud_courant, chemin_actuel, hl_push=True)
                            
            if not structure_donnees and (not self.historique or self.historique[-1].get("msg") != "SUCCESS"):
                save_state(2, None, [], msg="FAIL")
                
        temps_fin = time.perf_counter()
        self.temps_calcul_ms = (temps_fin - temps_debut) * 1000 
        self.index_historique = 0

    # ==================== RENDU VISUEL ====================
    def restaurer_etat_index(self):
        if not self.historique or self.index_historique < 0 or self.index_historique >= len(self.historique):
            return
            
        etat = self.historique[self.index_historique]
        algo_actuel = self.combo_algo.get()
        est_dfs = algo_actuel.startswith("DFS")
        est_bfs = algo_actuel.startswith("BFS")
        est_ucs = algo_actuel.startswith("UCS")
        est_astar = algo_actuel.startswith("A*")
        est_idastar = algo_actuel.startswith("IDA*")
        
        # Condition pour l'affichage des Poids
        afficher_poids = not (est_dfs or est_bfs)
        
        # Stats
        nb_visites = len(etat["visited"])
        msg_supp = f"  |  ℹ️ {etat['msg']}" if etat.get("msg") else ""
        self.lbl_stats.config(text=f"📊 Nœuds explorés : {nb_visites}  |  ⏱️ Temps de calcul : {self.temps_calcul_ms:.3f} ms{msg_supp}")

        # Code Update
        self.listbox_code.selection_clear(0, tk.END)
        self.listbox_code.selection_set(etat["line"] - 1)
        self.listbox_code.see(etat["line"] - 1)

        self.canvas.delete("all")
        set_structure = set([item[0] for item in etat["stack"]])
        set_visited = set(etat["visited"])
        set_path = set(etat["path"])
        
        largeur_reelle = self.canvas.winfo_width()
        hauteur_reelle = self.canvas.winfo_height()
        if largeur_reelle <= 1: largeur_reelle = self.canvas_size
        if hauteur_reelle <= 1: hauteur_reelle = self.canvas_size
        
        tc_w = largeur_reelle / self.taille_grille
        tc_h = hauteur_reelle / self.taille_grille
        tc = min(tc_w, tc_h) 
        
        offset_x = (largeur_reelle - (tc * self.taille_grille)) / 2
        offset_y = (hauteur_reelle - (tc * self.taille_grille)) / 2
        
        # Dessin de la grille
        for r in range(self.taille_grille):
            for c in range(self.taille_grille):
                x1 = offset_x + c * tc
                y1 = offset_y + r * tc
                x2 = x1 + tc
                y2 = y1 + tc
                
                if (r, c) == self.position_depart: couleur = "#10b981"
                elif (r, c) == self.position_cible: couleur = "#ef4444"
                elif (r, c) == etat["curr"]: couleur = "#f97316"
                elif (r, c) in set_path: couleur = "#fcd34d"
                elif (r, c) in set_visited: couleur = "#93c5fd"
                elif (r, c) in set_structure: couleur = "#d8b4fe"
                elif (r, c) in self.obstacles: couleur = "#475569"
                else: couleur = "#ffffff"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur, outline="#cbd5e1")
                
                if afficher_poids and (r, c) in self.poids_cases and (r, c) not in self.obstacles and (r, c) != self.position_depart and (r, c) != self.position_cible:
                    cx = x1 + tc/2
                    cy = y1 + tc/2
                    self.canvas.create_text(cx, cy, text=str(self.poids_cases[(r, c)]), font=("Arial", int(tc//2.5), "bold"), fill="#1e293b")

        # Dessin des flèches
        if etat["path"] and len(etat["path"]) > 1:
            for i in range(len(etat["path"]) - 1):
                r1, c1 = etat["path"][i]
                r2, c2 = etat["path"][i+1]
                cx1 = offset_x + c1 * tc + tc/2
                cy1 = offset_y + r1 * tc + tc/2
                cx2 = offset_x + c2 * tc + tc/2
                cy2 = offset_y + r2 * tc + tc/2
                self.canvas.create_line(cx1, cy1, cx2, cy2, arrow=tk.LAST, fill="#0f172a", width=2)

        # Mise à jour STRUCTURE
        self.txt_structure.delete(1.0, tk.END)
        if etat.get("hl_pop_node"):
            self.txt_structure.insert(tk.END, f" ❌ [POP / BACKTRACK] : {etat['hl_pop_node']}\n", "hl_pop")
            self.txt_structure.insert(tk.END, "-"*30 + "\n")

        if not etat["stack"]:
            self.txt_structure.insert(tk.END, "\n   [ Vide ]")
        else:
            if est_dfs: entete = " 🔥 PILE (LIFO) :\n"
            elif est_idastar: entete = " 🔄 PILE D'APPELS (IDA* Récursif) :\n"
            elif est_astar: entete = " 🌟 FILE DE PRIORITÉ (Trie par f = g + h) :\n"
            elif est_ucs: entete = " ⚖️ FILE DE PRIORITÉ (Trie par Coût) :\n"
            else: entete = " ⏩ FILE (FIFO) :\n"
            
            self.txt_structure.insert(tk.END, entete)
            elements = list(reversed(etat["stack"])) if (est_dfs or est_idastar) else etat["stack"]
            
            for idx, item in enumerate(elements):
                if est_astar or est_idastar:
                    node, path, g, f = item
                    texte_ligne = f"  [{idx:02d}] -> {node} | f={f} (g={g})\n"
                elif est_ucs:
                    node, path, cost = item
                    texte_ligne = f"  [{idx:02d}] -> {node} | Coût: {cost}\n"
                else:
                    node, path = item
                    texte_ligne = f"  [{idx:02d}] -> {node}\n"
                    
                if (est_dfs or est_idastar) and idx == 0 and etat.get("hl_push"):
                    self.txt_structure.insert(tk.END, texte_ligne, "hl_push")
                elif not (est_dfs or est_idastar) and idx == len(elements)-1 and etat.get("hl_push"):
                    self.txt_structure.insert(tk.END, texte_ligne, "hl_push")
                else:
                    self.txt_structure.insert(tk.END, texte_ligne)
        self.txt_structure.see(1.0)

        # Mise à jour VISITÉS 
        self.txt_visites.delete(1.0, tk.END)
        if not etat["visited"]:
            self.txt_visites.insert(tk.END, "\n   [ Aucun ]")
        else:
            for idx, v_node in enumerate(etat["visited"]):
                texte_ligne = f" #{idx+1:02d} : {v_node}\n"
                if idx == len(etat["visited"]) - 1 and etat.get("hl_v"):
                    self.txt_visites.insert(tk.END, texte_ligne, "hl_visite")
                else:
                    self.txt_visites.insert(tk.END, texte_ligne)
        self.txt_visites.see(tk.END)

        # Mise à jour CHEMIN
        self.txt_chemin.delete(1.0, tk.END)
        if not etat["path"]:
            self.txt_chemin.insert(tk.END, "[ En attente... ]")
        else:
            trajet_str = " ➔ ".join([str(n) for n in etat["path"]])
            if etat.get("msg") and "SUCCESS" in etat["msg"]:
                trajet_str += "\n\n🎉 [Objectif Atteint !]"
            self.txt_chemin.insert(tk.END, trajet_str)

    # ==================== NAVIGATION ====================
    def etape_avant(self):
        if self.index_historique < len(self.historique) - 1:
            self.index_historique += 1
            self.restaurer_etat_index()
        else:
            self.mettre_en_pause()

    def etape_arriere(self):
        if self.index_historique > 0:
            self.index_historique -= 1
            self.restaurer_etat_index()

    def lancer_animation_auto(self):
        self.en_cours = True
        self.bouton_demarrer.config(state=tk.DISABLED)
        self.bouton_pause.config(state=tk.NORMAL)
        self.bouton_avancer.config(state=tk.DISABLED)
        self.bouton_retour.config(state=tk.DISABLED)
        self.combo_algo.config(state=tk.DISABLED)
        self.spin_taille.config(state=tk.DISABLED)
        self.boucle_animation()

    def boucle_animation(self):
        if self.en_cours:
            if self.index_historique < len(self.historique) - 1:
                self.etape_avant()
                self.after(self.glissiere_vitesse.get(), self.boucle_animation)
            else:
                self.mettre_en_pause()

    def mettre_en_pause(self):
        self.en_cours = False
        self.bouton_demarrer.config(state=tk.NORMAL)
        self.bouton_pause.config(state=tk.DISABLED)
        self.bouton_avancer.config(state=tk.NORMAL)
        self.bouton_retour.config(state=tk.NORMAL)
        self.combo_algo.config(state="readonly")
        self.spin_taille.config(state=tk.NORMAL)

    def reinitialiser_grille(self):
        self.mettre_en_pause()
        self.compiler_historique()
        self.index_historique = 0
        self.restaurer_etat_index()

if __name__ == "__main__":
    application = VisualisateurAlgorithmes()
    application.update()
    application.restaurer_etat_index() 
    application.mainloop()