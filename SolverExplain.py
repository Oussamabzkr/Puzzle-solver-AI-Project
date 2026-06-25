import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# =========================================================================
# Pseudo-codes officiels pour le N-Puzzle
# =========================================================================
CODE_DFS = [
    "01. pile.ajouter( (État_Initial, [État_Initial]) )",
    "02. Tant que pile n'est pas vide :",
    "03.   courant, chemin = pile.retirer_dernier() [POP]",
    "04.   Si courant == État_Cible : SUCCÈS",
    "05.   Si courant non visité :",
    "06.     Visités.ajouter(courant)",
    "07.     Pour chaque mouvement valide (Haut, Bas, Gauche, Droite) :",
    "08.       nouvel_etat = permuter_case_vide(courant)",
    "09.       Si nouvel_etat non visité :",
    "10.         pile.ajouter( (nouvel_etat, chemin + [nouvel_etat]) ) [PUSH]"
]

CODE_IDA_STAR = [
    "01. seuil = h(État_Initial)",
    "02. Boucle Infinie :",
    "03.   res, chemin = Recherche(État_Initial, g=0, seuil)",
    "04.   Si res == SUCCÈS : Objectif atteint",
    "05.   Si res == INFINI : Échec",
    "06.   seuil = res  [Mise à jour du seuil f]",
    "07. ",
    "08. Fonction Recherche(etat, g, seuil) :",
    "09.   f = g + h(etat)",
    "10.   Si f > seuil : retourner f",
    "11.   Si etat == État_Cible : SUCCÈS",
    "12.   min_f = INFINI",
    "13.   Pour chaque successeur valide :",
    "14.     res = Recherche(successeur, g+1, seuil)",
    "15.     min_f = min(min_f, res)",
    "16.   retourner min_f"
]

class VisualisateurNPuzzle(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulateur de N-Puzzle (8 & 15 Puzzle)")
        self.geometry("1550x900")
        self.configure(bg="#f1f5f9")
        
        self.taille_grille = 3 
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.board_state = list(self.goal_state)
        
        self.historique = []
        self.index_historique = -1
        self.en_cours = False
        self.temps_calcul_ms = 0.0
        self.solution_trouvee = False
        self.mode_chemin_optimal = False
        
        self.creer_layout()
        self.generer_puzzle_par_difficulte()

        self.canvas.bind("<Configure>", lambda event: self.dessiner_plateau_dynamique())

    def creer_layout(self):
        separateur_principal = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#94a3b8", sashwidth=8)
        separateur_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==================== COLONNE GAUCHE ====================
        cadre_gauche = tk.Frame(separateur_principal, bg="#cbd5e1")
        separateur_principal.add(cadre_gauche, minsize=550, stretch="always")
        
        cadre_top_options = tk.Frame(cadre_gauche, bg="#cbd5e1")
        cadre_top_options.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)
        
        cadre_algorithme = tk.LabelFrame(cadre_top_options, text=" ⚙️ Algorithme & Puzzle ", bg="#f8fafc", font=("Arial", 9, "bold"))
        cadre_algorithme.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.combo_algo = ttk.Combobox(cadre_algorithme, values=[
            "IDA* (Heuristique Manhattan)",
            "IDA* (Heuristique Hamming)",
            "DFS (Profondeur d'abord)"
        ], state="readonly", font=("Arial", 9))
        self.combo_algo.set("IDA* (Heuristique Manhattan)")
        self.combo_algo.pack(fill=tk.X, padx=5, pady=2)
        self.combo_algo.bind("<<ComboboxSelected>>", self.changer_algorithme_contexte)
        
        self.combo_type_puzzle = ttk.Combobox(cadre_algorithme, values=["Puzzle 8 (3x3)", "Puzzle 15 (4x4)"], state="readonly", font=("Arial", 9))
        self.combo_type_puzzle.set("Puzzle 8 (3x3)")
        self.combo_type_puzzle.pack(fill=tk.X, padx=5, pady=2)
        self.combo_type_puzzle.bind("<<ComboboxSelected>>", self.changer_taille_puzzle)

        cadre_difficulte = tk.LabelFrame(cadre_top_options, text=" 📊 Difficulté ", bg="#f8fafc", font=("Arial", 9, "bold"))
        cadre_difficulte.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        
        self.combo_diff = ttk.Combobox(cadre_difficulte, values=[
            "1 - Très Facile", "2 - Facile", "3 - Moyen", "4 - Difficile", "5 - Expert"
        ], state="readonly", width=14, font=("Arial", 9))
        self.combo_diff.set("2 - Facile")
        self.combo_diff.pack(padx=5, pady=10)
        self.combo_diff.bind("<<ComboboxSelected>>", lambda e: self.generer_puzzle_par_difficulte())
        
        # أزرار الإجراءات (تم إضافة زر الحساب هنا)
        cadre_actions = tk.Frame(cadre_gauche, bg="#cbd5e1")
        cadre_actions.pack(fill=tk.X, padx=5, pady=2, side=tk.TOP)
        tk.Button(cadre_actions, text="🎲 Mélanger", bg="#e67e22", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=self.generer_puzzle_par_difficulte).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(cadre_actions, text="🚀 Calculer la Solution", bg="#ef4444", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=self.lancer_calcul).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(cadre_actions, text="📊 Comparer", bg="#8b5cf6", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=self.ouvrir_fenetre_comparaison).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        cadre_controle = tk.LabelFrame(cadre_gauche, text=" 🕹️ Contrôle & Vitesse d'Exécution ", bg="#f8fafc", font=("Arial", 10, "bold"))
        cadre_controle.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM, expand=False) 
        
        disposition_boutons = tk.Frame(cadre_controle, bg="#f8fafc")
        disposition_boutons.pack(fill=tk.X, padx=5, pady=2)
        
        self.bouton_retour = tk.Button(disposition_boutons, text="⏮ Arrière", bg="#6366f1", fg="white", font=("Arial", 9, "bold"), command=self.etape_arriere)
        self.bouton_retour.pack(side=tk.LEFT, padx=2, pady=2)
        self.bouton_demarrer = tk.Button(disposition_boutons, text="▶ Lancer l'Animation", bg="#10b981", fg="white", font=("Arial", 9, "bold"), command=self.lancer_animation_auto)
        self.bouton_demarrer.pack(side=tk.LEFT, padx=2, pady=2)
        self.bouton_pause = tk.Button(disposition_boutons, text="⏸ Pause", bg="#f59e0b", fg="white", font=("Arial", 9, "bold"), command=self.mettre_en_pause, state=tk.DISABLED)
        self.bouton_pause.pack(side=tk.LEFT, padx=2, pady=2)
        self.bouton_avancer = tk.Button(disposition_boutons, text="Avant ⏭", bg="#3b82f6", fg="white", font=("Arial", 9, "bold"), command=self.etape_avant)
        self.bouton_avancer.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.bouton_chemin_opt = tk.Button(disposition_boutons, text="🏁 Chemin Optimal", bg="#0d9488", fg="white", font=("Arial", 9, "bold"), command=self.activer_mode_chemin_optimal)
        self.bouton_chemin_opt.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.bouton_reinitialiser = tk.Button(disposition_boutons, text="🔄 Reset", bg="#64748b", fg="white", font=("Arial", 9, "bold"), command=self.reinitialiser_simulation)
        self.bouton_reinitialiser.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # التعديل: بدء السرعة من 1
        self.glissiere_vitesse = tk.Scale(cadre_controle, from_=1, to=2000, orient=tk.HORIZONTAL, label="Délai d'animation (ms)", bg="#f8fafc", highlightthickness=0, font=("Arial", 9, "bold"))
        self.glissiere_vitesse.set(350)
        self.glissiere_vitesse.pack(fill=tk.X, padx=10, pady=2)

        self.lbl_stats = tk.Label(cadre_controle, text="En attente... | Cliquez sur 'Calculer la Solution'", bg="#e2e8f0", fg="#0f172a", font=("Arial", 10, "bold"), pady=5)
        self.lbl_stats.pack(fill=tk.X, padx=5, pady=5)

        cadre_canevas = tk.Frame(cadre_gauche, bg="#1e293b", bd=2, relief=tk.GROOVE)
        cadre_canevas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.TOP)
        self.canvas = tk.Canvas(cadre_canevas, bg="#1e293b", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # ==================== COLONNE DROITE ====================
        pane_droit = tk.PanedWindow(separateur_principal, orient=tk.VERTICAL, bg="#cbd5e1", sashwidth=8)
        separateur_principal.add(pane_droit, minsize=560, stretch="always")
        
        cadre_code = tk.LabelFrame(pane_droit, text=" 📝 Suivi Pas-à-Pas du Pseudo-code ", bg="#f8fafc", font=("Arial", 10, "bold"))
        pane_droit.add(cadre_code, minsize=160, stretch="always")
        self.listbox_code = tk.Listbox(cadre_code, font=("Consolas", 11, "bold"), bg="#1e293b", fg="#e2e8f0", selectbackground="#ea580c", selectforeground="white", highlightthickness=0)
        self.listbox_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
        pane_milieu = tk.PanedWindow(pane_droit, orient=tk.HORIZONTAL, bg="#94a3b8", sashwidth=8)
        pane_droit.add(pane_milieu, minsize=260, stretch="always")
        
        self.lbl_cadre_structure = tk.LabelFrame(pane_milieu, text=" 💾 Structure : STACK / Frontière ", bg="#f8fafc", fg="#7c3aed", font=("Arial", 9, "bold"))
        pane_milieu.add(self.lbl_cadre_structure, minsize=280, stretch="always")
        scroll_struct = tk.Scrollbar(self.lbl_cadre_structure)
        scroll_struct.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_structure = tk.Text(self.lbl_cadre_structure, font=("Consolas", 9), bg="#ffffff", fg="#5b21b6", highlightthickness=0, yscrollcommand=scroll_struct.set)
        self.txt_structure.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_struct.config(command=self.txt_structure.yview)
        
        cadre_visites = tk.LabelFrame(pane_milieu, text=" 👁️ Nœuds Explorés & Visités ", bg="#f8fafc", fg="#dc2626", font=("Arial", 9, "bold"))
        pane_milieu.add(cadre_visites, minsize=280, stretch="always")
        scroll_visites = tk.Scrollbar(cadre_visites)
        scroll_visites.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_visites = tk.Text(cadre_visites, font=("Consolas", 9), bg="#ffffff", fg="#991b1b", highlightthickness=0, yscrollcommand=scroll_visites.set)
        self.txt_visites.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_visites.config(command=self.txt_visites.yview)
        
        pane_inferieur = tk.PanedWindow(pane_droit, orient=tk.HORIZONTAL, bg="#94a3b8", sashwidth=8)
        pane_droit.add(pane_inferieur, minsize=240, stretch="always")

        cadre_solvabilite = tk.LabelFrame(pane_inferieur, text=" 🔬 Analyse Mathématique de Résolubilité ", bg="#f8fafc", fg="#0d9488", font=("Arial", 9, "bold"))
        pane_inferieur.add(cadre_solvabilite, minsize=280, stretch="always")
        scroll_solv = tk.Scrollbar(cadre_solvabilite)
        scroll_solv.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_solvabilite = tk.Text(cadre_solvabilite, font=("Consolas", 9), bg="#ffffff", fg="#115e59", highlightthickness=0, yscrollcommand=scroll_solv.set)
        self.txt_solvabilite.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_solv.config(command=self.txt_solvabilite.yview)

        cadre_chemin = tk.LabelFrame(pane_inferieur, text=" 🏁 Chemin Direct de la Solution (Arbre Épuré) ", bg="#f8fafc", fg="#b45309", font=("Arial", 9, "bold"))
        pane_inferieur.add(cadre_chemin, minsize=280, stretch="always")
        scroll_chem = tk.Scrollbar(cadre_chemin)
        scroll_chem.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_chemin = tk.Text(cadre_chemin, font=("Consolas", 9, "bold"), bg="#ffffff", fg="#854d0e", highlightthickness=0, yscrollcommand=scroll_chem.set)
        self.txt_chemin.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_chem.config(command=self.txt_chemin.yview)

        for txt_area in [self.txt_structure, self.txt_visites, self.txt_solvabilite, self.txt_chemin]:
            txt_area.tag_configure("hl_push", background="#e9d5ff", foreground="black", font=("Consolas", 9, "bold"))
            txt_area.tag_configure("hl_pop", background="#fecaca", foreground="#7f1d1d", font=("Consolas", 9, "bold")) 
            txt_area.tag_configure("hl_visite", background="#bfdbfe", foreground="black", font=("Consolas", 9, "bold"))
            txt_area.tag_configure("hl_success", background="#d1fae5", foreground="#065f46", font=("Consolas", 9, "bold"))
            txt_area.tag_configure("hl_alert", background="#ffedd5", foreground="#9a3412", font=("Consolas", 9, "bold"))
        
        self.mettre_a_jour_affichage_code()

    # =========================================================================
    # DÉCLENCHEMENT EXPLICITE DU CALCUL
    # =========================================================================
    def lancer_calcul(self):
        self.lbl_stats.config(text="⏳ Calcul de la solution en cours... Veuillez patienter.")
        self.update_idletasks() # Mise à jour de l'UI
        self.compiler_historique_recherche()
        self.restaurer_etat_index_visuel()

    def mettre_a_jour_affichage_code(self):
        self.listbox_code.delete(0, tk.END)
        algo = self.combo_algo.get()
        code_source = CODE_DFS if "DFS" in algo else CODE_IDA_STAR
        for ligne in code_source:
            self.listbox_code.insert(tk.END, ligne)

    def changer_taille_puzzle(self, event=None):
        type_puz = self.combo_type_puzzle.get()
        if "3x3" in type_puz:
            self.taille_grille = 3
            self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        else:
            self.taille_grille = 4
            self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
        self.generer_puzzle_par_difficulte()

    def changer_algorithme_contexte(self, event=None):
        self.mettre_a_jour_affichage_code()
        # Effacer l'historique pour forcer un nouveau calcul
        self.historique = []
        self.dessiner_plateau_sans_historique()

    def calculer_et_tracer_resolubilite(self, etat):
        self.txt_solvabilite.delete(1.0, tk.END)
        liste = list(etat)
        liste.remove(0)
        
        inversions_paires = []
        inversions_total = 0
        
        for i in range(len(liste)):
            for j in range(i + 1, len(liste)):
                if liste[i] > liste[j]:
                    inversions_paires.append((liste[i], liste[j]))
                    inversions_total += 1
                    
        self.txt_solvabilite.insert(tk.END, f"► Analyse du plateau :\n {etat}\n\n", "hl_push")
        self.txt_solvabilite.insert(tk.END, f"• Total d'inversions détectées: {inversions_total}\n\n")
        
        if inversions_paires:
            self.txt_solvabilite.insert(tk.END, "• Paires d'inversions :\n")
            chunk_size = 3
            for i in range(0, len(inversions_paires), chunk_size):
                chunk = inversions_paires[i:i+chunk_size]
                self.txt_solvabilite.insert(tk.END, f"  {chunk}\n")
        else:
            self.txt_solvabilite.insert(tk.END, "  [Aucune inversion]\n")
            
        self.txt_solvabilite.insert(tk.END, "\n• Verdict mathématique :\n")
        if self.taille_grille == 3:
            resoluble = (inversions_total % 2 == 0)
            status_text = "VALIDE (Inversions Paires)" if resoluble else "INVALIDÉ (Inversions Impaires)"
            self.txt_solvabilite.insert(tk.END, f"  ➔ Grille 3x3 : {status_text}\n", "hl_success" if resoluble else "hl_pop")
            return resoluble
        else:
            idx_vide = etat.index(0)
            ligne_depuis_bas = self.taille_grille - (idx_vide // self.taille_grille)
            self.txt_solvabilite.insert(tk.END, f"  Case vide à la ligne {ligne_depuis_bas} (du bas).\n")
            
            if ligne_depuis_bas % 2 == 0:
                resoluble = (inversions_total % 2 != 0)
                cond_str = "Ligne Paire -> Impaire requis"
            else:
                resoluble = (inversions_total % 2 == 0)
                cond_str = "Ligne Impaire -> Paire requis"
                
            status_text = f"CONFORME ({cond_str})" if resoluble else f"REFUSÉ ({cond_str})"
            self.txt_solvabilite.insert(tk.END, f"  ➔ Grille 4x4 : {status_text}\n", "hl_success" if resoluble else "hl_pop")
            return resoluble

    def generer_puzzle_par_difficulte(self):
        self.mettre_en_pause()
        self.mode_chemin_optimal = False
        diff = self.combo_diff.get()[0]
        nb_mouvements = {"1": 5, "2": 15, "3": 30, "4": 55, "5": 90}[diff]
        
        etat_courant = list(self.goal_state)
        historique_melange = [tuple(etat_courant)]
        
        attempts = 0
        while attempts < 1000:
            for _ in range(nb_mouvements):
                successeurs = self.obtenir_successeurs(tuple(etat_courant))
                choix = random.choice(successeurs)[0]
                if choix not in historique_melange[-2:]:
                    etat_courant = list(choix)
                    historique_melange.append(tuple(etat_courant))
            
            if self.calculer_et_tracer_resolubilite(tuple(etat_courant)):
                break
            attempts += 1
                
        self.board_state = list(etat_courant)
        
        # On ne calcule plus automatiquement la solution
        self.historique = []
        self.index_historique = -1
        self.temps_calcul_ms = 0.0
        self.dessiner_plateau_sans_historique()

    def obtenir_successeurs(self, etat):
        successeurs = []
        idx = etat.index(0)
        r, c = idx // self.taille_grille, idx % self.taille_grille
        
        mouvements = [(-1, 0, "Haut"), (1, 0, "Bas"), (0, -1, "Gauche"), (0, 1, "Droite")]
        for dr, dc, action in mouvements:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.taille_grille and 0 <= nc < self.taille_grille:
                n_idx = nr * self.taille_grille + nc
                n_list = list(etat)
                n_list[idx], n_list[n_idx] = n_list[n_idx], n_list[idx]
                successeurs.append((tuple(n_list), action))
        return successeurs

    def h_hamming(self, etat):
        return sum(1 for i in range(len(etat)) if etat[i] != 0 and etat[i] != self.goal_state[i])

    def h_manhattan(self, etat):
        score = 0
        for i in range(len(etat)):
            val = etat[i]
            if val != 0:
                r_act, c_act = i // self.taille_grille, i % self.taille_grille
                idx_cible = self.goal_state.index(val)
                r_cib, c_cib = idx_cible // self.taille_grille, idx_cible % self.taille_grille
                score += abs(r_act - r_cib) + abs(c_act - c_cib)
        return score

    def compiler_historique_recherche(self):
        start_time = time.perf_counter()
        self.historique = []
        self.solution_trouvee = False
        
        algo = self.combo_algo.get()
        etat_initial = tuple(self.board_state)
        f_heuristique = self.h_manhattan if "Manhattan" in algo else self.h_hamming
        noeuds_visites = []

        if "IDA*" in algo:
            seuil = f_heuristique(etat_initial)
            frontiere_virtuelle = [(etat_initial, [etat_initial], 0, seuil)]
            
            def log_ida(ligne, curr, path, hl_push=False, hl_pop=None, hl_v=False, msg=None):
                if self.solution_trouvee: return
                stack_copy = [(item[0], list(item[1]), item[2], item[3]) for item in frontiere_virtuelle]
                self.historique.append({
                    "line": ligne, "stack": stack_copy, "visited": list(noeuds_visites),
                    "path": list(path), "curr": curr, "hl_push": hl_push, "hl_pop_node": hl_pop,
                    "hl_v": hl_v, "msg": msg or f"Seuil f actuel : {seuil}"
                })

            def recherche_rec(chemin, g, seuil_courant):
                if self.solution_trouvee: return seuil_courant, None
                curr = chemin[-1]
                f = g + f_heuristique(curr)
                
                log_ida(9, curr, chemin)
                log_ida(10, curr, chemin)
                
                if curr not in noeuds_visites:
                    noeuds_visites.append(curr)
                    
                if f > seuil_courant:
                    return f, None
                    
                log_ida(11, curr, chemin)
                if curr == self.goal_state:
                    self.solution_trouvee = True
                    log_ida(11, curr, chemin, msg="SUCCESS : Objectif découvert !")
                    return "SUCCESS", chemin
                    
                min_f = float('inf')
                log_ida(12, curr, chemin)
                log_ida(13, curr, chemin)
                
                for succ, _ in self.obtenir_successeurs(curr):
                    if self.solution_trouvee: break
                    if succ not in chemin:
                        f_succ = (g + 1) + f_heuristique(succ)
                        frontiere_virtuelle.append((succ, chemin + [succ], g + 1, f_succ))
                        log_ida(14, curr, chemin, hl_push=True)
                        
                        res, res_path = recherche_rec(chemin + [succ], g + 1, seuil_courant)
                        
                        if frontiere_virtuelle:
                            popped = frontiere_virtuelle.pop()
                            log_ida(15, curr, chemin, hl_pop=popped[0])
                        
                        if res == "SUCCESS":
                            return "SUCCESS", res_path
                        if res < min_f:
                            min_f = res
                
                if not self.solution_trouvee:
                    log_ida(16, curr, chemin)
                return min_f, None

            while not self.solution_trouvee:
                log_ida(2, etat_initial, [], msg=f"Nouvelle itération : Seuil fixe = {seuil}")
                log_ida(3, etat_initial, [])
                status, path_resolu = recherche_rec([etat_initial], 0, seuil)
                if status == "SUCCESS" or self.solution_trouvee:
                    break
                if status == float('inf') or seuil == status:
                    log_ida(5, etat_initial, [], msg="FAIL : Impossible de résoudre")
                    break
                log_ida(6, etat_initial, [])
                seuil = status
                
        else:
            frontiere = [(etat_initial, [etat_initial])]
            
            def log_dfs(ligne, curr, path, hl_push=False, hl_pop=None, hl_v=False, msg=None):
                if self.solution_trouvee: return
                stack_copy = [(item[0], list(item[1])) for item in frontiere]
                self.historique.append({
                    "line": ligne, "stack": stack_copy, "visited": list(noeuds_visites),
                    "path": list(path), "curr": curr, "hl_push": hl_push, "hl_pop_node": hl_pop,
                    "hl_v": hl_v, "msg": msg
                })

            log_dfs(1, etat_initial, [], hl_push=True)
            while frontiere and not self.solution_trouvee:
                log_dfs(2, None, [])
                curr, path = frontiere.pop()
                log_dfs(3, curr, path, hl_pop=curr)
                
                log_dfs(4, curr, path)
                if curr == self.goal_state:
                    self.solution_trouvee = True
                    log_dfs(4, curr, path, msg="SUCCESS : Objectif trouvé")
                    break
                    
                log_dfs(5, curr, path)
                if curr not in noeuds_visites:
                    noeuds_visites.append(curr)
                    log_dfs(6, curr, path, hl_v=True)
                    
                    log_dfs(7, curr, path)
                    for succ, _ in reversed(self.obtenir_successeurs(curr)):
                        if self.solution_trouvee: break
                        log_dfs(8, curr, path)
                        if succ not in noeuds_visites and succ not in [f[0] for f in frontiere]:
                            log_dfs(9, curr, path)
                            frontiere.append((succ, path + [succ]))
                            log_dfs(10, curr, path, hl_push=True)

        self.temps_calcul_ms = (time.perf_counter() - start_time) * 1000
        self.index_historique = 0

    def activer_mode_chemin_optimal(self):
        if not self.historique: return
        self.mettre_en_pause()
            
        dernier_état = self.historique[-1]
        chemin_optimal = dernier_état["path"]
        
        if not chemin_optimal:
            chemin_optimal = [tuple(self.board_state)]
            
        historique_filtre = []
        for index, etat_validation in enumerate(chemin_optimal):
            historique_filtre.append({
                "line": 4, 
                "stack": [], 
                "visited": list(chemin_optimal[:index]),
                "path": list(chemin_optimal[:index+1]), 
                "curr": etat_validation,
                "msg": f"Affichage Optimal - Étape {index} / {len(chemin_optimal)-1}"
            })
            
        self.historique = historique_filtre
        self.index_historique = 0
        self.mode_chemin_optimal = True
        self.restaurer_etat_index_visuel()

    def dessiner_plateau_dynamique(self, config_manuelle=None):
        configuration_actuelle = config_manuelle
        
        if configuration_actuelle is None:
            if not self.historique or self.index_historique < 0 or self.index_historique >= len(self.historique):
                configuration_actuelle = tuple(self.board_state)
            else:
                etat = self.historique[self.index_historique]
                configuration_actuelle = etat["curr"] if etat["curr"] else tuple(self.board_state)
        
        self.canvas.delete("all")
        canv_w = self.canvas.winfo_width()
        canv_h = self.canvas.winfo_height()
        
        taille_utile = min(canv_w, canv_h) - 10
        if taille_utile < 100: 
            taille_utile = 400 
            
        offset_x = (canv_w - taille_utile) / 2
        offset_y = (canv_h - taille_utile) / 2
        tc = taille_utile / self.taille_grille
        
        for r in range(self.taille_grille):
            for c in range(self.taille_grille):
                idx = r * self.taille_grille + c
                val = configuration_actuelle[idx]
                
                x1, y1 = offset_x + (c * tc), offset_y + (r * tc)
                x2, y2 = x1 + tc, y1 + tc
                
                if val != 0:
                    if val == self.goal_state[idx]:
                        couleur_bloc = "#10b981" 
                    else:
                        couleur_bloc = "#3b82f6" if val % 2 == 0 else "#f59e0b" 
                        
                    self.canvas.create_rectangle(x1+4, y1+4, x2-4, y2-4, fill=couleur_bloc, outline="#ffffff", width=2)
                    self.canvas.create_text(x1 + tc/2, y1 + tc/2, text=str(val), font=("Arial", int(tc//2.8), "bold"), fill="#ffffff")
                else:
                    self.canvas.create_rectangle(x1+4, y1+4, x2-4, y2-4, fill="#1e293b", outline="#334155", width=1)

    def dessiner_plateau_sans_historique(self):
        self.lbl_stats.config(text="📊 En attente de calcul... | Cliquez sur 'Calculer la Solution'")
        self.dessiner_plateau_dynamique(config_manuelle=tuple(self.board_state))
        
        self.txt_structure.delete(1.0, tk.END)
        self.txt_structure.insert(tk.END, "\n   [ En attente de calcul... ]")
        
        self.txt_visites.delete(1.0, tk.END)
        self.txt_visites.insert(tk.END, "\n   [ En attente de calcul... ]")
        
        self.txt_chemin.delete(1.0, tk.END)
        self.txt_chemin.insert(tk.END, "\n   [ En attente de calcul... ]")

    def restaurer_etat_index_visuel(self):
        if not self.historique:
            self.dessiner_plateau_sans_historique()
            return
            
        etat = self.historique[self.index_historique]
        algo = self.combo_algo.get()
        est_dfs = "DFS" in algo
        
        nb_vis = len(etat["visited"])
        txt_msg = f"  |  ℹ️ {etat['msg']}" if etat.get("msg") else ""
        self.lbl_stats.config(text=f"📊 Nœuds explorés : {nb_vis}  |  ⏱️ Temps calcul : {self.temps_calcul_ms:.2f} ms{txt_msg}")

        self.listbox_code.selection_clear(0, tk.END)
        self.listbox_code.selection_set(etat["line"] - 1)
        self.listbox_code.see(etat["line"] - 1)

        self.dessiner_plateau_dynamique()

        self.txt_structure.delete(1.0, tk.END)
        if etat.get("hl_pop_node"):
            self.txt_structure.insert(tk.END, f" ❌ [POP / EXPLORÉ] :\n {str(etat['hl_pop_node'])}\n", "hl_pop")
            self.txt_structure.insert(tk.END, "-"*40 + "\n")

        if not etat["stack"]:
            self.txt_structure.insert(tk.END, "\n   [ Pile de la frontière vide ]")
        else:
            titre = " 🔥 PILE ACTIVE (DFS LIFO) :\n" if est_dfs else " 🔄 FRONTIÈRE DES APPELS (IDA*) :\n"
            self.txt_structure.insert(tk.END, titre)
            
            elements = list(reversed(etat["stack"])) if est_dfs else etat["stack"]
            for i, item in enumerate(elements[:150]):
                if not est_dfs:
                    node, path, g, f = item
                    corps = f"  [{i:02d}] {node} | f={f}\n"
                else:
                    node, path = item
                    corps = f"  [{i:02d}] {node}\n"
                
                if i == 0 and etat.get("hl_push"):
                    self.txt_structure.insert(tk.END, corps, "hl_push")
                else:
                    self.txt_structure.insert(tk.END, corps)
            if len(elements) > 150:
                self.txt_structure.insert(tk.END, f"   ... (+ {len(elements)-150} nœuds masqués)")

        self.txt_visites.delete(1.0, tk.END)
        if not etat["visited"]:
            self.txt_visites.insert(tk.END, "\n   [ Aucun nœud visité ]")
        else:
            for idx, v_node in enumerate(etat["visited"][-200:]):
                corps_v = f" #{idx+1:03d} : {v_node}\n"
                if idx == len(etat["visited"][-200:]) - 1 and etat.get("hl_v"):
                    self.txt_visites.insert(tk.END, corps_v, "hl_visite")
                else:
                    self.txt_visites.insert(tk.END, corps_v)

        self.txt_chemin.delete(1.0, tk.END)
        if not etat["path"]:
            self.txt_chemin.insert(tk.END, "[ Aucun chemin d'exploration actif ]")
        else:
            self.txt_chemin.insert(tk.END, f"► Trajectoire : {len(etat['path'])} nœuds\n\n", "hl_alert")
            for step_idx, step_state in enumerate(etat["path"]):
                self.txt_chemin.insert(tk.END, f" Etape {step_idx:02d} ➔ {step_state}\n")
            if etat.get("msg") and "SUCCESS" in etat["msg"]:
                self.txt_chemin.insert(tk.END, "\n🎯 [CIBLE ATTEINTE EN POSITION ORDONNÉE !]", "hl_success")

    def etape_avant(self):
        if not self.historique: return
        if self.index_historique < len(self.historique) - 1:
            self.index_historique += 1
            self.restaurer_etat_index_visuel()
        else:
            self.mettre_en_pause()

    def etape_arriere(self):
        if not self.historique: return
        if self.index_historique > 0:
            self.index_historique -= 1
            self.restaurer_etat_index_visuel()

    def lancer_animation_auto(self):
        # Si aucun calcul n'a été fait, forcer le calcul d'abord
        if not self.historique:
            self.lancer_calcul()
            
        self.en_cours = True
        self.bouton_demarrer.config(state=tk.DISABLED)
        self.bouton_pause.config(state=tk.NORMAL)
        self.bouton_avancer.config(state=tk.DISABLED)
        self.bouton_retour.config(state=tk.DISABLED)
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

    def reinitialiser_simulation(self):
        self.mettre_en_pause()
        self.changer_taille_puzzle()

    def ouvrir_fenetre_comparaison(self):
        fenetre_comp = tk.Toplevel(self)
        fenetre_comp.title("Comparateur Analytique Multicritères")
        fenetre_comp.geometry("740x460")
        fenetre_comp.configure(bg="#f8fafc")
        
        # Modification du titre de la fenêtre de comparaison
        tk.Label(fenetre_comp, text="📊 Comparaison des algorithmes", font=("Arial", 12, "bold"), bg="#f8fafc", fg="#1e293b").pack(pady=10)
        
        cadre_choix = tk.Frame(fenetre_comp, bg="#f8fafc")
        cadre_choix.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(cadre_choix, text="Méthode A:", bg="#f8fafc").grid(row=0, column=0, padx=5)
        c1 = ttk.Combobox(cadre_choix, values=["IDA* (Heuristique Manhattan)", "IDA* (Heuristique Hamming)", "DFS (Profondeur d'abord)"], state="readonly")
        c1.set("IDA* (Heuristique Manhattan)")
        c1.grid(row=0, column=1, padx=5)
        
        tk.Label(cadre_choix, text="Méthode B:", bg="#f8fafc").grid(row=0, column=2, padx=5)
        c2 = ttk.Combobox(cadre_choix, values=["IDA* (Heuristique Manhattan)", "IDA* (Heuristique Hamming)", "DFS (Profondeur d'abord)"], state="readonly")
        c2.set("IDA* (Heuristique Hamming)")
        c2.grid(row=0, column=3, padx=5)

        colonnes = ("critere", "algo1", "algo2")
        tableau = ttk.Treeview(fenetre_comp, columns=colonnes, show="headings", height=6)
        
        # Les en-têtes dynamiques
        tableau.heading("critere", text="Indicateurs de Performance")
        tableau.heading("algo1", text="Méthode A")
        tableau.heading("algo2", text="Méthode B")
        
        tableau.column("critere", width=280, anchor="center")
        tableau.column("algo1", width=200, anchor="center")
        tableau.column("algo2", width=200, anchor="center")
        tableau.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        def executer_comparaison_interne():
            algo1_nom = c1.get()
            algo2_nom = c2.get()
            
            # Mise à jour des noms d'algorithmes dans le tableau dynamiquement
            tableau.heading("algo1", text=algo1_nom)
            tableau.heading("algo2", text=algo2_nom)
            
            sauvegarde_algo = self.combo_algo.get()
            
            self.combo_algo.set(algo1_nom)
            self.compiler_historique_recherche()
            t1 = f"{self.temps_calcul_ms:.2f} ms"
            path1 = len(self.historique[-1]["path"]) if self.historique else 0
            vis1 = len(self.historique[-1]["visited"]) if self.historique else 0
            
            self.combo_algo.set(algo2_nom)
            self.compiler_historique_recherche()
            t2 = f"{self.temps_calcul_ms:.2f} ms"
            path2 = len(self.historique[-1]["path"]) if self.historique else 0
            vis2 = len(self.historique[-1]["visited"]) if self.historique else 0
            
            self.combo_algo.set(sauvegarde_algo)
            # Pas besoin de recompiler la sauvegarde pour le main thread si l'user ne l'a pas demandé
            
            for item in tableau.get_children(): 
                tableau.delete(item)
            
            tableau.insert("", tk.END, values=("Temps d'exécution de la recherche", t1, t2))
            tableau.insert("", tk.END, values=("Volume global des nœuds visités", vis1, vis2))
            tableau.insert("", tk.END, values=("Profondeur finale (Longueur solution)", path1, path2))

        tk.Button(fenetre_comp, text="🚀 Lancer la Comparaison", bg="#10b981", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=executer_comparaison_interne).pack(pady=10)

if __name__ == "__main__":
    app = VisualisateurNPuzzle()
    app.update()
    app.restaurer_etat_index_visuel()
    app.mainloop()