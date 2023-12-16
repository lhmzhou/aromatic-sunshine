import pandas as pd
import requests
from decimal import Decimal
import json 
import os 
from datetime import date

def cleanup_charges(charges: pd.DataFrame, rename: bool, gross: str, cash: str, cpt: str) -> pd.DataFrame:
    """Standardize the cleaning into a normalized table of prices"""
    
    if rename:
        charges["gross"] = charges[gross]
        charges["cash"] = charges[cash]        
        charges["concept_code"] = charges[cpt].apply(lambda x: strip_zero(x.strip()))
        charges["vocabulary_id"] = "cpt"

    for column in ["gross", "cash"]:
        if charges[column].dtype != 'float64':
            charges[column] = charges[column].apply(lambda x: x.str.replace(",", "").str.replace("$", ""))
            charges[column] = pd.to_numeric(charges[column], errors='ignore', downcast='float')

    charges = charges[charges.vocabulary_id == "cpt"]
    charges = charges.merge(concept[["concept_code"]], on="concept_code")
    charges = charges.groupby(["vocabulary_id", "concept_code"])[["cash", "gross"]].max().reset_index()
    charges = pd.melt(charges, id_vars="concept_code", value_vars=["cash", "gross"])
    charges = charges.rename(columns={"concept_code": "cpt", "variable": "type", "value": "price"})
    charges = charges.drop_duplicates().dropna().round(2).sort_values(["cpt", "type"])

    return charges


def load_json(url: str) -> dict:
    """Requests the JSON data from the given URL and returns the parsed dictionary"""
    response = requests.get(url)
    
    if response.status_code == 200:
        charges = response.json()
    else:
        charges = {}
    
    return charges

def strip_zero(string: str) -> str:
    """Some unfortunate individuals pad their CPT codes with zeros"""
    if len(string) == 6 and string[0] == "0":
        return string[1:]
    else: 
        return string

dt = pd.read_csv("./csv/hospital.csv")
dt = dt[dt.can_automate == True]

concept = pd.read_csv("./csv/CONCEPT.csv.gz",compression='gzip',sep="\t")
concept = concept[(concept.vocabulary_id=='CPT4')]

status = []

def process_charges(row):
    try:
        if row["type"] == "CSV":
            with urllib.request.urlopen(row["file_url"]) as f:
                charges = pd.read_csv(f, skiprows=int(row["skiprow"]), dtype="object", keep_default_na=False)
        elif row["type"] == "JSON":
            os.system('curl ' + row["file_url"] + " | jq > tmp.json")
            with open("tmp.json", "r") as f:
                charges = json.load(f)
            if os.path.exists("tmp.json"):
                os.remove("tmp.json")
            charges = charges['data']
            del charges[0]
            code_type = [x[0]['code type'] for x in charges]
            code = [x[0]['code'] for x in charges]
            gross = [x[0]['gross charge'] for x in charges]
            cash = [x[0]['discounted cash price'] for x in charges]
            charges = pd.DataFrame(list(zip(code_type, code, gross, cash)))
            charges.columns = ['vocabulary_id', 'concept_code', 'gross', 'cash']
            charges = cleanup_charges(
                charges=charges,
                rename=False,
                gross="gross",
                cash="cash",
                cpt="cpt"
            )

        charges.to_json("./raw/" + str(row["hospital_npi"]) + ".jsonl", lines=True, orient="records")

        status.append({
            "date": str(date.today()),
            "hospital_npi": row["hospital_npi"],
            "status": "SUCCESS",
            "file_url": row["file_url"]
        })
    except Exception as e:
        print(e)
        status.append({
            "date": str(date.today()),
            "hospital_npi": row["hospital_npi"],
            "status": "FAILURE",
            "file_url": row["file_url"]
        })
        
for index, row in dt.iterrows():
    if row["idn"] == "Parkridge" or row["idn"] == "Mission Health" or row["idn"] == "Tennova Healthcare":
        charges = pd.read_csv(urllib.request.urlopen(row["file_url"]), skiprows=int(row["skiprow"]),
                              dtype="object", keep_default_na=False)
        charges = cleanup_charges(
            charges=charges,
            rename=True,
            gross=row["gross"],
            cash=row["cash"],
            cpt=row["cpt"]
        )
        charges.to_json("./raw/" + str(row["hospital_npi"]) + ".jsonl", lines=True, orient="records")
    elif row["idn"] == "Advent Health" or row["idn"] == "Memorial" or row["idn"] == 'Covenant Health':
        process_charges(row)


pd.DataFrame(status).sort_values(['hospital_npi']).to_csv("status_results.csv", index=False)