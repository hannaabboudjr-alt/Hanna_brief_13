"""
========================================================================
 CONSTRUIRE LA BASE SQLITE A PARTIR DES CSV — méthode du cours
========================================================================

On suit exactement le schéma de collecte vu dans le récapitulatif du
cours :

    1. se connecter à la source                (ici : pas besoin, un CSV
                                                  se lit directement avec
                                                  pd.read_csv, pas de
                                                  moteur SQLAlchemy)
    2. LA REQUÊTE DE COLLECTE                   pd.read_csv(...)
    3. écrire chez soi                          df.to_sql(..., con,
                                                  if_exists="replace")

if_exists="replace" rend le script REJOUABLE : on peut le relancer
plusieurs fois, le résultat est toujours le même (pas de doublons),
contrairement à if_exists="append" qui doublerait les données à chaque
nouvelle exécution.

On horodate aussi la collecte (colonne collecte_le), comme demandé dans
la checklist du cours : ça permet de savoir QUAND les données ont été
récupérées.
========================================================================
"""

import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd

DOSSIER = Path(__file__).parent
BASE_SQLITE = DOSSIER / "risques_pro.db"

# "con" : on se connecte à SA PROPRE base (celle qu'on construit),
# pas à la source. C'est le nom utilisé dans le cours pour cette
# connexion de destination.
con = sqlite3.connect(BASE_SQLITE)

# On horodate une seule fois, pour que tous les CSV de cette exécution
# aient exactement le même instant de collecte.
collecte_le = datetime.now()

for fichier_csv in DOSSIER.glob("*.csv"):

    # Le nom de la table = le nom du fichier, sans l'extension ".csv".
    nom_table = fichier_csv.stem

    # ---- 2. LA REQUÊTE DE COLLECTE ----
    # Pour une base source, ce serait pd.read_sql("SELECT ...", engine).
    # Pour un CSV, pas de connexion à ouvrir : pd.read_csv() suffit.
    df = pd.read_csv(fichier_csv, sep=";")

    # On ajoute la colonne d'horodatage, comme vu en cours.
    df["collecte_le"] = collecte_le

    # ---- 3. écrire chez soi ----
    df.to_sql(nom_table, con, if_exists="replace", index=False)

    print(f"{nom_table:20} {len(df):>7} lignes")

con.close()
print(f"\nBase créée : {BASE_SQLITE}")
