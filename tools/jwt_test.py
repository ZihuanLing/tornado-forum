import time
from datetime import datetime

import jwt

current_time = datetime.utcnow()

data = jwt.encode({
    'name': 'zihuan',
    'id': 1,
    'exp': current_time,
}, 'abc').decode('utf8')

time.sleep(2)

send_data = jwt.decode(data, 'abc', leeway=1, options={'verify_exp': False})

print(send_data)