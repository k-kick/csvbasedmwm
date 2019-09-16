# -*- coding: utf-8 -*-
import configparser
import csv
import copy
import re
from pathlib import Path
from pydicom import dcmread
from pydicom.dataset import Dataset
from pynetdicom import AE, evt
from pynetdicom.sop_class import ModalityWorklistInformationFind
from pynetdicom.sop_class import VerificationSOPClass
from logger import logger

# config
configPath = Path(Path(__file__).parent.resolve(), "settings.conf")
config = configparser.RawConfigParser()
config.read(configPath, "utf-8")
address = config.get("server", "address")
port = int(config.get("server", "port"))
calledAet = config.get("general", "calledAET")
csvPath = config.get("general", "csvPath")
p = Path(csvPath)
if not p.is_absolute():
    csvPath = Path(Path(__file__).parent.resolve(), csvPath)
ignoreCsvHeader = False if "0" == config.get("general", "ignoreCsvHeader") else True

# log
logPath = config.get("logging", "logPath")
rotateWen = config.get("logging", "rotateWen")
rotateCount = int(config.get("logging", "rotateCount"))
log = logger("csvbasedmwm", logPath, rotateWen, rotateCount)

# C_ECHO event handler
def handleCEcho(event):
    log.info("Handle a C-ECHO request event.")

# C_FIND event handler
def handleFind(event):
    log.info("Handle a C-FIND request event.")
    log.info("======================= REQUEST =======================")
    ds = event.identifier
    log.info("\n" + str(ds))
    storedDs = []

    with open(csvPath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        if ignoreCsvHeader: next(reader)
        for row in reader:
            tmpDs = copy.deepcopy(ds)
            tmpDs.AccessionNumber = row[0]
            tmpDs.PatientID = row[1]
            tmpDs.PatientName = row[2]
            tmpDs.StudyDate = row[3]
            tmpDs.StudyTime = row[4]
            tmpDs.Modality = row[5]
            storedDs.append(tmpDs)

    matching = []
    pattern = ""
    if "PatientID" in ds and ds.PatientID:
        # Convert wildcard to regex pattern
        pattern = re.sub(r"\*", ".*", ds.PatientID)
        pattern = re.sub(r"\?", ".", pattern)
        pattern = r"^%s$" % pattern

    if pattern:
        repattern = re.compile(pattern)
        matching = [ inst for inst in storedDs if repattern.match(inst.PatientID) ]

    log.info("======================= RESPONSE =======================")
    for inst in matching:
        log.info("\n" + str(inst))
        yield (0xFF00, inst)

handlers = [
    (evt.EVT_C_FIND, handleFind),
    (evt.EVT_C_ECHO, handleCEcho)]

# Initialise the Application Entity and specify the listen port
ae = AE(ae_title=calledAet.encode())

# Add the supported presentation context
ae.add_supported_context(VerificationSOPClass)
ae.add_supported_context(ModalityWorklistInformationFind)

# Start listening for incoming association requests
ae.start_server((address, port), evt_handlers=handlers)
