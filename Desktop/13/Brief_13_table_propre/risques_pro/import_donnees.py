"""
Importe les 6 fichiers *_nettoye.csv dans une base SQLite (risques_pro.db)
selon le schema_mld.sql à clés surrogates (id_xxx auto-incrémentées).

Usage :
    python import_donnees.py [dossier_csv]

Par défaut, le script cherche les CSV dans son propre dossier. Passe un
chemin en argument si tes fichiers sont ailleurs (ex: ton dossier Téléchargements).

Les CSV attendus (séparateur ";") :
    df_activitenettoye.csv, df_causenettoye.csv, df_hfnettoye.csv,
    df_partienettoye.csv, df_regionnettoye.csv, df_depensenettoye.csv
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

CSV_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
SCHEMA_FILE = Path(__file__).parent / "schema_mld.sql"
DB_FILE = Path(__file__).parent / "risques_pro.db"

FILES = {
    "activite": "df_activitenettoye.csv",
    "cause":    "df_causenettoye.csv",
    "hf":       "df_hfnettoye.csv",
    "partie":   "df_partienettoye.csv",
    "region":   "df_regionnettoye.csv",
    "depense":  "df_depensenettoye.csv",
}


def load(name):
    path = CSV_DIR / FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Introuvable : {path}")
    return pd.read_csv(path, sep=";")


def ids(conn, table, id_col, key_col):
    """Relit une table de dimension et renvoie un DataFrame [key_col, id_col]
    pour pouvoir associer chaque ligne source à sa clé surrogate."""
    return pd.read_sql(f"SELECT {id_col}, {key_col} FROM {table}", conn)


def main():
    if DB_FILE.exists():
        DB_FILE.unlink()
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

    df_activite = load("activite")
    df_cause    = load("cause")
    df_hf       = load("hf")
    df_partie   = load("partie")
    df_region   = load("region")
    df_depense  = load("depense")

    # ---------- 1. Dimensions (valeurs distinctes -> id_xxx auto) ----------

    df_activite[["code_NAF5", "libelle_NAF5"]].drop_duplicates() \
        .to_sql("NAF5", conn, if_exists="append", index=False)

    pd.concat([df_activite["risque"], df_region["risque"], df_depense["risque"]]) \
        .drop_duplicates().to_frame("risque") \
        .to_sql("Risque", conn, if_exists="append", index=False)

    df_cause[["libelle_cause_TR"]].drop_duplicates() \
        .to_sql("Cause", conn, if_exists="append", index=False)

    df_partie[["partie_corps"]].drop_duplicates() \
        .to_sql("PartieCorps", conn, if_exists="append", index=False)

    df_region[["libelle_region_admin"]].drop_duplicates() \
        .to_sql("Region", conn, if_exists="append", index=False)

    conn.commit()

    # ---------- 2. Faits : associer chaque ligne source à la clé surrogate ----------

    naf5   = ids(conn, "NAF5", "id_naf5", "code_NAF5")
    risque = ids(conn, "Risque", "id_risque", "risque")
    cause  = ids(conn, "Cause", "id_cause", "libelle_cause_TR")
    partie = ids(conn, "PartieCorps", "id_partie", "partie_corps")
    region = ids(conn, "Region", "id_region", "libelle_region_admin")

    activite = df_activite.merge(naf5, on="code_NAF5").merge(risque, on="risque")
    activite[["annee", "nb_jours_arret_travail", "id_naf5", "id_risque"]] \
        .to_sql("Activite", conn, if_exists="append", index=False)

    causefait = df_cause.merge(naf5, on="code_NAF5").merge(cause, on="libelle_cause_TR")
    causefait[["annee", "id_naf5", "id_cause"]] \
        .to_sql("CauseFait", conn, if_exists="append", index=False)

    hf = df_hf.merge(naf5, on="code_NAF5")
    hf[["annee", "sexe", "id_naf5"]] \
        .to_sql("HF", conn, if_exists="append", index=False)

    partiefait = df_partie.merge(naf5, on="code_NAF5").merge(partie, on="partie_corps")
    partiefait[["annee", "id_naf5", "id_partie"]] \
        .to_sql("PartieCorpsFait", conn, if_exists="append", index=False)

    sinistres = df_region.merge(region, on="libelle_region_admin").merge(risque, on="risque")
    sinistres[["annee", "nb_salaries", "nb_sinistres_int", "id_region", "id_risque"]] \
        .to_sql("SinistresRegion", conn, if_exists="append", index=False)

    depenses = df_depense.merge(risque, on="risque")
    depenses[["annee", "montant_depenses", "poste_depenses", "id_risque"]] \
        .to_sql("Depenses", conn, if_exists="append", index=False)

    conn.commit()

    # ---------- 3. Contrôle ----------
    print(f"Base créée : {DB_FILE}")
    for table in ["NAF5", "Risque", "Cause", "PartieCorps", "Region",
                  "Activite", "CauseFait", "HF", "PartieCorpsFait",
                  "SinistresRegion", "Depenses"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:18s} {n:>7} lignes")

    conn.close()


if __name__ == "__main__":
    main()
