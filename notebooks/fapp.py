import datetime
from peewee import *
import pandas as pd
from tqdm import tqdm
import numpy as np
import fingerprint_handler
import json
print('hh')
db = SqliteDatabase("../data/database.db", pragmas=[('journal_mode', 'wal')])

class ClassifyEntity(Model):
    smiles = TextField(unique=True, index=True)
    classification_json = TextField()

    class Meta:
        database = db

#Creating the Tables
db.create_tables([ClassifyEntity], safe=True)

def classify_structure(smiles):
    isglycoside = fingerprint_handler._isglycoside(smiles)

    fp = fingerprint_handler.calculate_fingerprint(smiles, 2)

    fp1 = fp[0].tolist()[0]
    fp2 = fp[1].tolist()[0]

    query_dict = {}
    query_dict["input_2048"] = fp1
    query_dict["input_4096"] = fp2

    # Handling SUPERCLASS
    fp_pred_url = "http://npclassifier-tf-server:8501/v1/models/SUPERCLASS:predict"
    payload = json.dumps({"instances": [ query_dict ]})

    headers = {"content-type": "application/json"}
    json_response = requests.post(fp_pred_url, data=payload, headers=headers)

    pred_super = np.asarray(json.loads(json_response.text)['predictions'])[0]
    n_super = list(np.where(pred_super>=0.3)[0])

    path_from_superclass = []
    for j in n_super:
        path_from_superclass += ontology_dictionary['Super_hierarchy'][str(j)]['Pathway']
    path_from_superclass = list(set(path_from_superclass))

    query_dict = {}
    query_dict["input_2048"] = fp1
    query_dict["input_4096"] = fp2

    # Handling CLASS
    fp_pred_url = "http://npclassifier-tf-server:8501/v1/models/CLASS:predict"
    payload = json.dumps({"instances": [ query_dict ]})

    headers = {"content-type": "application/json"}
    json_response = requests.post(fp_pred_url, data=payload, headers=headers)

    pred_class = np.asarray(json.loads(json_response.text)['predictions'])[0]
    n_class = list(np.where(pred_class>=0.1)[0])

    path_from_class = []
    for j in n_class:
        path_from_class += ontology_dictionary['Class_hierarchy'][str(j)]['Pathway']
    path_from_class = list(set(path_from_class))

    query_dict = {}
    query_dict["input_2048"] = fp1
    query_dict["input_4096"] = fp2

    # Handling PATHWAY
    fp_pred_url = "http://npclassifier-tf-server:8501/v1/models/PATHWAY:predict"
    payload = json.dumps({"instances": [ query_dict ]})

    headers = {"content-type": "application/json"}
    json_response = requests.post(fp_pred_url, data=payload, headers=headers)

    pred_path = np.asarray(json.loads(json_response.text)['predictions'])[0]
    n_path = list(np.where(pred_path>=0.5)[0])

    class_result = []
    superclass_result = []
    pathway_result = []

    # Voting on Answer
    pathway_result, superclass_result, class_result, isglycoside = prediction_voting.vote_classification(n_path,
                                                                                                        n_class,
                                                                                                        n_super,
                                                                                                        pred_class,
                                                                                                        pred_super,
                                                                                                        path_from_class,
                                                                                                        path_from_superclass,
                                                                                                        isglycoside,
                                                                                                        ontology_dictionary)

    return isglycoside, class_result, superclass_result, pathway_result, path_from_class, path_from_superclass, n_path, fp1, fp2


def _process_full_classification(smiles_string):
    try:
        db_record = ClassifyEntity.get(ClassifyEntity.smiles == smiles_string)
        return json.loads(db_record.classification_json)
    except:
        pass

    isglycoside, class_results, superclass_results, pathway_results, path_from_class, path_from_superclass, n_path, fp1, fp2 = classify_structure(smiles_string)

    respond_dict = {}
    respond_dict["class_results"] = class_results
    respond_dict["superclass_results"] = superclass_results
    respond_dict["pathway_results"] = pathway_results
    respond_dict["isglycoside"] = isglycoside

    respond_dict["fp1"] = fp1
    respond_dict["fp2"] = fp2

    # Lets save the result here, we should also check if its changed, and if so, we overwrite
    try:
        # Save it out
        ClassifyEntity.create(
                smiles=smiles_string,
                classification_json=json.dumps(respond_dict)
            )
    except:
        pass

    return respond_dict