from track19 import models, datamodeling_service
from track19.connectors.ca_cases_connector import CaCasesConnector
from track19.connectors.ca_hospitals_connector import CaHospitalsConnector
from track19.connectors.us_states_connector import UsaConnector
from track19.connectors.wisconsin_connector import WisconsinConnector

CONNECTORS = [
    UsaConnector,
    WisconsinConnector,
    CaCasesConnector,
    CaHospitalsConnector
]


def exec():
    datamodeling_service.init()
    for c in CONNECTORS:
        c().import_data()
