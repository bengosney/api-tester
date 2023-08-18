# Third Party
from icecream import ic

# First Party
from apitester.app.app import User

for id, field in User.model_fields.items():
    ic(id)

ic(User.model_fields.items())
