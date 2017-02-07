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
    'dataqs.cmap',
    'dataqs.landscan',
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
    },
    'cmap': {
        'task': 'dataqs.cmap.tasks.cmap_task',
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
    },
    {
        'name': 'Colleges and Universities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/4061dcd767c340d4a42fb7a0c6c5d5b4_0.geojson',
        'table': 'colleges_universities',
        'sld': 'point',
        'description': 'The Colleges and Universities shapefile is composed of all Post Secondary Education facilities as defined by the Integrated Post Secondary Education System (IPEDS, http://nces.ed.gov/ipeds/), National Center for Education Statistics (NCES, https://nces.ed.gov/), US Department of Education for the 2013-2014 school year. Included are Doctoral/Research Universities, Masters Colleges and Universities, Baccalaureate Colleges, Associates Colleges, Theological seminaries, Medical Schools and other health care professions, Schools of engineering and technology, business and management, art, music, design, Law schools, Teachers colleges, Tribal colleges, and other specialized institutions. Overall, this data layer covers all 50 states, as well as Puerto Rico and other assorted U.S. territories. This shapefile contains all MEDS/MEDS+ as approved by the National Geospatial-Intelligence Agency (NGA) Homeland Security Infrastructure Program (HSIP) Team. Complete field and attribute information is available in the ”Entities and Attributes” metadata section. Geographical coverage is depicted in the thumbnail above and detailed in the "Place Keyword" section of the metadata. This shapefile does not have a relationship class but is related to Supplemental Colleges. Colleges and Universities that are not included in the NCES IPEDS data are added to the Supplemental Colleges shapefile when found.'
    },
    {
        'name': 'Nursing Homes',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/e60622bb7fb344e889d9d03473aba74c_0.geojson',
        'table': 'nursing_homes',
        'sld': 'point',
        'description': 'The Nursing Home / Assisted Care shapefile contains facilities that house elderly adults. This shapefile’s attribution contains physical and demographic information for facilities in the continental United States, Hawaii, Alaska, District of Columbia and Puerto Rico. The purpose of this shapefile is to provide accurate locations for high concentrations of elderly adults in the event of a disaster. The attribution within this shapefile was populated via open source methodologies of authoritative sources.'
    },
    {
        'name': 'Veterans Health Administration Medical Facilities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/ec34e1f8ef7948e88b330ba8addeb571_0.geojson',
        'table': 'veterans_health_administration_medical_facilities',
        'sld': 'point',
        'description': 'Veterans Health Administration Medical Facilities in the United States This dataset includes Veteran Affairs hospitals, Veteran Affairs residential rehabilitation treatment programs, Veteran Affairs Nursing Home Care Units (NHCU), Veteran Affairs Outpatient Clinics, Vet Centers, and Veteran Affairs Medical Centers. It should not include planned and suspended (non-operational) sites and mobile clinics. These definitions were set by the Veterans Health Administration (VHA) Policy Board in December 1998 and are the basis for defining the category and the additional service types for each VHA service site. These definitions cover sites generally owned by the Department of Veterans Affairs (VA) with the exception of leased and contracted community-based outpatient clinics (CBOCs). 1. VA HOSPITAL: an institution (health care site) that is owned, staffed and operated by VA and whose primary function is to provide inpatient services. NOTE: Each geographically unique inpatient division of an integrated facility is counted as a separate hospital. 2. VA RESIDENTIAL REHABILITATION TREATMENT PROGRAM: provides comprehensive health and social services in a VA facility for eligible veterans who are ambulatory and do not require the level of care provided in nursing homes. 3. VA NURSING HOME CARE UNITS (NHCU): provides care to individuals who are not in need of hospital care, but who require nursing care and related medical or psychosocial services in an institutional setting. VA NHCUs are facilities designed to care for patients who require a comprehensive care management system coordinated by an interdisciplinary team. Services provided include nursing, medical, rehabilitative, recreational, dietetic, psychosocial, pharmaceutical, radiological, laboratory, dental and spiritual. 4. VA OUTPATIENT CLINICS: a. Community-Based Outpatient Clinic: a VA -operated, VA -funded, or VA -reimbursed health care facility or site geographically distinct or separate from a parent medical facility. This term encompasses all types of VA outpatient clinics, except hospital-based, independent and mobile clinics. Satellite, community-based, and outreach clinics have been redefined as CBOCs. Technically, CBOCs fall into four Categories, which are: > (i) VA-owned. A CBOC that is owned and staffed by VA. > (ii) Leased. A CBOC where the space is leased (contracted), but is staffed by VA. NOTE: This includes donated space staffed by VA. > (iii) Contracted. A CBOC where the space and the staff are not VA. This is typically a Healthcare Management Organization (HMO)-type provided where multiple sites can be associated with a single station identifier. > (iv) Not Operational. A CBOC which has been approved by Congress, but has not yet begun operating. b. Hospital-Based Outpatient Clinic: outpatient clinic functions located at a hospital. c. Independent Outpatient Clinic: a full-time, self-contained, freestanding, ambulatory care clinic that has no management, program, or fiscal relationship to a VA medical facility. Primary and specialty health care services are provided in an outpatient setting. 5. VET CENTER: Provides professional readjustment counseling, community education, outreach to special populations, brokering of services with community agencies, and access to links between the veteran and VA. 6. VA MEDICAL CENTER: a medical center is a unique VA site of care providing two or more types of services that reside at a single physical site location. The services provided are the primary service as tracked in the VHA Site Tracking (VAST) (i.e., VA Hospital, Nursing Home, Domiciliary, independent outpatient clinic (IOC), hospital-based outpatient clinic (HBOC), and CBOC). The definition of VA medical center does not include the Vet Centers as an identifying service. This dataset is based upon GFI data received from the National Geospatial-Intelligence Agency (NGA). At the request of NGA, text fields in this dataset have been set to all upper case to facilitate consistent database engine search results. At the request of NGA, all diacritics (e.g., the German umlaut or the Spanish tilde) have been replaced with their closest equivalent English character to facilitate use with database systems that may not support diacritics. The currentness of this dataset is indicated by the [CONTDATE] attribute. Based upon this attribute, the oldest record dates from 09/21/2007 and the newest record dates from 10/15/2007.'
    },
    {
        'name': 'Major Sport Venues',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/15142d7e20074d2390efeab9a2fe9aa8_0.geojson',
        'table': 'major_sport_venues',
        'sld': 'point',
        'description': "The Major Sport Venues dataset is composed of facilities within the United States, Canada, and Mexico that host events for the National Association for Stock Car Auto Racing (NASCAR), Indy Racing League (IRL), Major League Soccer (MLS), Major League Baseball (MLB), National Basketball Association (NBA), Women's National Basketball Association (WNBA), National Hockey League (NHL), National Football League (NFL), Professional Golfers Association (PGA) Tour, National Collegiate Athletic Association (NCAA) Division 1-Football Bowl Subdivision (FBS), National Collegiate Athletic Association (NCAA) Division 1 Basketball, Minor League Baseball (MiLB) Class Triple-A, and thoroughbred horse racing. Large numbers of people congregate at these facilities to attend major sporting events, therefore the locations of these facilities and the characteristics that describe each facility is essential for emergency preparedness, response, and evacuation. [NOTE: This shapefile is related (one-to-many) to the “Usage” table, which captures the relationship between “MajorSportVenues” and its associated events. “MajorSportVenues” is the origin using VENUEID as the primary key. The “Usage” table is the destination using VENUEID as the foreign key. The relationship is used to demonstrate multiple uses/events at a single venue location.]"
    },
    {
        'name': 'Day Care Centers',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/3a9271a1a30443fca150461b35a51b53_0.geojson',
        'table': 'day_care_centers',
        'sld': 'point',
        'description': 'This database contains locations of day care centers for 50 states of USA, Washington D.C., and Puerto Rico.The dataset only includes center based day care locations (including schools and religious institutes) and does not include group, home, and family based day cares. All the data was acquired from respective states departments or their open source websites and contains data only provided by these sources. Information on the source of data for each state is available in the database itself.Data for the states of AK, AR, AZ, CA, CT, FL, GA, IA, ID, IN, KY, LA, MI, MO, MN, MS, MT, NC, NV, NY, OH, PA, SC, SD, and TX was updated in this release.Currency of data is denoted by the SOURCEDATE field.The TYPE attribute is a common classification of day care for all states which classifies every day care into Center Based, School Based, Head Start, or Religious Facility.'
    },
    {
        'name': 'Private Schools',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/36695bf035fb4e98a88dbdcbaca2c40d_0.geojson',
        'table': 'private_schools',
        'sld': 'point',
        'description': 'This dataset represents private schools composed of all private elementary and secondary education features in the United States as defined by the Private School Universe Survey (PSS), National Center for Education Statistics, US Department of Education. This includes all kindergarten through 12th grade schools as tracked by the PSS. This feature class contains all MEDS/MEDS+ attributes as approved by NGA. For each field, the 'Not Available' and NULL designations are used to indicate that the data for the particular record and field is currently unavailable and will be populated when and if that data becomes available.'
    },
    {
        'name': 'Public Schools',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/1f74a16c80e949c0adfd7866684b83c5_0.geojson',
        'table': 'public_schools',
        'sld': 'point',
        'description': 'This Public Schools feature dataset is composed of all Public elementary and secondary education facilities in the United States as defined by the Common Core of Data(CCD, https://nces.ed.gov/ccd/ ), National Center for Education Statistics (NCES, https://nces.ed.gov ), US Department of Education for the 2012-2013 school year. This includes all Kindergarten through 12th grade schools as tracked by the Common Core of Data. Included in this dataset are military schools in US territories and referenced in the city field with an APO or FPO address. DOD schools represented in the NCES data that are outside of the United States or US territories have been omitted. This shapefile contains all MEDS/MEDS+ as approved by NGA. Complete field and attribute information is available in the ”Entities and Attributes” metadata section. Geographical coverage is depicted in the thumbnail above and detailed in the Place Keyword section of the metadata. This shapefile does not have a relationship class.'
    },
    {
        'name': 'Urgent Care Facilities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/0d748999f5eb4e76a7e0389442381af6_0.geojson',
        'table': 'urgent_care_facilities',
        'sld': 'point',
        'description': "Urgent Care Facilities Urgent care is defined as the delivery of ambulatory medical care outside of a hospital emergency department on a walk-in basis without a scheduled appointment. (Source: Urgent Care Association of America) The Urgent Care dataset consists of any location that is capable of providing emergency medical care and must provide emergency medical treatment beyond what can normally be provided by an EMS unit, must be able to perform surgery, or must be able to provide recuperative care beyond what is normally provided by a doctor's office. In times of emergency, the facility must be able to accept patients from the general population or patients from a significant subset of the general population (e.g., children). Florida and Arizona license Urgent Care facilities within their state. However, the criteria for licensing and the criteria for inclusion in this dataset do not appear to be the same. For these two states, this dataset contains entities that fit TGS' criteria for an Urgent Care facility but may not be licensed as Urgent Care by the state. During processing, TGS found that this is a rapidly changing industry. Although TGS intended for all Urgent Care facilities to be included in this dataset, the newest facilities may not be included. Entities that are excluded from this dataset are administrative offices, physician offices, workman compensation facilities, free standing emergency rooms, and hospitals. Urgent Care facilities that are operated by and co-located with a hospital are also excluded because the locations are included in the hospital dataset. ID# 10194253 is a 'mobile' urgent care center that provides urgent care to private residences. This entity is plotted at its administrative building. Records with '-DOD' appended to the end of the [NAME] value are located on a military base, as defined by the Defense Installation Spatial Data Infrastructure (DISDI) military installations and military range boundaries. At the request of NGA, text fields in this dataset have been set to all upper case to facilitate consistent database engine search results. At the request of NGA, all diacritics (e.g., the German umlaut or the Spanish tilde) have been replaced with their closest equivalent English character to facilitate use with database systems that may not support diacritics. This dataset does not contain any Urgent Care facilities in American Samoa, Guam, the Virgin Islands, or the Commonwealth of the Northern Mariana Islands. The currentness of this dataset is indicated by the [CONTDATE] field. Based upon this field, the oldest record is dated 11/22/2004 and the newest record is dated 07/17/2009."
    },
    {
        'name': 'All Places of Worship',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/ece7900854a443c28e1351a2eb3d7e7c_0.geojson',
        'table': 'all_places_of_worship',
        'sld': 'point',
        'description': "Places of Worship in the United States. The Places of Worship dataset is composed of any type of building or portion of a building that is used, constructed, designed, or adapted to be used as a place for religious and spiritual activities. These facilities include, but are not limited to, the following types: chapels, churches, mosques, shrines, synagogues, and temples. The license free Large Protestant Churches, Mosques, Jewish Synagogues, and Roman Catholic Churches in Large Cities datasets were merged together to create the initial data for the Places of Worship dataset. Additional entities have been added from TGS research. This dataset contains Buddhist, Christian, Hindu, Islamic, Judaic, and Sikh places of worship. Unitarian places of worship have been included when a congregation from one of these religions meets at a church owned by a Unitarian congregation. Some Protestant denominations are not currently represented in this dataset. The Places of Worship dataset is not intended to include homes of religious leaders (unless they also serve as a place of organized worship), religious schools (unless they also serve as a place of organized worship for people other than those enrolled in the school), Jewish Mikvahs or Hillel facilities, and buildings that serve a purely administrative purpose. If a building's primary purpose is something other than worship (e.g., a community center, a public school), but a religious group uses the building for worship on a regular basis, it was included in this dataset if it otherwise met the criteria for inclusion. Convents and monasteries are included in this dataset, regardless of whether or not the facilities are open to the public, because religious services are regularly held at these locations. TGS was not tasked with ensuring the completeness of this layer. No entities are included in this dataset for the Commonwealth of the Northern Mariana Islands. On 08/07/2007, TGS ceased making phone calls to verify information about religious locations. Therefore, most entities in this dataset were verified using alternative reference sources such as topographic maps, parcel maps, various sources of imagery, and internet research. The [CONTHOW] (contact how) value for these entities has been set to 'ALT REF'. The website http://www.gettochurch.org was used for verification during processing. As of August 2009, this website is no longer active. Records with '-DOD' appended to the end of the [NAME] value are located on a military base, as defined by the Defense Installation Spatial Data Infrastructure (DISDI) military installations and military range boundaries."
    },
    {
        'name': 'Jewish Synagogues',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/c40427b8d2a342b58e819f87d521abfb_0.geojson',
        'table': 'jewish_synagogues',
        'sld': 'point',
        'description': "The Jewish Synagogues dataset is derived from the TGS 2009 Q4 'PlacesofWorship' data layer and contains all Jewish Synagogues in the United States. The remaining portion of this abstract, as well as much of the remaining metadata, references the entire Places of Worship database from which this subset was derived: The Places of Worship dataset is composed of any type of building or portion of a building that is used, constructed, designed, or adapted to be used as a place for religious and spiritual activities. These facilities include, but are not limited to, the following types: chapels, churches, mosques, shrines, synagogues, and temples. The license free Large Protestant Churches, Mosques, Jewish Synagogues, and Roman Catholic Churches in Large Cities datasets were merged together to create the initial data for the Places of Worship dataset. Additional entities have been added from TGS research. This dataset contains Buddhist, Christian, Hindu, Islamic, Judaic, and Sikh places of worship. Unitarian places of worship have been included when a congregation from one of these religions meets at a church owned by a Unitarian congregation. Some Protestant denominations are not currently represented in this dataset. The Places of Worship dataset is not intended to include homes of religious leaders (unless they also serve as a place of organized worship), religious schools (unless they also serve as a place of organized worship for people other than those enrolled in the school), Jewish Mikvahs or Hillel facilities, and buildings that serve a purely administrative purpose. If a building's primary purpose is something other than worship (e.g., a community center, a public school), but a religious group uses the building for worship on a regular basis, it was included in this dataset if it otherwise met the criteria for inclusion. Convents and monasteries are included in this dataset, regardless of whether or not the facilities are open to the public, because religious services are regularly held at these locations. TGS was not tasked with ensuring the completeness of this layer. No entities are included in this dataset for the Commonwealth of the Northern Mariana Islands. On 08/07/2007, TGS ceased making phone calls to verify information about religious locations. Therefore, most entities in this dataset were verified using alternative reference sources such as topographic maps, parcel maps, various sources of imagery, and internet research. The [CONTHOW] (contact how) value for these entities has been set to 'ALT REF'. The website http://www.gettochurch.org was used for verification during processing. As of August 2009, this website is no longer active. Records with '-DOD' appended to the end of the [NAME] value are located on a military base, as defined by the Defense Installation Spatial Data Infrastructure (DISDI) military installations and military range boundaries."
    }
]

def dataqs_extend():
    from settings import INSTALLED_APPS
    INSTALLED_APPS += DATAQS_APPS
