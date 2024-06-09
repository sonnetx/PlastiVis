# preprocess data to show constant connections
from pathlib import Path
import pandas as pd
import numpy as np
import os
import json
import gzip

CURRENT_DIRECTORY = Path(__file__).parent
CURRENT_DIRECTORY = "T:\Plastivis Project\SciVisContest23"

# Todo: need _regionSummary.parquet
# def getParallelCoords(sims, timestep):
#     metrics = ['elecActivity', 'calcium', 'synapticInput', 'grownAxons', 'conDendrites', 'grownDendrites', 'conAxons']
#     # build target df
#     simsDict = {}
#     for sim in sims:
#         monitors = pd.DataFrame(index=dfPositions['area'].unique())
#         for m in metrics:
#             data = pd.read_csv(str(CURRENT_DIRECTORY)+"/SciVisContest23/viz-" + sim + "/monitors/byRegion/" + m + ".csv").set_index('10001').iloc[:,timestep//100].to_frame()
#             data.columns = [m]
#             monitors = pd.concat([monitors, data], axis=1, ignore_index=False)
#         directory = str(CURRENT_DIRECTORY) + "/SciVisContest23/viz-" + sim + "/network/constant"
#         connections = pd.read_parquet(directory + "/step_" + str(round(timestep, -4)) + "_regionSummary.parquet").set_index('area')
#         innerdf = pd.concat([monitors, connections], axis=1)
#         # innerdf['sim'] = sim
#         simsDict[sim] = innerdf
#     return simsDict

# sims = ['calcium', 'stimulus', 'no-network', 'disable']

def savegzip(data,filename):
    json_str = json.dumps(data) + "\n"               # 2. string (i.e. JSON)
    json_bytes = json_str.encode('utf-8')            # 3. bytes (i.e. UTF-8)

    with gzip.open(filename, 'w') as fout:       # 4. fewer bytes (i.e. gzip)
        fout.write(json_bytes)                      

# =========================  

for sim in sims:
    createdIngoingConnectionsDFDict = []
    createdOutgoingConnectionsDFDict = []
    deletedIngoingConnectionsDFDict = []
    deletedOutgoingConnectionsDFDict = []

 

    for timestep in range(10000,1000000,10000):
        deletedIngoingConnectionsDFDict.append( json.loads(pd.read_parquet(str(CURRENT_DIRECTORY)+"/SciVisContest23/viz-" + sim + "/network/constant/step_" + str(timestep) + "_in_constant.parquet").to_json(orient="values")))
        deletedOutgoingConnectionsDFDict.append( json.loads(pd.read_parquet(str(CURRENT_DIRECTORY)+"/SciVisContest23/viz-" + sim + "/network/constant/step_" + str(timestep) + "_out_constant.parquet").to_json(orient="values")))
    savegzip([deletedIngoingConnectionsDFDict,deletedOutgoingConnectionsDFDict],str(CURRENT_DIRECTORY) + "/SciVisContest23/regionData/"+sim+"_connectionList.json")

# Todo: need _regionSummary.parquet
# for timestep in range(10000,1000000,10000):
#     savegzip(getParallelCoords(sims, timestep),str(CURRENT_DIRECTORY) + "/SciVisContest23/regionData/PC_"+timestep+".json")

# Todo: the others file in public