import os
from dotenv import load_dotenv
from globalUtils.positions import get_positions

load_dotenv()


d = get_positions()
print(d)
