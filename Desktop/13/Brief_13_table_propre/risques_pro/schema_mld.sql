-- =========================================================
-- MLD — base "Risques professionnels" (SQLite)
-- Version alignée sur le schéma avec clés surrogates (id_xxx)
-- =========================================================

PRAGMA foreign_keys = ON;

-- ---------- Dimensions ----------

CREATE TABLE NAF5 (
    id_naf5      INTEGER PRIMARY KEY AUTOINCREMENT,
    code_NAF5    TEXT NOT NULL UNIQUE,
    libelle_NAF5 TEXT NOT NULL
);

CREATE TABLE Risque (
    id_risque INTEGER PRIMARY KEY AUTOINCREMENT,
    risque    TEXT NOT NULL UNIQUE
);

CREATE TABLE Cause (
    id_cause         INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle_cause_TR TEXT NOT NULL UNIQUE
);

CREATE TABLE PartieCorps (
    id_partie    INTEGER PRIMARY KEY AUTOINCREMENT,
    partie_corps TEXT NOT NULL UNIQUE
);

CREATE TABLE Region (
    id_region             INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle_region_admin  TEXT NOT NULL UNIQUE
);

-- ---------- Faits ----------
-- UNIQUE(...) reconstitue la clé naturelle (annee + dimensions) que la
-- clé surrogate id_xxx ne protège plus toute seule : sans elle, rien
-- n'empêche deux lignes identiques d'exister avec des id différents.

CREATE TABLE Activite (
    id_activite             INTEGER PRIMARY KEY AUTOINCREMENT,
    annee                   INTEGER NOT NULL,
    nb_jours_arret_travail  REAL,
    id_naf5                 INTEGER NOT NULL REFERENCES NAF5(id_naf5),
    id_risque               INTEGER NOT NULL REFERENCES Risque(id_risque),
    UNIQUE (annee, id_naf5, id_risque)
);

CREATE TABLE CauseFait (
    id_cause_fait INTEGER PRIMARY KEY AUTOINCREMENT,
    annee         INTEGER NOT NULL,
    id_naf5       INTEGER NOT NULL REFERENCES NAF5(id_naf5),
    id_cause      INTEGER NOT NULL REFERENCES Cause(id_cause),
    UNIQUE (annee, id_naf5, id_cause)
);

CREATE TABLE HF (
    id_hf   INTEGER PRIMARY KEY AUTOINCREMENT,
    annee   INTEGER NOT NULL,
    sexe    TEXT NOT NULL CHECK (sexe IN ('Hommes', 'Femmes')),
    id_naf5 INTEGER NOT NULL REFERENCES NAF5(id_naf5),
    UNIQUE (annee, id_naf5, sexe)
);

CREATE TABLE PartieCorpsFait (
    id_partie_fait INTEGER PRIMARY KEY AUTOINCREMENT,
    annee          INTEGER NOT NULL,
    id_naf5        INTEGER NOT NULL REFERENCES NAF5(id_naf5),
    id_partie      INTEGER NOT NULL REFERENCES PartieCorps(id_partie),
    UNIQUE (annee, id_naf5, id_partie)
);

CREATE TABLE SinistresRegion (
    id_sinistre       INTEGER PRIMARY KEY AUTOINCREMENT,
    annee             INTEGER NOT NULL,
    nb_salaries       INTEGER,
    nb_sinistres_int  INTEGER,
    id_region         INTEGER NOT NULL REFERENCES Region(id_region),
    id_risque         INTEGER NOT NULL REFERENCES Risque(id_risque),
    UNIQUE (annee, id_region, id_risque)
);

CREATE TABLE Depenses (
    id_depense        INTEGER PRIMARY KEY AUTOINCREMENT,
    annee             INTEGER NOT NULL,
    montant_depenses  INTEGER,
    poste_depenses    TEXT NOT NULL,
    id_risque         INTEGER NOT NULL REFERENCES Risque(id_risque),
    UNIQUE (annee, id_risque, poste_depenses)
);
