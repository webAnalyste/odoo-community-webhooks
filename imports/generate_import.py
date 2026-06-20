"""
Génère le fichier res_partner_import.csv pour Odoo
depuis les 3 exports CRM sources.

Usage : python3 generate_import.py
Output : res_partner_import.csv
"""

import csv
import os

# ── Chemins ──────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
SOURCES = {
    "customers": os.path.join(BASE, "sources", "franck-scandolera_export_customers_1781933237.csv"),
    "employees": os.path.join(BASE, "sources", "franck-scandolera_export_employees_1781933211.csv"),
    "prospects": os.path.join(BASE, "sources", "franck-scandolera_export_prospects_1781933797.csv"),
}
OUTPUT_SOC = os.path.join(BASE, "res_partner_1_societes.csv")
OUTPUT_CT  = os.path.join(BASE, "res_partner_2_contacts.csv")

# ── Colonnes CSV sociétés ───────────────────────────────────────────────────────
FIELDNAMES_SOC = [
    "id",
    "name",
    "is_company",
    "ref",
    "lang",
    "customer_rank",
    "supplier_rank",
    "country_id",
    "zip",
    "city",
    "street",
    "phone",
    "mobile",
    "email",
    "vat",
    "company_registry",
    "comment",
]

FIELDNAMES_SOC_EXTRA = [
    "id",
    "category_id/name",
    "title",
]

# ── Colonnes CSV contacts ────────────────────────────────────────────────────
FIELDNAMES_CT = [
    "id",
    "name",
    "is_company",
    "parent_id/id",
    "lang",
    "country_id",
    "zip",
    "city",
    "street",
    "phone",
    "mobile",
    "email",
    "user_id/email",
    "function",
    "title",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
PAYS_MAP = {
    "France": "France",
    "Belgique": "Belgique",
    "Belgium": "Belgique",
    "Suisse": "Suisse",
    "Switzerland": "Suisse",
    "Luxembourg": "Luxembourg",
    "Espagne": "Espagne",
    "Spain": "Espagne",
    "Allemagne": "Allemagne",
    "Germany": "Allemagne",
    "Italie": "Italie",
    "Italy": "Italie",
    "Royaume-Uni": "Royaume-Uni",
    "United Kingdom": "Royaume-Uni",
    "États-Unis": "États-Unis",
    "United States": "États-Unis",
    "Canada": "Canada",
    "Portugal": "Portugal",
    "Pays-Bas": "Pays-Bas",
    "Netherlands": "Pays-Bas",
    "Sénégal": "Sénégal",
    "Senegal": "Sénégal",
    "Maroc": "Maroc",
    "Morocco": "Maroc",
    "Algérie": "Algérie",
    "Algeria": "Algérie",
    "Tunisie": "Tunisie",
    "Tunisia": "Tunisie",
    "Côte d'Ivoire": "Côte d'Ivoire",
    "Cameroun": "Cameroun",
    "Cameroon": "Cameroun",
    "Martinique": "Martinique",
    "Guadeloupe": "Guadeloupe",
    "Réunion": "Réunion",
    "Polynésie française": "Polynésie française",
    "Nouvelle-Calédonie": "Nouvelle-Calédonie",
}

TITLE_MAP = {
    "M":           "Monsieur",
    "M.":          "Monsieur",
    "Mr":          "Monsieur",
    "Mr.":         "Monsieur",
    "Monsieur":    "Monsieur",
    "Mme":         "Madame",
    "Mme.":        "Madame",
    "Madame":      "Madame",
    "Mlle":        "Mademoiselle",
    "Mlle.":       "Mademoiselle",
    "Mademoiselle":"Mademoiselle",
    "Dr":          "Docteur",
    "Dr.":         "Docteur",
    "Docteur":     "Docteur",
    "Prof":        "Professeur",
    "Prof.":       "Professeur",
    "Professeur":  "Professeur",
    "Pr":          "Professeur",
}

LANG_MAP = {
    "fr-FR": "fr_FR",
    "en-US": "en_US",
    "en-GB": "en_GB",
    "de-DE": "de_DE",
    "es-ES": "es_ES",
    "it-IT": "it_IT",
}


def clean(val):
    v = (val or "").strip()
    v = v.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return v


def bool_to_int(val):
    """'Oui'/'Non' → 1/0"""
    return "1" if clean(val).lower() in ("oui", "yes", "true", "1") else "0"


def invert_bool(val):
    """'Non' → 1 (is_company), 'Oui' → 0 (particulier)"""
    return "0" if clean(val).lower() in ("oui", "yes", "true", "1") else "1"


def clean_vat(val):
    """Garde uniquement les TVA au format FR + 11 alphanum"""
    v = clean(val).upper().replace(" ", "").replace(".", "")
    if not v:
        return ""
    import re
    if re.match(r'^[A-Z]{2}[A-Z0-9]{2}[0-9]{9}$', v) or re.match(r'^[A-Z]{2}[0-9]{11}$', v):
        return v
    if re.match(r'^FR[A-Z0-9]{2}[0-9]{9}$', v):
        return v
    return ""


def map_pays(val):
    v = clean(val)
    return PAYS_MAP.get(v, v)


def map_title(val):
    v = clean(val)
    return TITLE_MAP.get(v, v)


def map_lang(val):
    v = clean(val)
    return LANG_MAP.get(v, v)


def clean_tags(val):
    """'annonceur|école|' → 'annonceur,école' (minuscules pour matcher Odoo)"""
    parts = [p.strip().lower() for p in clean(val).split("|") if p.strip()]
    return ",".join(parts)


def read_source(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        return list(reader)


# ── Traitement principal ──────────────────────────────────────────────────────
def process():
    seen_companies = {}   # id_societe → external_id société déjà écrite
    rows_soc = []
    rows_ct  = []

    for source_name, path in SOURCES.items():
        records = read_source(path)
        print(f"  [{source_name}] {len(records)} lignes lues")

        for rec in records:
            id_soc    = clean(rec.get("Id de la société", ""))
            nom_soc   = clean(rec.get("Société", ""))
            rue       = clean(rec.get("Rue", ""))
            ville     = clean(rec.get("Ville", ""))
            cp        = clean(rec.get("Code postal", ""))
            pays      = map_pays(rec.get("Pays", ""))
            tva       = clean(rec.get("TVA intracommunautaire", ""))
            siret     = clean(rec.get("Siret", ""))
            iban      = clean(rec.get("IBAN", ""))
            bic       = clean(rec.get("BIC", ""))
            langue    = map_lang(rec.get("Langue", ""))
            code_tiers = clean(rec.get("Code tiers", ""))
            is_client  = bool_to_int(rec.get("Statut Client", ""))
            is_vendor  = bool_to_int(rec.get("Statut Fournisseur", ""))
            comment    = clean(rec.get("Commentaires", ""))
            tags       = clean_tags(rec.get("Catégories", ""))
            commercial = clean(rec.get("Commercial responsable", ""))
            est_particulier = clean(rec.get("Est un particulier", ""))

            # ── Champs contact ────────────────────────────────────────────
            id_contact  = clean(rec.get("Id du contact", ""))
            prenom      = clean(rec.get("Prénom du contact", ""))
            nom         = clean(rec.get("Nom du contact", ""))
            email_ct    = clean(rec.get("Email du contact", ""))
            tel_fixe    = clean(rec.get("Téléphone fixe", ""))
            tel_mobile  = clean(rec.get("Téléphone portable", ""))
            civilite    = clean(rec.get("Civilité du contact", ""))
            poste       = clean(rec.get("Poste/Job du contact", ""))
            nom_complet = f"{prenom} {nom}".strip() if (prenom or nom) else ""

            is_particulier = clean(est_particulier).lower() in ("oui", "yes", "true", "1")

            # ── CAS 1 : Particulier → une seule ligne personne ────────────
            if is_particulier:
                nom_personne = nom_complet or nom_soc
                if id_soc and nom_personne and id_soc not in seen_companies:
                    seen_companies[id_soc] = f"soc_{id_soc}"
                    tags_individuel = "individuel" if not tags else tags + ",individuel"
                    rows_soc.append({
                        "id":                 f"soc_{id_soc}",
                        "name":               nom_personne,
                        "is_company":         "0",
                        "ref":                code_tiers,
                        "lang":               langue,
                        "customer_rank":      is_client,
                        "supplier_rank":      is_vendor,
                        "country_id":         pays,
                        "zip":                cp,
                        "city":               ville,
                        "street":             rue,
                        "phone":              tel_fixe,
                        "mobile":             tel_mobile,
                        "email":              email_ct,
                        "vat":                clean_vat(tva),
                        "company_registry":   "",
                        "comment":            comment,
                        "category_id/name":   tags_individuel,
                        "user_id/email":      commercial,
                        "function":           poste,
                        "title":              map_title(civilite),
                        "bank_ids/bank":      bic,
                        "bank_ids/acc_number": iban,
                    })
                # Pas de ligne contact séparée pour un particulier

            else:
                # ── CAS 2 : Société → ligne société + ligne contact ───────
                if id_soc and nom_soc and id_soc not in seen_companies:
                    ext_id_soc = f"soc_{id_soc}"
                    seen_companies[id_soc] = ext_id_soc

                    rows_soc.append({
                        "id":                 ext_id_soc,
                        "name":               nom_soc,
                        "is_company":         "1",
                        "ref":                code_tiers,
                        "lang":               langue,
                        "customer_rank":      is_client,
                        "supplier_rank":      is_vendor,
                        "country_id":         pays,
                        "zip":                cp,
                        "city":               ville,
                        "street":             rue,
                        "phone":              clean(rec.get("Téléphone fixe", "")),
                        "mobile":             clean(rec.get("Téléphone portable", "")),
                        "email":              "",
                        "vat":                clean_vat(tva),
                        "company_registry":   siret,
                        "comment":            comment,
                        "category_id/name":   tags,
                        "user_id/email":      commercial,
                        "function":           "",
                        "title":              "",
                        "bank_ids/bank":      bic,
                        "bank_ids/acc_number": iban,
                    })

                if id_contact and nom_complet:
                    rows_ct.append({
                        "id":                 f"ct_{id_contact}_{id_soc}",
                        "name":               nom_complet,
                        "is_company":         "0",
                        "parent_id/id":       f"__import__.soc_{id_soc}",
                        "lang":               langue,
                        "country_id":         pays,
                        "zip":                cp,
                        "city":               ville,
                        "street":             rue,
                        "phone":              tel_fixe,
                        "mobile":             tel_mobile,
                        "email":              email_ct,
                        "user_id/email":      commercial,
                        "function":           poste,
                        "title":              map_title(civilite),
                    })

    return rows_soc, rows_ct


# ── Écriture CSV ──────────────────────────────────────────────────────────────
def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


OUTPUT_SOC_EXTRA = os.path.join(BASE, "res_partner_1b_societes_extra.csv")

if __name__ == "__main__":
    print("Lecture des sources...")
    rows_soc, rows_ct = process()
    write_csv(OUTPUT_SOC,       rows_soc, FIELDNAMES_SOC)
    write_csv(OUTPUT_SOC_EXTRA, rows_soc, FIELDNAMES_SOC_EXTRA)
    write_csv(OUTPUT_CT,        rows_ct,  FIELDNAMES_CT)
    print(f"\n✅ Fichier 1  : {OUTPUT_SOC}  ({len(rows_soc)} lignes)")
    print(f"✅ Fichier 1b : {OUTPUT_SOC_EXTRA}  (tags/titre/vendeur, à importer après)")
    print(f"✅ Fichier 2  : {OUTPUT_CT}  ({len(rows_ct)} lignes)")
