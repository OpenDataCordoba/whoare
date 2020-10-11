from datetime import datetime
from whoare.whoare import WhoAre

wa = WhoAre()
wa.load('data99.com.ar')

assert wa.domain.changed == datetime.now() 
