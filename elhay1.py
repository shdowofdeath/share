import sys
import os
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import jnpr


device = Device(host='10.247.140.4', user='juniper', password='Juniper123' )
device.open()

#pprint( device.facts )
device.bind(cfg=Config)
try:
    device.rpc.open_configuration(private=True)
except jnpr.junos.exception.RpcError as e:
    if 'severity: warning' in str(e):
        print str(e) 
        pass
    else:
        raise

device.bind( device=Config )
xml= """
            <configuration>
            <interfaces>
            <interface>
            <name>ge-1/1/0</name>
            <unit>
            <name>1500</name>
            <family>
            <inet operation="delete">
            </inet>
            </family>
            </unit>
            </interface>
            </interfaces>
            </configuration>"""
device.load(xml,format='xml')
device.commit
#for line in open("fila"):
# device = Config(device)
# set_cmd = line
# device.load(set_cmd, format='set')
# device.pdiff()
# device.commit()

#for line in open("fila"):
# print device.cli(line)


#device.cfg.load(template_path=template, template_vars=customer)


#device.bind(cu=Config)
#device.rpc.open_configuration(private=True,normalize=True)
#device.cu.load("set system host-name r0")
#device.cu.commit()
#device.rpc.close_configuration()


device.close()
