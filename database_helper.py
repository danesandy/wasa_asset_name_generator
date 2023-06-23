import csv
import pandas as pd
from name_generator import app
from name_generator.models import *
from name_generator.utils import *

app.app_context().push()

# # ASSET_TYPE
# data = pd.read_csv("newcodes\Equipment_Codes.csv")
# asset_type = list(data["Description"])
# code = list(data["Equipment_Code"])

# for at, co in zip(asset_type, code):
#     if asset_type := AssetType.query.filter_by(description=at).first():
#         print(asset_type.description)
#         asset_type.code = co
#     else:
#         db.session.add(AssetType(description=at, code=co))
# db.session.commit()

# # Location Codes
# data = pd.read_csv("newcodes\Facilities.csv")
# location = list(data["Description"])
# code = list(data["Facility_ID"])

# for lo, co in zip(location, code):
#     if facility := LocationCode.query.filter_by(description=lo).first():
#         print(facility.description)
#     #     facility.code = co
#     # else:
#     #     db.session.add(LocationCode(description=str(lo), code=str(co)))
# db.session.commit()

# # Process Codes
# data = pd.read_csv("newcodes\Process_Codes.csv")
# process = list(data["Description"])
# code = list(data["Process_Code"])

# for pr, co in zip(process, code):
#     if proc := ProcessCode.query.filter_by(description=pr).first():
#         print(proc.description)
#         proc.code = co
#     else:
#         db.session.add(ProcessCode(description=pr, code=co))
# db.session.commit()

# # Delete all rows
# db.session.query(Asset).delete
# db.session.commit()

# # Service Codes
# data = pd.read_csv("codes\Service_codes.csv")
# service = list(data["SERVICE"])
# code = list(data["CODE"])

# for se, co in zip(service, code):
#     db.session.add(ServiceCode(description=se, code=co))
# db.session.commit()

# send_email('danesandy10@gmail.com', 'password')