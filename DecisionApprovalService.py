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


class EvaluationDecisionService(ServiceBase):
    @rpc(DictionnaryItem, _returns=DictionnaryItem)
    def evaluationScore(ctx, LoanMap):
        try:
            logging.debug(f"Evaluating {LoanMap}")
            LoanMap.value = json.loads(LoanMap.value.replace("'", '"'))
        except json.JSONDecodeError as e:
            return DictionnaryItem(key="Erreur", value=f"Erreur de conversion : {e}")

        montant_pret = float(
            LoanMap.value["Montant du Prêt Demandé"].replace("EUR", "").strip()
        )
        duree = int(LoanMap.value["Durée du Prêt"].replace("ans", "").strip())
        revenu_mensuel = float(
            LoanMap.value["Revenu Mensuel"].replace("EUR", "").strip()
        )
        depense = float(LoanMap.value["Dépenses Mensuelles"].replace("EUR", "").strip())
        score = LoanMap.value["score"]
        properity_score = (
            LoanMap.value["score properity"] * duree * 12
            if "score properity" in LoanMap.value
            else 0
        )
        # Calculer le remboursement et le taux d'endettement
        taux_interet = 0.03
        remboursement = (montant_pret * taux_interet * (1 + taux_interet) ** duree) / (
            (1 + taux_interet) ** (duree - 1)
        )
        taux_endettement = (remboursement / revenu_mensuel) * 100

        # Évaluer la décision
        if (
            remboursement + depense < revenu_mensuel
            and score > 50
            and taux_endettement < 40
            and properity_score > montant_pret
        ):
            description = (
                "Vous correspondez à tous les critères. Nous acceptons votre crédit."
            )
            response = {"Réponse banque": True, "Description": description}
        else:
            description = "Nous ne pouvons pas accepter le crédit car "
            if remboursement + depense >= revenu_mensuel:
                description += "vos dépenses mensuelles sont trop élevées."
            if score <= 50:
                description += " Votre score de crédit est trop faible."
            if taux_endettement >= 40:
                description += " Le ratio de remboursement est trop risqué."
            if taux_endettement <= montant_pret:
                description += " la valeur de la propriété est inférieure au prêt demandé est trop risqué."
            response = {"Réponse banque": False, "Description": description}

        return DictionnaryItem(key="Réponse banque", value=json.dumps(response))


application = Application(
    [EvaluationDecisionService],
    tns="evaluation.decision.EvaluationDecisionService",
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

if __name__ == "__main__":
    wsgi_app = WsgiApplication(application)
    sys.exit(run_twisted([(wsgi_app, b"EvaluationDecisionService")], 8008))
