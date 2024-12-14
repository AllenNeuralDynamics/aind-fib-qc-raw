#%% Import
import csv
import glob
import json
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
from datetime import datetime, timezone
from aind_data_schema_models.modalities import Modality
from aind_data_schema.core.quality_control import QCEvaluation, QualityControl, QCMetric, Stage, Status, QCStatus
import boto3
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import argparse 
from pathlib import Path
import logging
from aind_log_utils.log import setup_logging

parser = argparse.ArgumentParser(description="Raw fiber QC")

data_folder = Path("../data")
results_folder = Path("../results")

#parser.add_argument("--asset-name", type=str, default = 'behavior_746346_2024-12-12_12-41-44')

# Parse the command-line arguments
#args = parser.parse_args()
#asset_name = args.asset_name

#if not results_folder.is_dir():
#    results_folder.mkdir(parents=True)

#if asset_name is not None and asset_name == "":
#    asset_name = None

#if asset_name is not None:
#    sessionfolder = str(data_folder / asset_name)

sessionfolder = '/root/capsule/data/behavior_746346_2024-12-12_12-41-44'

sessionname = sessionfolder.split('behavior_')[1]
fibfolder = sessionfolder + '/fib'

mouse_id = sessionname.split('_')[0]

setup_logging("aind-fiber-raw-qc", mouse_id=mouse_id, session_name = sessionname)

#%%
t = datetime.now(timezone.utc)

# Build some status objects
s = QCStatus(evaluator="Automated", status=Status.PASS, timestamp=t.isoformat())

#need to skip the entire QC if FIP files don't exist

file1  = glob.glob(fibfolder + os.sep + "FIP_DataG*")[0]
file2 = glob.glob(fibfolder + os.sep + "FIP_DataIso_*")[0]
file3 = glob.glob(fibfolder + os.sep + "FIP_DataR_*")[0]

with open(file1) as f:
    reader = csv.reader(f)
    datatemp = np.array([row for row in reader])
    data1 = datatemp[:,:].astype(np.float32)
    #del datatemp
    
with open(file2) as f:
    reader = csv.reader(f)
    datatemp = np.array([row for row in reader])
    data2 = datatemp[:,:].astype(np.float32)
    #del datatemp
    
with open(file3) as f:
    reader = csv.reader(f)
    datatemp = np.array([row for row in reader])
    data3 = datatemp[:,:].astype(np.float32)
    #del datatemp


#%% read behavior json file
behavior_json_path = sessionfolder + '/behavior/behavior_' + sessionname + '.json'

with open(behavior_json_path, 'r', encoding='utf-8') as f:
    behavior_json = json.load(f)

RisingTime=behavior_json['B_PhotometryRisingTimeHarp']
FallingTime=behavior_json['B_PhotometryFallingTimeHarp']


#%%raw data
%matplotlib inline
plt.figure()
plt.subplot(2,4,1)
plt.plot(data1[:,1])
plt.subplot(2,4,2)
plt.plot(data1[:,2])
plt.subplot(2,4,3)
plt.plot(data1[:,3])
plt.subplot(2,4,4)
plt.plot(data1[:,4])

plt.subplot(2,4,5)
plt.plot(data2[:,1])
plt.subplot(2,4,6)
plt.plot(data2[:,2])
plt.subplot(2,4,7)
plt.plot(data2[:,3])
plt.subplot(2,4,8)
plt.plot(data2[:,4])
plt.show
plt.savefig(str(results_folder) + '/raw_traces.png')
plt.savefig('/root/capsule/results/raw_traces.png')
#%%
#sensor floor
plt.figure()
plt.subplot(1,3,1)
plt.hist(data1[:,5])
plt.subplot(1,3,2)
plt.hist(data1[:,5])
plt.subplot(1,3,3)
plt.hist(data1[:,5])
plt.show()


#%%
Metrics = dict()

if len(data1) == len(data2) and len(data2) == len(data3):
    Metrics["IsDataSizeSame"] = True
else:
    Metrics["IsDataSizeSame"] = False
    logging.info("DataSizes are not the same")

if len(data1) > 18000:
    Metrics["IsDataLongerThan15min"] = True
else:
    Metrics["IsDataLongerThan15min"] = False
    logging.info("The session is shorter than 15min")

if len(RisingTime) == len(FallingTime):
    Metrics["IsSyncPulseSame"] = True
else:
    Metrics["IsSyncPulseSame"] = False
    logging.info("# of Rising and Falling sync pulses are not the same")

if np.isnan(data1).any():
    Metrics["NoGreenNan"] = False
    logging.info("Green Ch has NaN")
else:
    Metrics["NoGreenNan"] = True

if np.isnan(data2).any():
    Metrics["NoIsoNan"] = False
    logging.info("Green Ch has NaN")
else:
    Metrics["NoIsoNan"] = True

if np.isnan(data1).any():
    Metrics["NoGreenNan"] = False
    logging.info("Green Ch has NaN")
else:
    Metrics["NoGreenNan"] = True

eval0 = QCEvaluation(
    name="Data length check",
    modality=Modality.FIB,
    stage=Stage.RAW,
    metrics=[
        QCMetric(name="Data length same", value=Metrics["IsDataSizeSame"], status_history=[s]),
        QCMetric(name="Session length >15min", value=Metrics["IsDataLongerThan15min"], status_history=[s])
    ],
    notes="Pass when GreenCh_data_length==IsoCh_data_length and GreenCh_data_length==RedCh_data_length, and the session is >15min",
)

qc = QualityControl(evaluations=[eval0])
qc.write_standard_file(output_directory="/results")
# %%
