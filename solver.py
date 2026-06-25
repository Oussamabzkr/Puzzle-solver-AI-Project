import tkinter as tk
from tkinter import ttk, messagebox
import time
import random

# ==========================================
# MOTEUR DE RÉSOLUTION (BACK-END)
# ==========================================

def obtenir_objectif(n):
    return tuple(list(range(1, n * n)) + [0])

def analyser_resolubilite(etat, n):
    """
    Retourne un tuple : (est_resoluble, inversions, ligne_vide_depuis_bas)
    Pour fournir plus de détails dans l'interface graphique.
    """
    inversions = 0
    etat_sans_zero = [x for x in etat if x != 0]
    for i in range(len(etat_sans_zero)):
        for j in range(i + 1, len(etat_sans_zero)):
            if etat_sans_zero[i] > etat_sans_zero[j]:
                inversions += 1
                
    if n % 2 != 0: 
        # Grille impaire (ex: 3x3)
        est_res = (inversions % 2 == 0)
        return est_res, inversions, None
    else: 
        # Grille paire (ex: 4x4)
        idx_zero = etat.index(0)
        ligne_depuis_bas = n - (idx_zero // n)
        est_res = ((inversions + ligne_depuis_bas) % 2 == 1)
        return est_res, inversions, ligne_depuis_bas

def distance_hamming(etat, objectif):
    return sum(1 for i, val in enumerate(etat) if val != 0 and val != objectif[i])

def distance_manhattan(etat, n):
    dist = 0
    for i, val in enumerate(etat):
        if val == 0: continue
        idx_objectif = val - 1 
        x1, y1 = i % n, i // n
        x2, y2 = idx_objectif % n, idx_objectif // n
        dist += abs(x1 - x2) + abs(y1 - y2)
    return dist

def obtenir_voisins(etat, n):
    voisins = []
    idx_zero = etat.index(0)
    x, y = idx_zero % n, idx_zero // n
    mouvements = [(0, -1), (0, 1), (-1, 0), (1, 0)] # Haut, Bas, Gauche, Droite
    for dx, dy in mouvements:
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n:
            nouvel_idx = ny * n + nx
            nouvel_etat = list(etat)
            nouvel_etat[idx_zero], nouvel_etat[nouvel_idx] = nouvel_etat[nouvel_idx], nouvel_etat[idx_zero]
            voisins.append(tuple(nouvel_etat))
    return voisins

def ida_etoile(etat_initial, n, type_heuristique='manhattan'):
    objectif = obtenir_objectif(n)
    
    def h(etat):
        if type_heuristique == 'manhattan':
            return distance_manhattan(etat, n)
        return distance_hamming(etat, objectif)

    noeuds_explores = [0]

    def recherche(chemin, ensemble_chemin, g, limite):
        noeud = chemin[-1]
        noeuds_explores[0] += 1
        f = g + h(noeud)
        if f > limite: return f
        if noeud == objectif: return "TROUVE"
            
        limite_min = float('inf')
        for voisin in obtenir_voisins(noeud, n):
            if voisin not in ensemble_chemin:
                chemin.append(voisin)
                ensemble_chemin.add(voisin)
                t = recherche(chemin, ensemble_chemin, g + 1, limite)
                if t == "TROUVE": return "TROUVE"
                if t < limite_min: limite_min = t
                chemin.pop()
                ensemble_chemin.remove(voisin)
        return limite_min

    limite = h(etat_initial)
    chemin = [etat_initial]
    ensemble_chemin = {etat_initial}
    
    while True:
        t = recherche(chemin, ensemble_chemin, 0, limite)
        if t == "TROUVE":
            return chemin, noeuds_explores[0]
        if t == float('inf'):
            return None, noeuds_explores[0]
        limite = t

def generer_puzzle(n, mouvements_difficulte=20):
    etat = obtenir_objectif(n)
    for _ in range(mouvements_difficulte):
        voisins = obtenir_voisins(etat, n)
        etat = random.choice(voisins)
    return etat

# ==========================================
# INTERFACE GRAPHIQUE (FRONT-END avec Tkinter)
# ==========================================

class ApplicationPuzzle(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Solveur de Puzzle 8 et 15 (IDA*)")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")
        
        self.n = 3 # Par défaut: Puzzle 8 (3x3)
        self.etat_actuel = obtenir_objectif(self.n)
        self.chemin_solution = []
        self.index_etape = 0
        self.lecture_en_cours = False
        
        self.creer_widgets()
        self.dessiner_plateau()
        self.log("Bienvenue ! Générez un puzzle pour commencer.")

    def creer_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- ZONE GAUCHE : PLATEAU ---
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(left_frame, width=400, height=400, bg="white", highlightthickness=2)
        self.canvas.pack(pady=10)
        
        # Contrôles de relecture visuelle
        relecture_frame = tk.Frame(left_frame, bg="#f0f0f0")
        relecture_frame.pack(pady=5)
        
        self.btn_prev = ttk.Button(relecture_frame, text="◀ Précédent", command=self.etape_precedente, state=tk.DISABLED)
        self.btn_prev.grid(row=0, column=0, padx=5)
        
        self.btn_auto = ttk.Button(relecture_frame, text="▶ Lecture Auto", command=self.basculer_lecture_auto, state=tk.DISABLED)
        self.btn_auto.grid(row=0, column=1, padx=5)
        
        self.btn_next = ttk.Button(relecture_frame, text="Suivant ▶", command=self.etape_suivante, state=tk.DISABLED)
        self.btn_next.grid(row=0, column=2, padx=5)
        
        self.lbl_etape = tk.Label(left_frame, text="Étape : 0 / 0", bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.lbl_etape.pack()

        # --- ZONE DROITE : CONTRÔLES ET LOGS ---
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20)
        
        # Paramètres
        params_frame = tk.LabelFrame(right_frame, text="Paramètres du Puzzle", bg="#f0f0f0", padx=10, pady=10)
        params_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(params_frame, text="Taille :", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.var_taille = tk.IntVar(value=3)
        ttk.Radiobutton(params_frame, text="Puzzle-8", variable=self.var_taille, value=3).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(params_frame, text="Puzzle-15", variable=self.var_taille, value=4).grid(row=0, column=2, sticky="w")
        
        tk.Label(params_frame, text="Difficulté :", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=5)
        self.var_difficulte = tk.StringVar(value="Facile")
        
        niveaux = ["Facile", "Moyen", "Difficile", "Très Difficile", "Extrême"]
        combo_diff = ttk.Combobox(params_frame, textvariable=self.var_difficulte, values=niveaux, state="readonly", width=25)
        combo_diff.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)
        
        ttk.Button(params_frame, text="Générer un Puzzle Aléatoire", command=self.generer_nouveau).grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Actions de Résolution
        actions_frame = tk.LabelFrame(right_frame, text="Résolution et Comparaison", bg="#f0f0f0", padx=10, pady=10)
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="Résoudre avec Manhattan (Rapide)", command=lambda: self.lancer_resolution('manhattan')).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Résoudre avec Hamming (Lent)", command=lambda: self.lancer_resolution('hamming')).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Générer Tableau de Comparaison (Les 2 heuristiques)", command=self.lancer_comparaison).pack(fill=tk.X, pady=8)
        
        # Console de sortie
        tk.Label(right_frame, text="Console des résultats :", bg="#f0f0f0").pack(anchor="w")
        self.text_log = tk.Text(right_frame, height=18, width=50, bg="black", fg="#00FF00", font=("Consolas", 9))
        self.text_log.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        """Affiche un message dans la console de l'application"""
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)
        self.update_idletasks()

    def dessiner_plateau(self):
        """Moteur de rendu du plateau sur le Canvas"""
        self.canvas.delete("all")
        taille_case = 400 // self.n
        
        for i, val in enumerate(self.etat_actuel):
            x = (i % self.n) * taille_case
            y = (i // self.n) * taille_case
            
            if val == 0:
                self.canvas.create_rectangle(x, y, x+taille_case, y+taille_case, fill="#d3d3d3", outline="gray")
            else:
                couleur = "#4a90e2" if val % 2 == 0 else "#50e3c2"
                if val == i + 1: couleur = "#27ae60" # Vert si à la bonne place
                
                self.canvas.create_rectangle(x+2, y+2, x+taille_case-2, y+taille_case-2, fill=couleur, outline="black", width=2)
                self.canvas.create_text(x + taille_case//2, y + taille_case//2, text=str(val), font=("Arial", 24, "bold"), fill="white")

    def generer_nouveau(self):
        self.n = self.var_taille.get()
        diff_str = self.var_difficulte.get()
        
        mapping_difficulte = {
            "Facile": 15,
            "Moyen": 30,
            "Difficile": 50,
            "Très Difficile": 80,
            "Extrême": 120
        }
        coups = mapping_difficulte.get(diff_str, 20)
        
        self.text_log.delete(1.0, tk.END)
        self.log(f"--- GÉNÉRATION : Puzzle {self.n}x{self.n} [{diff_str}] ---")
        
        self.etat_actuel = generer_puzzle(self.n, mouvements_difficulte=coups)
        
        est_res, inversions, ligne_vide = analyser_resolubilite(self.etat_actuel, self.n)
        
        self.log("\n[Parité et Résolubilité]")
        self.log(f" > Nombre d'inversions trouvées : {inversions}")
        
        if self.n % 2 != 0:
            self.log(" > Règle (Grille impaire) : Les inversions doivent être paires.")
            self.log(f" > {inversions} est un nombre {'pair' if inversions % 2 == 0 else 'impair'}.")
        else:
            self.log(f" > Position case vide (depuis le bas) : {ligne_vide}")
            somme = inversions + ligne_vide
            self.log(f" > Somme (Inversions + Ligne) : {somme}")
            self.log(" > Règle (Grille paire) : La somme doit être impaire.")
            self.log(f" > {somme} est un nombre {'impair' if somme % 2 != 0 else 'pair'}.")
            
        if est_res:
            self.log("\n=> Le plateau EST SOLUBLE")
        else:
            self.log("\n=> Le plateau est INSOLUBLE")
            
        self.chemin_solution = []
        self.index_etape = 0
        self.btn_next.config(state=tk.DISABLED)
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED)
        self.lbl_etape.config(text="Étape : 0 / 0")
        self.dessiner_plateau()
        self.log("-" * 40)

    def lancer_resolution(self, heuristique):
        est_res, _, _ = analyser_resolubilite(self.etat_actuel, self.n)
        if not est_res:
            messagebox.showerror("Erreur", "Configuration insoluble.")
            return
            
        self.log(f"\n[Recherche IDA* avec heuristique : {heuristique.upper()}]...")
        debut = time.time()
        resultat = ida_etoile(self.etat_actuel, self.n, type_heuristique=heuristique)
        # Conversion du temps en millisecondes
        temps_ecoule = (time.time() - debut) * 1000
        
        if resultat[0] is not None:
            self.chemin_solution = resultat[0]
            noeuds = resultat[1]
            profondeur = len(self.chemin_solution) - 1
            
            self.log(f"Solution trouvée !")
            self.log(f"  - Temps d'exécution : {temps_ecoule:.2f} ms")
            self.log(f"  - Noeuds explorés   : {noeuds}")
            self.log(f"  - Profondeur        : {profondeur} mouvements")
            
            self.index_etape = 0
            self.btn_next.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.NORMAL)
            self.lbl_etape.config(text=f"Étape : 0 / {profondeur}")
            self.dessiner_plateau()
        else:
            self.log("Échec de la résolution.")

    def lancer_comparaison(self):
        est_res, _, _ = analyser_resolubilite(self.etat_actuel, self.n)
        if not est_res: return
            
        difficulte_choisie = self.var_difficulte.get()
        if self.n == 4 and difficulte_choisie in ["Difficile", "Très Difficile", "Extrême"]:
            rep = messagebox.askyesno("Attention Temps", "Utiliser Hamming sur un Puzzle-15 difficile peut prendre énormément de temps (voire bloquer l'interface). Voulez-vous continuer ?")
            if not rep: return
            
        self.log("\n" + "="*45)
        self.log(" TABLEAU DE COMPARAISON")
        self.log("="*45)
        
        self.log("Exécution de Manhattan en cours...")
        t_debut = time.time()
        res_man = ida_etoile(self.etat_actuel, self.n, 'manhattan')
        t_man = (time.time() - t_debut) * 1000 # En millisecondes
        
        self.log("Exécution de Hamming en cours...")
        t_debut = time.time()
        res_ham = ida_etoile(self.etat_actuel, self.n, 'hamming')
        t_ham = (time.time() - t_debut) * 1000 # En millisecondes
        
        self.log("\nRÉSULTATS :")
        self.log(f"{' ':<15}| {'Manhattan':<12}| {'Hamming':<12}")
        self.log("-" * 45)
        self.log(f"{'Profondeur':<15}| {len(res_man[0])-1:<12}| {len(res_ham[0])-1:<12}")
        self.log(f"{'Noeuds exp.':<15}| {res_man[1]:<12}| {res_ham[1]:<12}")
        self.log(f"{'Temps (ms)':<15}| {t_man:<12.2f}| {t_ham:<12.2f}")
        self.log("="*45)
        
        # Préparer la relecture avec Manhattan
        self.chemin_solution = res_man[0]
        self.index_etape = 0
        self.btn_next.config(state=tk.NORMAL)
        self.btn_auto.config(state=tk.NORMAL)
        self.lbl_etape.config(text=f"Étape : 0 / {len(self.chemin_solution)-1}")

    # --- MÉTHODES DE RELECTURE VISUELLE ---
    def etape_suivante(self):
        if self.index_etape < len(self.chemin_solution) - 1:
            self.index_etape += 1
            self.etat_actuel = self.chemin_solution[self.index_etape]
            self.dessiner_plateau()
            self.btn_prev.config(state=tk.NORMAL)
            self.lbl_etape.config(text=f"Étape : {self.index_etape} / {len(self.chemin_solution)-1}")
            if self.index_etape == len(self.chemin_solution) - 1:
                self.btn_next.config(state=tk.DISABLED)
                self.lecture_en_cours = False
                self.btn_auto.config(text="▶ Lecture Auto")

    def etape_precedente(self):
        if self.index_etape > 0:
            self.index_etape -= 1
            self.etat_actuel = self.chemin_solution[self.index_etape]
            self.dessiner_plateau()
            self.btn_next.config(state=tk.NORMAL)
            self.lbl_etape.config(text=f"Étape : {self.index_etape} / {len(self.chemin_solution)-1}")
            if self.index_etape == 0:
                self.btn_prev.config(state=tk.DISABLED)

    def basculer_lecture_auto(self):
        if not self.lecture_en_cours:
            if self.index_etape == len(self.chemin_solution) - 1:
                self.index_etape = 0
            self.lecture_en_cours = True
            self.btn_auto.config(text="⏸ Pause")
            self.jouer_animation()
        else:
            self.lecture_en_cours = False
            self.btn_auto.config(text="▶ Lecture Auto")

    def jouer_animation(self):
        if self.lecture_en_cours and self.index_etape < len(self.chemin_solution) - 1:
            self.etape_suivante()
            self.after(300, self.jouer_animation)

if __name__ == "__main__":
    app = ApplicationPuzzle()
    app.mainloop()