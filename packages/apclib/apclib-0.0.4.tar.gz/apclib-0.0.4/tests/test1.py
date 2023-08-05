# %%
import os
import sys
sys.path.append(
        os.path.dirname(
            os.path.dirname(__file__))+"\\src")

print (sys.path)
import apclib
from apclib import controllers
import apclib.models

# print (apclib.controllers.gain_update)
# %%
from apclib.controllers import fuzzy