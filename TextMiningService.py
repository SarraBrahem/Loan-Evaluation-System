import logging
import sys
import re
import json
from spyne import Application, rpc, ServiceBase, Unicode, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.DEBUG)


class DictionnaryItem(ComplexModel):
    __namespace__ = "information_extraction"
    key = Unicode
    value = Unicode


class ClientInformationExtractionService(ServiceBase):
    @rpc(Unicode, _returns=DictionnaryItem)
    def extraire_informations(ctx, texte):
        # Dictionnaire pour stocker les informations extraites
        informations = {}

        # Liste des clés à extraire
        keys = [
            "Adresse",
            "Email",
            "Numéro de Téléphone",
            "Montant du Prêt Demandé",
            "Durée du Prêt",
            "Description de la Propriété",
            "Revenu Mensuel",
            "Dépenses Mensuelles",
            "Nom du Client",
        ]

        # Utilisation d'expressions régulières pour extraire chaque information
        for key in keys:
            pattern = rf"{key}:\s*(.*?)\s*(?=\b(?:{'|'.join(keys)})|$)"
            match = re.search(pattern, texte, re.DOTALL)
            if match:
                informations[key] = match.group(1).strip()

        # Affichage pour débogage
        logging.debug("Informations extraites :", informations)

        # Retourne les informations en JSON
        informationObject = DictionnaryItem(
            key=key, value=json.dumps(informations, ensure_ascii=False)
        )
        logging.debug(f"Extracted information: {informationObject.value}")
        return informationObject


application = Application(
    [ClientInformationExtractionService],
    tns="spyne.examples.hello",
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

if __name__ == "__main__":
    wsgi_app = WsgiApplication(application)
    sys.exit(run_twisted([(wsgi_app, b"ClientInformationExtractionService")], 8000))
