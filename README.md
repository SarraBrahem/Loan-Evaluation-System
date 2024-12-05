# Loan Evaluation System

**Description**  
Ce projet met en œuvre un système de services web composites pour l'évaluation automatisée des demandes de prêt immobilier. Construit sur une architecture orientée services (SOA), il intègre plusieurs services spécialisés pour analyser les données client, vérifier la solvabilité, évaluer les propriétés et prendre des décisions d'approbation des prêts.

## Fonctionnalités
- **Extraction des informations client** à partir de texte brut via des techniques de NLP.
- **Vérification de la solvabilité** grâce à des scores de crédit personnalisés.
- **Évaluation des propriétés immobilières** basée sur des données de marché et des vérifications légales.
- **Prise de décision** automatisée en fonction de critères de risque financiers.

## Architecture
- **Services SOA** :
  - `TextMiningService` : Extraction des informations client (adresse, montant demandé, revenu, etc.).
  - `SolvabilityVerificationService` : Analyse des données financières pour calculer un score de solvabilité.
  - `ProperityEvaluationService` : Évaluation de la valeur et de la conformité des propriétés.
  - `DecisionApprovalService` : Prise de décision finale basée sur les résultats des services précédents.
  - `ServiceComposer` : Coordination entre tous les services pour une évaluation complète.
- **Surveillance et Automatisation** :
  - `WatchdogService` : Surveillance des fichiers entrants pour lancer automatiquement le pipeline de traitement.

## Installation et Déploiement
1. Clonez le dépôt :
   https://github.com/SarraBrahem/Loan-Evaluation-System.git
   cd loan-evaluation-system
   
Configurez un environnement Python (3.x recommandé) :
python -m venv env
source env/bin/activate  # sous Windows : .\env\Scripts\activate
pip install -r requirements.txt

Lancez les services individuellement :
Exemple pour TextMiningService :
python TextMiningService.py

Lancez le compositeur de services :
python ServiceComposer.py

Activez la surveillance avec WatchdogService :
python WatchdogService.py

Tests
- Les tests unitaires et d'intégration sont disponibles dans le fichier test.py.
- Exemple d'exécution des tests :
python test.py

Contributions
Ce projet a été développé dans le cadre du Master 2 Datascale à l'Université de Versailles par :

Sarra Brahem
