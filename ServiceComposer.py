# Example for one service - similar structure should apply to other services.
import logging
import sys
from spyne import Application, rpc, ServiceBase, Unicode, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client


class DictionnaryItem(ComplexModel):
    key = Unicode
    value = Unicode


class LoanDemandService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def loanDemand(ctx, request):
        try:
            clientInfo = Client(
                "http://localhost:8000/ClientInformationExtractionService?wsdl"
            )
            clientSolvency = Client(
                "http://localhost:8002/SolvencyVerificationService?wsdl"
            )
            clientProperity = Client(
                "http://localhost:8009/ProperityVerificationService?wsdl"
            )
            clientDecision = Client(
                "http://localhost:8008/EvaluationDecisionService?wsdl"
            )

            response_info = clientInfo.service.extraire_informations(request)
            response_solvency = clientSolvency.service.solvencyVerif(response_info)
            response_properity = clientProperity.service.ProperityVerify(
                response_solvency
            )
            final_response = clientDecision.service.evaluationScore(response_properity)

            return final_response.value
        except Exception as e:
            logging.error(f"Error during service call: {str(e)}")
            return f"Erreur lors de l'appel au service : {str(e)}"


application = Application(
    [LoanDemandService],
    tns="sarra.brahem.loanDemandService",
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)

if __name__ == "__main__":
    wsgi_app = WsgiApplication(application)
    print(" composed service is running on port 8004")
    sys.exit(run_twisted([(wsgi_app, b"LoanDemandService")], 8004))
