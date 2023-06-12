import csv
import pandas as pd
from name_generator import app
from name_generator.models import *

app.app_context().push()

# # ASSET_TYPE
# data = pd.read_csv("codes\Asset_types.csv")
# asset_type = list(data["ASSET_TYPE"])
# code = list(data["CODE"])

# for at, co in zip(asset_type, code):
#     db.session.add(AssetType(description=at, code=co))
# db.session.commit()

# Location Codes
data = pd.read_csv("codes\Location_codes.csv")
location = list(data["LOCATION"])
code = list(data["CODE"])

for lo, co in zip(location, code):
    db.session.add(LocationCode(description=str(lo), code=str(co)))
db.session.commit()

# Process Codes
data = pd.read_csv("codes\Process_codes.csv")
process = list(data["PROCESS"])
code = list(data["CODE"])

for pr, co in zip(process, code):
    db.session.add(ProcessCode(description=pr, code=co))
db.session.commit()

# Service Codes
data = pd.read_csv("codes\Service_codes.csv")
service = list(data["SERVICE"])
code = list(data["CODE"])

for se, co in zip(service, code):
    db.session.add(ServiceCode(description=se, code=co))
db.session.commit()
