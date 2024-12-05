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


class CreditDataBase:
    data_source = "db/credit.json"

    @classmethod
    def get_client_data(cls, client_name):
        with open(cls.data_source, "r") as file:
            data = json.load(file)
            return data.get(
                client_name,
                {"paiements_retard": 0, "montant_credit": 0, "faillite": False},
            )


class SolvencyVerificationService(ServiceBase):
    @staticmethod
    def scoring_credit(paiements_retard, montant_credit, faillite, revenu_mensuel):
        logging.debug("Calculating credit score")

        # Factor 1: Late payments
        score_paiements_retard = (
            100
            if paiements_retard == 0
            else 70
            if paiements_retard <= 2
            else 40
            if paiements_retard <= 5
            else 10
        )

        # Factor 2: Credit amount ratio
        ratio_endettement = montant_credit / revenu_mensuel if revenu_mensuel else 0
        score_credit = (
            100 if ratio_endettement < 0.2 else 70 if ratio_endettement < 0.5 else 40
        )

        # Factor 3: Bankruptcy
        score_faillite = 0 if faillite else 100

        # Weighted total score
        score_total = (
            score_paiements_retard * 0.40 + score_credit * 0.30 + score_faillite * 0.30
        )
        logging.debug(f"Credit score calculated: {score_total}")
        return score_total

    @rpc(DictionnaryItem, _returns=DictionnaryItem)
    def solvencyVerif(ctx, LoanMap):
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
        revenu_mensuel = LoanMap.value.get("Revenu Mensuel")
        if not revenu_mensuel:
            logging.error("Missing 'Revenu Mensuel'")
            return DictionnaryItem(key="Erreur", value="Revenu Mensuel manquant")

        name = LoanMap.value.get("Nom du Client")
        if not name:
            logging.error("Missing 'Nom du Client'")
            return DictionnaryItem(key="Erreur", value="Nom du Client manquant")

        logging.debug(f"Client name: {name}")
        revenu_mensuel = float(revenu_mensuel.replace("EUR", "").strip())
        data_client = CreditDataBase.get_client_data(name)

        logging.debug(f"Client data: {data_client}")

        # Calculating score
        score = SolvencyVerificationService.scoring_credit(
            data_client["paiements_retard"],
            data_client["montant_credit"],
            data_client["faillite"],
            revenu_mensuel,
        )
        LoanMap.value["score"] = score

        logging.debug(f"Final score: {score}")
        return DictionnaryItem(key="Calcul de Score", value=json.dumps(LoanMap.value))


application = Application(
    [SolvencyVerificationService],
    tns="solvency.verification.SolvencyVerificationService",
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

if __name__ == "__main__":
    wsgi_app = WsgiApplication(application)
    sys.exit(run_twisted([(wsgi_app, b"SolvencyVerificationService")], 8002))
