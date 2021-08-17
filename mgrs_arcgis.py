import warnings
warnings.filterwarnings('ignore')

import json, mgrs
import pandas as pd
import numpy as np
from arcgis.geometry import Polyline
from arcgis.features import Feature, FeatureSet, FeatureCollection


def calculateLineAttributes(df, i):
    m = mgrs.MGRS()
    
    min_date = df[df.DATE_TIME == min(df.DATE_TIME)]
    max_date = df[df.DATE_TIME == max(df.DATE_TIME)]
    attributes={}
    
    attributes["TRACK_TDDS_COMBO"] = i
    attributes["PERPETRATOR"] = None
    attributes["ATTACK_TYPE"] = None
    attributes["LAUNCH_SITE"] = None
    attributes["FLIGHT_TERMINATION_SITE"] = None
    attributes["TERMINATION_TYPE"] = None
    attributes["ASSESSED_TARGET"] = None
    attributes["ATTACK_SUCCESS"] = None
    attributes["COORDINATED_ATTACK"] = None
    attributes["UAS_MODEL"] = None
    attributes["MIDB_EQUIP_CODE"] = min_date['MIDB_EQUIP_CODE'].values[0]
    attributes["SOURCE"] = min_date['ID'].values[0]
    attributes["ORIGIN_POINT_X_DD"] = min_date['LON'].values[0]
    attributes["ORIGIN_POINT_Y_DD"] = min_date['LAT'].values[0]
    attributes["TERMINATION_POINT_X_DD"] = max_date['LON'].values[0]
    attributes["TERMINATION_POINT_Y_DD"]= max_date['LAT'].values[0]
    attributes["LAUNCH_DTE"] = min(df.DATE_TIME)
    attributes["TERMINATION_DTE"] = max(df.DATE_TIME)
    attributes["FLIGHT_DURATION_MIN"] = df.time_delta_before.sum()/60
    attributes["FLIGHT_DIST_KM"] = df.KM_after.sum()
    attributes["ORIGIN_MGRS"] = m.toMGRS(attributes["ORIGIN_POINT_Y_DD"],attributes["ORIGIN_POINT_X_DD"])
    attributes["TERMINATION_MGRS"] = m.toMGRS(attributes["TERMINATION_POINT_Y_DD"],attributes["TERMINATION_POINT_X_DD"])
    attributes["MIST_ALTITUDE"] = max(df.ALTITUDE)
    attributes["MIST_CENOT"] = max(df.CENOT)
    attributes["MIST_FREQ"] = max(df.FREQ)
    attributes["MIST_FREQ_ACCURACY"] = max(df.FREQ_ACCURACY)
    attributes["MIST_FREQ_UNITS"] = max(df.FREQ_UNITS)
    attributes["MIST_CENOT_NAME"] = max(df.CENOT_NAME)
    attributes["MIST_TDDS_TRK_NUM"] = max(df.TDDS_TRK_NUM)
    attributes["MIST_TDDS_SCN"] = max(df.TDDS_SCN)
    attributes["MIST_FILENAME"] = max(df.FILENAME)
    
    return attributes


def removeOutliers(df, threshold=10000):
    df_filter = df[(df.MPH_before <= threshold) | (df.MPH_after <= threshold)]
    
    return df_filter


def haversine(lat1, lon1, lat2, lon2, earth_radius=6371):
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    
    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2

    return earth_radius * 2 * np.arcsin(np.sqrt(a))


def calcBeforeAfter(df):
    df['time_delta_before'] = df.DATE_TIME - df.DATE_TIME.shift(1)
    df['time_delta_after'] = df.DATE_TIME.shift(-1) - df.DATE_TIME
    df.time_delta_before = df.time_delta_before.dt.total_seconds()
    df.time_delta_after = df.time_delta_after.dt.total_seconds()
    df['KM_before'] = haversine(df.LAT.shift(),df.LON.shift(),df.loc[1:,'LAT'],df.loc[1:,'LON'])
    df['KM_after'] = haversine(df.loc[1:,'LAT'],df.loc[1:,'LON'],df.LAT.shift(-1),df.LON.shift(-1))
    df['MPH_before'] = (df.KM_before/df.time_delta_before)*2237
    df['MPH_after'] = (df.KM_after/df.time_delta_after)*2237
    df.MPH_before.fillna(df.MPH_after,inplace=True)
    df.MPH_after.fillna(df.MPH_before,inplace=True)
    
    return df


def castDtypes(df):
    df.DATE_TIME = round(df.DATE_TIME/1000)
    df.DATE_TIME = pd.to_datetime(df.DATE_TIME,unit='s')
    
    return df


def pointToLineFeatureSet(df):
    features = []
    
    df['TRACK_TDDS_COMBO'] = df.TDDS_SCN.str.cat(df.TDDS_TRK_NUM,sep="_")
    df = castDtypes(df)
    
    for i in df.TRACK_TDDS_COMBO.unique():
        line1 = {
          "paths" : [[]],
          "spatialReference" : {"wkid" : 4326}
        }
        df_filter = df[df.TRACK_TDDS_COMBO == i]
        df_filter = calcBeforeAfter(df_filter)
        df_cleaned = removeOutliers(df_filter)
        
        LON_list = df_cleaned.LON.to_list()
        LAT_list = df_cleaned.LAT.to_list()

        for x, y in zip(LON_list,LAT_list):
            line1['paths'][0].append([x,y])
            
        polyline = Polyline(line1)        
        attributes = calculateLineAttributes(df_cleaned, i)
        feature = Feature(geometry=polyline, attributes=attributes)
        features.append(feature)
        
    fset = FeatureSet(features = features,
                      geometry_type="Polyline",
                      spatial_reference={'wkid': 4326})
        
        
    return fset


def buildDataFrame(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    temp_dict = {}
    for feature in data['features']:
        # LAT Y, LON X
        temp_dict[feature['id']] = {}
        temp_dict[feature['id']]['LON'] = feature['geometry']['coordinates'][0]
        temp_dict[feature['id']]['LAT'] = feature['geometry']['coordinates'][1]
        temp_dict[feature['id']]['ID'] = feature['properties']['ID']
        temp_dict[feature['id']]['SECLAB'] = feature['properties']['SECLAB']
        temp_dict[feature['id']]['FILENAME'] = feature['properties']['FILENAME']
        temp_dict[feature['id']]['CORREL_INDX'] = feature['properties']['CORREL_INDX']
        temp_dict[feature['id']]['TDDS_SCN'] = feature['properties']['TDDS_SCN']
        temp_dict[feature['id']]['TDDS_TRK_NUM'] = feature['properties']['TDDS_TRK_NUM']
        temp_dict[feature['id']]['TIBS_LBL'] = feature['properties']['TIBS_LBL']
        temp_dict[feature['id']]['TIBS_MSG_NUM'] = feature['properties']['TIBS_MSG_NUM']
        temp_dict[feature['id']]['TIBS_STATION_ADDR'] = feature['properties']['TIBS_STATION_ADDR']
        temp_dict[feature['id']]['TIBS_SUBNET'] = feature['properties']['TIBS_SUBNET']
        temp_dict[feature['id']]['USMTF_PRODUCER_DIGRAPH'] = feature['properties']['USMTF_PRODUCER_DIGRAPH']
        temp_dict[feature['id']]['USMTF_MSG_NUM'] = feature['properties']['USMTF_MSG_NUM']
        temp_dict[feature['id']]['USMTF_TRK_NUM'] = feature['properties']['USMTF_TRK_NUM']
        temp_dict[feature['id']]['CENOT'] = feature['properties']['CENOT']
        temp_dict[feature['id']]['ENTITY_NUM'] = feature['properties']['ENTITY_NUM']
        temp_dict[feature['id']]['ENTITY_ACTIVITY'] = feature['properties']['ENTITY_ACTIVITY']
        temp_dict[feature['id']]['ENTITY_TYP'] = feature['properties']['ENTITY_TYP']
        temp_dict[feature['id']]['ENVIR_ID'] = feature['properties']['ENVIR_ID']
        temp_dict[feature['id']]['OPER_NAME'] = feature['properties']['OPER_NAME']
        temp_dict[feature['id']]['ALTITUDE'] = feature['properties']['ALTITUDE']
        temp_dict[feature['id']]['ALTITUDE_UNITS'] = feature['properties']['ALTITUDE_UNITS']
        temp_dict[feature['id']]['COMMS_EXTERNAL_MODULAT'] = feature['properties']['COMMS_EXTERNAL_MODULAT']
        temp_dict[feature['id']]['FREQ'] = feature['properties']['FREQ']
        temp_dict[feature['id']]['FREQ_UNITS'] = feature['properties']['FREQ_UNITS']
        temp_dict[feature['id']]['FREQ_ACCURACY'] = feature['properties']['FREQ_ACCURACY']
        temp_dict[feature['id']]['ENTITY_UPD_NUM'] = feature['properties']['ENTITY_UPD_NUM']
        temp_dict[feature['id']]['ORIG_NODE'] = feature['properties']['ORIG_NODE']
        temp_dict[feature['id']]['ORIG_SUBNET'] = feature['properties']['ORIG_SUBNET']
        temp_dict[feature['id']]['PKG_NUM'] = feature['properties']['PKG_NUM']
        temp_dict[feature['id']]['XMIT_NODE'] = feature['properties']['XMIT_NODE']
        temp_dict[feature['id']]['XMIT_SUBNET'] = feature['properties']['XMIT_SUBNET']
        temp_dict[feature['id']]['MIDB_EQUIP_CODE'] = feature['properties']['MIDB_EQUIP_CODE']
        temp_dict[feature['id']]['TRIXS_PRODUCER_DIGRAPH'] = feature['properties']['TRIXS_PRODUCER_DIGRAPH']
        temp_dict[feature['id']]['TRIXS_MSG_NUM'] = feature['properties']['TRIXS_MSG_NUM']
        temp_dict[feature['id']]['TRIXS_SOI_NUM'] = feature['properties']['TRIXS_SOI_NUM']
        temp_dict[feature['id']]['ENTITY_SZ'] = feature['properties']['ENTITY_SZ']
        temp_dict[feature['id']]['DATE_TIME'] = feature['properties']['DATE_TIME']
        temp_dict[feature['id']]['XMIT_TIME'] = feature['properties']['XMIT_TIME']
        temp_dict[feature['id']]['INGEST_TIME'] = feature['properties']['INGEST_TIME']
        temp_dict[feature['id']]['FADE_RECEIVED_TIME'] = feature['properties']['FADE_RECEIVED_TIME']        
    temp_dict

    df = pd.DataFrame.from_dict(temp_dict, orient='index')
    
    return df


df = buildDataFrame('tdds_points.geojson')
fset = pointToLineFeatureSet(df)
fc = FeatureCollection.from_featureset(fset=fset)
fset.sdf

###
#from arcgis import GIS
#gis = GIS('https://dcgsmarinecorps.maps.arcgis.com/','dzietz_DCGSMARINECORPS','B@seball1')
#map1 = gis.map()
#map1.basemap = "dark-gray"
#map1.center = {  'spatialReference': {'wkid':  4326},
#                 'x': 29.9,
#                 'y': 28.8}
#map1.zoom = 5.0

#sym_poly_aoi = {
#  "type": "esriSFS",
#  "style": "esriSFSSolid",
#  "color": [0,0,0,0],
#    "outline": {
#     "type": "esriSLS",
#     "style": "esriSLSSolid",
#     "color": [0,255,0,255],
#     "width": 3}
#}
#map1.draw(fset, symbol = sym_poly_aoi)
#map1.add_layer(flayer)
#map1

#lat = 28.73781858
#lon = 29.83331736

#m = mgrs.MGRS()
#c = m.toMGRS(lon,lat)
#c

#d = m.toLatLon(c)
#d

#m_ll = mgrs.MGRS().toMGRS(lat,lon)