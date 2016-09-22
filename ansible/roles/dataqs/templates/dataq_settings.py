# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Django settings for the GeoNode project.
from celery.schedules import crontab

# Append these to INSTALLED_APPS
DATAQS_APPS = (
    'dataqs',
    'dataqs.aqicn',
    'dataqs.airnow',
    'dataqs.forecastio',
    'dataqs.gdacs',
    'dataqs.gfms',
    'dataqs.nasa_gpm',
    'dataqs.spei',
    'dataqs.usgs_quakes',
    'dataqs.wqp',
    'dataqs.hifld',
    'dataqs.gistemp',
)

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT = 'redis'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://'
CELERY_ALWAYS_EAGER = False
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERYD_POOL_RESTARTS = True
CELERY_ENABLE_REMOTE_CONTROL = True

# AirNow API username:password
# (sign up for a free account at http://airnowapi.org/account/request/)
AIRNOW_ACCOUNT = 'your_airnow_username:your_airnow_password'

# NASA GPM FTP ACCOUNT
# (sign up at http://registration.pps.eosdis.nasa.gov/registration/)
GPM_ACCOUNT = 'your_gpm_email_account'

# Location of GeoServer data directory
GS_DATA_DIR = '/var/lib/tomcat7/webapps/geoserver/data'

# Directory where temporary data_queues geoprocessing files should
# be downloaded
GS_TMP_DIR = '/tmp'

# Time to wait before updating Geoserver mosaic (keep at 0 unless Geoserver
# is on a different server.
# In that case, there will need to be an automated rsync between GS_TMP_DIR
# where celery is running and
# GS_DATA_DIR where GeoServer is running.
RSYNC_WAIT_TIME = 0

# Add more scheduled geoprocessors here (ideally in local_settings.py file)
CELERYBEAT_SCHEDULE = {
    'gfms': {
        'task': 'dataqs.gfms.tasks.gfms_task',
        'schedule': crontab(minute=3),
        'args': ()
    },
    'forecast_io': {
        'task': 'dataqs.forecastio.tasks.forecast_io_task',
        'schedule': crontab(minute=1),
        'args': ()
    },
    'aqicn': {
        'task': 'dataqs.aqicn.tasks.aqicn_task',
        'schedule': crontab(hour=5, minute=0),
        'args': ()
    },
    'gdacs': {
        'task': 'dataqs.gdacs.tasks.gdacs_task',
        'schedule': crontab(hour=1, minute=0),
        'args': ()
    },
    'usgs_quakes': {
        'task': 'dataqs.usgs_quakes.tasks.usgs_quake_task',
        'schedule': crontab(hour=3,  minute=0),
        'args': ()
    },
    'spei': {
        'task': 'dataqs.spei.tasks.spei_task',
        'schedule': crontab(hour=4, minute=0),
        'args': ()
    },
    'wqp': {
        'task': 'dataqs.wqp.tasks.wqp_task',
        'schedule': crontab(hour=2, minute=0),
        'args': ()
    },
    'airnow': {
        'task': 'dataqs.gfms.tasks.airnow_task',
        'schedule': crontab(hour=6, minute=0),
        'args': ()
    },
    'nasa_gpm': {
        'task': 'dataqs.nasa_gpm.tasks.nasa_gpm_task',
        'schedule': crontab(hour=7, minute=0),
        'args': ()
    },
    'hifld': {
        'task': 'dataqs.hifld.tasks.hifld_task',
        'schedule': crontab(day_of_week='sunday', hour=12, minute=0),
        'args': ()
    },
    'gistemp': {
        'task': 'dataqs.gistemp.tasks.gistemp_task',
        'schedule': crontab(day_of_month=15, hour=12, minute=0),
        'args': ()
    }
}

HIFLD_LAYERS = [
    {
        'name': 'US State Boundaries',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/718791120f6549708cb642dac6ff0dbf_0.geojson',
        'table': 'us_state_boundaries',
        'sld': 'polygon',
        'description': 'This dataset represents States and equivalent entities, which are the primary governmental divisions of the United States. The TIGER/Line shapefiles and related database files (.dbf) are an extract of selected geographic and cartographic information from the U.S. Census Bureau\'s Master Address File / Topologically Integrated Geographic Encoding and Referencing (MAF/TIGER) Database (MTDB). The MTDB represents a seamless national file with no overlaps or gaps between parts, however, each TIGER/Line shapefile is designed to stand alone as an independent data set, or they can be combined to cover the entire nation. In addition to the fifty States, the Census Bureau treats the District of Columbia, Puerto Rico, and each of the Island Areas (American Samoa, the Commonwealth of the Northern Mariana Islands, Guam, and the U.S. Virgin Islands) as the statistical equivalents of States for the purpose of data presentation.  \n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/718791120f6549708cb642dac6ff0dbf_0'
    },
    {
        'name': 'US County Boundaries',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/53270fe7036f428fbfb11c4511994a6f_0.geojson',
        'table': 'us_county_boundaries',
        'sld': 'polygon',
        'description': 'This dataset represents a seamless national county file with no overlaps or gaps between parts, however, each TIGER/Line shapefile is designed to stand alone as an independent data set, or they can be combined to cover the entire nation. The primary legal divisions of most states are termed counties. In Louisiana, these divisions are known as parishes. In Alaska, which has no counties, the equivalent entities are the organized boroughs, city and boroughs, municipalities, and for the unorganized area, census areas. The latter are delineated cooperatively for statistical purposes by the State of Alaska and the Census Bureau. In four states (Maryland, Missouri, Nevada, and Virginia), there are one or more incorporated places that are independent of any county organization and thus constitute primary divisions of their states. These incorporated places are known as independent cities and are treated as equivalent entities for purposes of data presentation. The District of Columbia and Guam have no primary divisions, and each area is considered an equivalent entity for purposes of data presentation. The Census Bureau treats the following entities as equivalents of counties for purposes of data presentation: Municipios in Puerto Rico, Districts and Islands in American Samoa, Municipalities in the Commonwealth of the Northern Mariana Islands, and Islands in the U.S. Virgin Islands. The entire area of the United States, Puerto Rico, and the Island Areas is covered by counties or equivalent entities. The boundaries for counties and equivalent entities are mostly as of January 1, 2013, primarily as reported through the Census Bureau\'s Boundary and Annexation Survey (BAS). However, some changes made after January 2013, including the addition and deletion of counties, are included. \n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/53270fe7036f428fbfb11c4511994a6f_0'
    },
    {
        'name': 'US Urban Areas',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/12076211b9f047aca1153cb079bbd923_0.geojson',
        'table': 'us_urban_areas',
        'sld': 'polygon',
        'description': 'This dataset represents urban areas that represent densely developed territory, encompassing residential, commercial, and other nonresidential urban land uses. In general, this territory consists of areas of high population density and urban land use resulting in a representation of the "urban footprint." There are two types of urban areas: urbanized areas (UAs) that contain 50,000 or more people and urban clusters (UCs) that contain at least 2,500 people, but fewer than 50,000 people (except in the U.S. Virgin Islands and Guam which each contain urban clusters with populations greater than 50,000). Each urban area is identified by a 5-character numeric census code that may contain leading zeroes.  \n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/12076211b9f047aca1153cb079bbd923_0'
    },
    {
        'name': 'Poultry Slaughtering and Processing Facilities ',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/b6b9cc72fb58476d92056d5c7ed25f8b_0.geojson',
        'table': 'poultry_facilities',
        'sld': 'point',
        'description': 'This dataset represents facilities which engage in slaughtering, processing, and/or warehousing for the purpose of producing poultry and egg products. Facilities where poultry is raised or where eggs are laid are not included in this dataset, as they are included in a separate layer. \n\nThe source data used for this data layer does not include any facilities in American Samoa, the US Virgin Islands, or Wyoming. Records with "-DOD" appended to the end of the [NAME] value are located on a military base, as defined by the Defense Installation Spatial Data Infrastructure (DISDI) military installations and military range boundaries. \n\nAt the request of NGA, text fields in this dataset have been set to all upper case to facilitate consistent database engine search results. At the request of NGA, all diacritics (e.g., the German umlaut or the Spanish tilde) have been replaced with their closest equivalent English character to facilitate use with database systems that may not support diacritics. The currentness of this dataset is indicated by the [CONTDATE] field. Based upon this field, the oldest record dates from 01/22/09 and the newest record dates from 07/10/09. \n\nThe following use cases describe how the data may be used and help to define and clarify requirements.\n\n1) A threat against agricultural facilities has been identified and protective measures must be taken to protect the food supply.\n2) A disaster has occurred, or is in the process of occurring, and facilities in the vicinity must be identified in order to comprehensively evacuate and secure the area.\n\nTGS was not tasked with ensuring the completeness of this layer.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/b6b9cc72fb58476d92056d5c7ed25f8b_0'
    },
    {
        'name': 'State Fairgrounds',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/7f35881c8860490ab6a76516978e9e15_0.geojson',
        'table': 'state_fairgrounds',
        'sld': 'point',
        'description': 'This dataset represents the locations of the major state/regional agricultural fairs held throughout the United States. This dataset displays the locations and other pertinent information about the state level agricultural fairs held throughout the United States. It aids in providing the situational awareness for the agricultural sector, as well as the high value symbolic sector. Not only are the fairs gathering places for large numbers of livestock that then disperse, but large numbers of people congregate at these fairs. Additionally, other events--such as gun shows, arts & crafts shows, trade shows, etc.--are held at the fairgrounds locations through the year.\n\nSome states (e.g., Alaska) have multiple state fairground sites. Hawaii holds its main state fair event at the Aloha Bowl, but does not have any other specific state fairground facility. Rhode Island and Connecticut do not hold specific state fair events--just regional events. In summary, 47 states have at least 1 record within this database, while Hawaii, Connecticut, and Rhode Island are not represented. There are no state fair events represented in any of the major U.S. territories (e.g., Puerto Rico).\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/7f35881c8860490ab6a76516978e9e15_0'
    },
    {
        'name': 'EPA Emergency Response (ER) Toxic Substances Control Act (TSCA) Facilities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/5e2d8818b8ca4dbc8f14ea2e118b9a86_0.geojson',
        'table': 'epa_tsca_facilities',
        'sld': 'point',
        'description': 'This dataset represents integrated facility information from FRS, limited to the subset of facilities that link to the Toxic Substances Control Act (TSCA). This subset of data was identified as information that can be used in the Hazardous Materials Emergency Support Function #10. Additional contact, state ids, NAICs, and SIC attributes are linked by registry id. It contains only active facilities. This feature contains location and facility identification information from EPA\'s Facility Registry System (FRS) for the subset of facilities that link to the Toxic Substances Control Act (TSCA) System. The TSCA database supports the Toxic Substances Control Act (TSCA) of 1976, which provides EPA with authority to require reporting, record-keeping and testing requirements, and restrictions relating to chemical substances and/or mixtures. Certain substances are generally excluded from TSCA, including, among others, food, drugs, cosmetics and pesticides. TSCA addresses the production, importation, use, and disposal of specific chemicals including polychlorinated biphenyls (PCBs), asbestos, radon and lead-based paint.FRS identifies and geospatially locates facilities, sites or places subject to environmental regulations or of environmental interest. Using vigorous verification and data management procedures, FRS integrates facility data from EPA\'s national program systems, other federal agencies, and State and tribal master facility records and provides EPA with a centrally managed, single source of comprehensive and authoritative information on facilities. This data set contains the subset of FRS integrated facilities that link to TSCA facilities once the TSCA data has been integrated into the FRS database. Additional information on FRS is available at the EPA website http://www.epa.gov/enviro/html/fii/index.html.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/5e2d8818b8ca4dbc8f14ea2e118b9a86_0'
    },
    {
        'name': 'EPA Emergency Response (ER) Risk Management Plan (RMP) Facilities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/77002470dde842dca4da8fe9eadc557f_0.geojson',
        'table': 'epa_er_rmp_facilities',
        'sld': 'point',
        'description': 'This dataset represents integrated facility information from FRS, limited to the subset of facilities that link to the Risk Management Plan (RMP) database. This subset of data was identified as information that can be used in the Hazardous Materials Emergency Support Function #10. Additional contact, state ids, NAICs, and SIC attributes are linked by registry id. It contains only active facilities. This feature contains location and facility identification information from EPA\'s Facility Registry System (FRS) for the subset of facilities that link to the Risk Management Plan (RMP) database. RMP stores the risk management plans reported by companies that handle, manufacture, use, or store certain flammable or toxic substances, as required under section 112(r) of the Clean Air Act (CAA). FRS identifies and geospatially locates facilities, sites or places subject to environmental regulations or of environmental interest. Using vigorous verification and data management procedures, FRS integrates facility data from EPA\'s national program systems, other federal agencies, and State and tribal master facility records and provides EPA with a centrally managed, single source of comprehensive and authoritative information on facilities. This data set contains the subset of FRS integrated facilities that link to RMP facilities once the RMP data has been integrated into the FRS database. Additional information on FRS is available at the EPA website http://www.epa.gov/enviro/html/fii/index.html.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @  https://hifld-dhs-gii.opendata.arcgis.com/datasets/77002470dde842dca4da8fe9eadc557f_0'
    },
    {
        'name': 'EPA Emergency Response (ER) Toxic Release Inventory (TRI) Facilities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/5e549b76b1d74365bd6f25497105cd4d_0.geojson',
        'table': 'epa_er_tri_facilities',
        'sld': 'point',
        'description': 'This dataset represents integrated facility information from FRS, limited to the subset of facilities that link to the Toxic Release Inventory (TRI). This subset of data was identified as information that can be used in the Hazardous Materials Emergency Support Function #10. Additional contact, state ids, NAICs, and SIC attributes are linked by registry id. It contains only active facilities. This feature contains location and facility identification information from EPA\'s Facility Registry System (FRS) for the subset of facilities that link to the Toxic Release Inventory (TRI) System. TRI is a publicly available EPA database reported annually by certain covered industry groups, as well as federal facilities. It contains information about more than 650 toxic chemicals that are being used, manufactured, treated, transported, or released into the environment, and includes information about waste management and pollution prevention activities. FRS identifies and geospatially locates facilities, sites or places subject to environmental regulations or of environmental interest. Using vigorous verification and data management procedures, FRS integrates facility data from EPA\'s national program systems, other federal agencies, and State and tribal master facility records and provides EPA with a centrally managed, single source of comprehensive and authoritative information on facilities. This data set contains the subset of FRS integrated facilities that link to TRI facilities once the TRI data has been integrated into the FRS database. Additional information on FRS is available at the EPA website http://www.epa.gov/enviro/html/fii/index.html.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @  https://hifld-dhs-gii.opendata.arcgis.com/datasets/5e549b76b1d74365bd6f25497105cd4d_0'
    },
    {
        'name': 'US Hospitals',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/42ce7fa255f14f6e8c1933d3adf1e762_0.geojson',
        'table': 'hospitals',
        'sld': 'point',
        'description': 'This database represents locations of Hospitals for 50 states and Washington D.C. , Puerto Rico and US territories. The dataset only includes hospital facilities and does not include nursing homes. Data for all the states was acquired from respective states departments or their open source websites and then geocoded and converted into a spatial database. After geocoding the exact spatial location of each point was moved to rooftops wherever possible and points which have been physically verified have been labelled "Geocode", "Imagery", "Imagery with other" and "Unverified" depending on the methodology used to move the points. "Unverified" data points have still not been physically examined even though each of the points has been street geocoded as mentioned above. Missing records are denoted by "Not Available" or NULL values. Not Available denotes information that was either missing in the source data or data that has not been populated current version. This dataset has been developed to represent Hospitals for inclusion in the HSIP datasets.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @ https://hifld-dhs-gii.opendata.arcgis.com/datasets/42ce7fa255f14f6e8c1933d3adf1e762_0'

    },
    {
        'name': 'US Pharmacies',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/19145a0e403a4af4b2e4b76a6f2ec0ee_0.geojson',
        'table': 'pharmacies',
        'sld': 'point',
        'description': 'This dataset represents pharmacies in the United States and Territories. A pharmacy is a facility whose primary function is to store, prepare and legally dispense prescription drugs under the professional supervision of a licensed pharmacist. It meets any licensing or certification standards set forth by the jurisdiction where it is located. This geospatial dataset includes pharmacies in the United States, as well as the territories of American Samoa, Guam, Puerto Rico, the Commonwealth of the Northern Mariana Islands, and the Virgin Islands. The tabular data was gathered from the National Plan and Provider Enumeration System (NPPES) dataset. Pharmacies that were verified to service only animal populations were excluded from the dataset. The currentness of this dataset is indicated by the [CONTDATE] field. Based on this field the oldest record dates from 03/30/2010 and the newest record dates from 10/25/2010.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @  https://hifld-dhs-gii.opendata.arcgis.com/datasets/19145a0e403a4af4b2e4b76a6f2ec0ee_0'
    },
    {
        'name': 'Hazardous Materials Routes',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/b40531c05e0847b4a59555631833df16_0.geojson',
        'table': 'hazmat_routes',
        'sld': 'line',
        'description': 'This dataset represents all designated and restricted road and highway routes for highway route controlled quantities (HRCQ) of Class 7 (radioactive) materials (RAM) (HRCQ/RAM) and non-radioactive hazardous materials (NRHMs) transportation. The Federal Motor Carrier Safety Administration (FMCSA) Hazardous Material Routes were developed using the 2004 First Edition TIGER/Line files. The routes are described in the National Hazardous Material Route Registry (NMHRR). The on-line NMHRR linkage is http://hazmat.fmcsa.dot.gov/nhmrr/index.asp With the exception of 13 features that were not identified with the Tiger/Lines, Hazmat routes were created by extracting the TIGER/Line segments that corresponded to each individual route. Hazmat routes in the NTAD, are organized into 3 database files, hazmat.shp, hmroutes.dbf, and hmstcnty.dbf. Each record in each database represents a unique Tiger/Line segment. These Tiger/Line segments are grouped into routes identified as character strings in the ROUTE_ID field in the hmroutes.dbf table. The route name appearing in the ROUTE_ID is assigned by FMCSA and is unique for each State . The hmstcnty.dbf table allows the user to select routes by State and County. A single shapefile, called hazmat.shp, represents geometry for all routes in the United States.\n\nSource: Homeland Infrastructure Foundation-Level Data (HIFLD) @  https://hifld-dhs-gii.opendata.arcgis.com/datasets/b40531c05e0847b4a59555631833df16_0'
    }
]

def dataqs_extend():
    from settings import INSTALLED_APPS
    INSTALLED_APPS += DATAQS_APPS
