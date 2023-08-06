import os
from typing import Dict, Union

import fasttext
import wget
from kolibri.data.ressources import resources
from pathlib import Path

models = {"low_mem": None, "high_mem": None}
#FTLANG_CACHE = os.getenv("FTLANG_CACHE", "/tmp/fasttext-langdetect")

target_path=resources.get(str(Path('modules', 'language_detector', 'lid.176.bin'))).path

def download_model(name):
    url = f"https://dl.fbaipublicfiles.com/fasttext/supervised-models/{name}"
#    target_path = os.path.join(FTLANG_CACHE, name)
    if not os.path.exists(target_path):
        os.makedirs(target_path, exist_ok=True)
        wget.download(url=url, out=target_path)
    return target_path


def get_or_load_model(low_memory=False):
    if low_memory:
        model = models.get("low_mem", None)
        if not model:
            model_path = download_model("lid.176.ftz")
            model = fasttext.load_model(model_path)
            models["low_mem"] = model
        return model
    else:
        model = models.get("high_mem", None)
        if not model:
            model_path = download_model("lid.176.bin")
            model = fasttext.load_model(model_path)
            models["high_mem"] = model
        return model


def detect_language(text: str, low_memory=False) -> Dict[str, Union[str, float]]:
    model = get_or_load_model(low_memory)
    labels, scores = model.predict(text.replace('\r', '').replace('\n', ''))
    label = labels[0].replace("__label__", '')
    score = min(float(scores[0]), 1.0)
    return {
        "lang": label,
        "score": score,
    }

#print(detect_language("Bjr.pq dois je payer cette somme et que je viens de payer 195 eEnvoyé depuis mon appareil Galaxy\r\n-------- Message d'origine --------De : energie@octaplus.be Date : 2/03/22  00:57  (GMT+01:00) À : lucianadambros@outlook.be Objet : Votre facture d'énergie OCTA+ n° 17307802 du 02/03/22\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n                            Chère cliente, cher client,\r\n\r\nCi-joint, vous trouverez votre facture pour la fourniture de gaz et/ou d'électricité.\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n                                Payer € 29,65 rapidement et en toute sécurité via Bancontact >\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n                            Numéro de facture : 17307802\r\nMontant : € 29,65\r\nSur le compte : BE67 7350 4478 5187\r\nCommunication structurée : +++173/0780/20082+++\r\nDate d'échéance :  17/03/2022\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n                                Payer votre facture de € 29,65 en ligne >\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n                            Vous pouvez consulter et télécharger toutes vos factures via l'espace client sur notre site web : www.octaplus.be. Votre espace client peut être activé à l'aide de votre numéro de client et le code d'activation se trouvant sur vos factures. Si votre espace client a déjà été activé, vous pouvez vous identifier grâce à votre login et votre mot de passe existant.\r\n\r\nNous vous remercions d'ores et déjà pour votre confiance. Des questions? N'hésitez pas à nous contacter.\r\n\r\nÉnergiquement vôtre,\r\n\r\nL'équipe OCTA+"))