import sys
import json
import logging

from spyne import rpc, ServiceBase, Unicode, ComplexModel, Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.DEBUG)


class DictionnaryItem(ComplexModel):
    __namespace__ = "information_extraction"
    key = Unicode
    value = Unicode


class PropeirtyDataBase:
    data_source = "db/properity.json"

    @classmethod
    def get_properity_data(cls, prop_desc):
        with open(cls.data_source, "r") as file:
            data = json.load(file)
            return {des: data.get(des, 0) for des in prop_desc}


class ProperityVerificationService(ServiceBase):
    @staticmethod
    def scoring_properity(desc_score):
        logging.debug("Calculating Properity score")
        score_total = 0
        for value in desc_score.values():
            if value:
                score_total += value
        # Factor 1: Late payments

        logging.debug(f"Properity score calculated: {score_total}")
        return score_total

    @rpc(DictionnaryItem, _returns=DictionnaryItem)
    def ProperityVerify(ctx, LoanMap):
        logging.debug(f"Raw LoanMap received: {LoanMap.value}")

        # JSON parsing with error handling
        try:
            LoanMap.value = json.loads(LoanMap.value.replace("'", '"'))
        except json.JSONDecodeError as e:
            logging.error(f"JSON conversion error: {e}")
            return DictionnaryItem(
                key="Erreur", value=f"Erreur de conversion JSON : {e}"
            )

        # Fetching and validating required data
        properity_description = LoanMap.value.get("Description de la Propriété")
        if not properity_description:
            logging.error("Missing 'Description de la Propriété'")
            return DictionnaryItem(
                key="Erreur", value="Description de la Propriété manquant"
            )

        name = LoanMap.value.get("Nom du Client")
        if not name:
            logging.error("Missing 'Nom du Client'")
            return DictionnaryItem(key="Erreur", value="Nom du Client manquant")

        logging.debug(f"Client name: {name}")
        properity_description = [
            t.strip().replace(",", "").replace(".", "")
            for t in properity_description.lower().split(" ")
        ]
        properity_data = PropeirtyDataBase.get_properity_data(properity_description)

        logging.debug(f"Properity data: {properity_data}")

        # Calculating score
        score = ProperityVerificationService.scoring_properity(properity_data)
        LoanMap.value["score properity"] = score

        logging.debug(f"Final score: {score}")
        return DictionnaryItem(
            key="Calcul de Score Properity", value=json.dumps(LoanMap.value)
        )


application = Application(
    [ProperityVerificationService],
    tns="Properity.verification.ProperityVerificationService",
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

if __name__ == "__main__":
    wsgi_app = WsgiApplication(application)
    sys.exit(run_twisted([(wsgi_app, b"ProperityVerificationService")], 8009))
