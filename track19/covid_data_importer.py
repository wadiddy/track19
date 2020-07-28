from track19 import models
from track19.connectors.ca_cases_connector import CaCasesConnector
from track19.connectors.ca_hospitals_connector import CaHospitalsConnector
from track19.connectors.us_states_connector import UsaConnector

CONNECTORS = [
    UsaConnector,
    CaCasesConnector,
    CaHospitalsConnector
]


def exec():
    for c in CONNECTORS:
        c().import_csv()
