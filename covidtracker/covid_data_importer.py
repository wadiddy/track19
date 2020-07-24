from covidtracker import models
from covidtracker.connectors.ca_cases_connector import CaCasesConnector
from covidtracker.connectors.ca_hospitals_connector import CaHospitalsConnector
from covidtracker.connectors.us_states_connector import UsaConnector

CONNECTORS = [
    UsaConnector,
    CaCasesConnector,
    CaHospitalsConnector
]


def exec():
    for c in CONNECTORS:
        c().import_csv()
