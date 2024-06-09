# conduct simulation specific analyses
import os
from pathlib import Path
import pandas as pd
import numpy as np

CURRENT_DIRECTORY = Path(__file__).parent
CURRENT_DIRECTORY = "C:/Users/sonne/Documents/Clark Scholars"

dfPositions = pd.read_csv(str(CURRENT_DIRECTORY)+"/SciVisContest23/viz-calcium/positions/rank_0_positions.txt", header=7, sep=' ')
dropColNames = list(dfPositions.columns[6:12])
dfPositions =  dfPositions.drop(dropColNames, axis=1)
dfPositions.columns = ['local id', 'pos x', 'pos y', 'pos z', 'area', 'type']

regionList = dfPositions['area'].unique().tolist()

def getAvgRegion(ts1, ts2, sim):
    # returns the average number of creations and deletions between two time steps
    directory = str(CURRENT_DIRECTORY) + "/SciVisContest23/viz-" + sim + "/network/changes/"
    resultCreated = pd.DataFrame({'area': regionList, 'avg': [0]*len(regionList)})
    resultDeleted = pd.DataFrame({'area': regionList, 'avg': [0]*len(regionList)})
    resultCreated.set_index('area', inplace=True)
    resultDeleted.set_index('area', inplace=True)
    for file in os.listdir(directory):
        if file.startswith("area_"): # regional data
            data = pd.read_csv(directory+file)
            data['total'] = data['in'] + data['out']
            regionName = file[:-12]
            if file.endswith('created.csv'):
                resultCreated.loc[regionName] = {'avg': data.iloc[ts1//10000:ts2//10000,-1].mean()}
            if file.endswith('deleted.csv'):
                resultDeleted.loc[regionName] = {'avg': data.iloc[ts1//10000:ts2//10000,-1].mean()}
    return (resultCreated, resultDeleted)

def getTimestepRegion(ts, sim):
    # returns the number of creations and deletions at one time step
    directory = str(CURRENT_DIRECTORY) + "/SciVisContest23/viz-" + sim + "/network/changes/"
    resultCreated = pd.DataFrame({'area': regionList, 'created': [0]*len(regionList)})
    resultDeleted = pd.DataFrame({'area': regionList, 'deleted': [0]*len(regionList)})
    resultCreated.set_index('area', inplace=True)
    resultDeleted.set_index('area', inplace=True)
    for file in os.listdir(directory):
        if file.startswith("area_"): # regional data
            data = pd.read_csv(directory+file)
            data['total'] = data['in'] + data['out']
            regionName = file[:-12]
            if file.endswith('created.csv'):
                resultCreated.loc[regionName] = {'created': data.iloc[ts//10000-1,-1]}
            if file.endswith('deleted.csv'):
                resultDeleted.loc[regionName] = {'deleted': data.iloc[ts//10000-1,-1]}
    return (resultCreated, resultDeleted)

def rankRegions(sim, critera = 'created'):
    # this just ranks regions based on magnitude of creation or deletion events
    # critera can be 'created' or 'deleted'
    resultCreated, resultDeleted = getAvgRegion(0, 990000, sim)
    if critera == 'created':
        return resultCreated.sort_values(by='avg', ascending=False).index
    else:
        return resultDeleted.sort_values(by='avg', ascending=False).index
    
def compareDisable(disableTS):
    # find large increases in deleted events
    createdBefore, deletedBefore = getAvgRegion(0, disableTS, sim='disable')
    createdAfter, deletedAfter = getAvgRegion(disableTS, 990000, sim='disable')
    created = pd.concat([createdBefore, createdAfter], axis=1)
    created.columns = ['before', 'after']
    created['change'] = created['after'] - created['before']
    created = created.sort_values(by='change', ascending=False)
    deleted = pd.concat([deletedBefore, deletedAfter], axis=1)
    deleted.columns = ['before', 'after']
    deleted['change'] = deleted['after'] - deleted['before']
    deleted = deleted.sort_values(by='change', ascending=False)
    return (created, deleted)

def rankDisable():
    # returns area list sorted based on most deletions
    created, deleted = compareDisable(disableTS=100000)
    return deleted.index

def compareStimulus(chunk = False, useBaseline = True, returnRankings = False):
    # find large increases in creations
    # stimTS = [150000, 152000,200000,202000,250000,252000, 300000,302000, 350000,352000,400000,402000, 
    #           450000,452000,500000,502000,550000,552000,652000,654000, 702000,704000,]
    stimTS = [150000, 200000,250000, 300000, 350000,400000, 450000,500000,550000,652000, 702000,]
    stimTS = [0] + stimTS + [990000]
    created = pd.DataFrame({'area': regionList}).set_index('area', inplace=True)
    deleted = pd.DataFrame({'area': regionList}).set_index('area', inplace=True)
    for i in range(1, len(stimTS)):
        if chunk:
            createdPeriod, deletedPeriod = getAvgRegion(stimTS[i-1], stimTS[i], sim='stimulus')
        else:
            createdPeriod, deletedPeriod = getTimestepRegion(stimTS[i], sim='stimulus')
        colName = i
        createdPeriod.columns = [colName]
        deletedPeriod.columns = [colName]
        created = pd.concat([created, createdPeriod], axis=1)
        deleted = pd.concat([deleted, deletedPeriod], axis=1)

        dfLen = len(created.columns)
        for iCol in range(dfLen):
            col = created.columns[iCol]
            if iCol == dfLen - 1:
                pass # this means it's the first column aka the baseline
            if useBaseline:
                created[col] = created[col] - created[created.columns[0]]
                deleted[col] = deleted[col] - deleted[deleted.columns[0]]
            else: # iterate from the back forward to avoid double subtration
                created[created.columns[dfLen - iCol - 1]] = created[created.columns[dfLen - iCol - 1]] - created[created.columns[dfLen - iCol - 2]]
                deleted[deleted.columns[dfLen - iCol - 1]] = deleted[deleted.columns[dfLen - iCol - 1]] - deleted[deleted.columns[dfLen - iCol - 2]]

        if returnRankings:
            # change absolute values to rankings
            for col in created.columns:
                created[col] = created[col].rank()
                deleted[col] = deleted[col].rank()
    return (created, deleted)

created, deleted = compareStimulus()