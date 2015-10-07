__author__ = 'elhay' 

import os,re, logging, pprint, sys
from common.credentials import *
from common.network import *
from prettytable import *

from novaclient import client as nova_client
import keystoneclient.v2_0.client as ksclient
import neutronclient.neutron.client as neclient
from cinderclient import client as cinder_client

# Some messaging
msg_main_menu = "\
1. \n\
2. Create untaged public Network\n\
3. Create VM(s)\n\
4. List VM ip's\n\
5. Create snapshot from VM\n\
6. Create Volume\n\
7. Create Multiple Volume\n\
8. Create 8 networks.\n\
9. Delete All VM's\n\
Q. Quit\n\
What do you want to do? "


def create_cinder_volume(cinder):
    size = questionIntOnly ("Size in GB ? \n")
    myvol = cinder.volumes.create(size=size)
    print myvol.id

def create_many_cinder_volume(cinder):
    size    = questionIntOnly ("Size in GB ? \n")
    howMany = questionIntOnly("How Many ? \n")
    for i in range(howMany):
        myvol = cinder.volumes.create(size=size)
        print myvol.id

def create_public_net(neutron,ip):
    networks = neutron.list_networks()[NETWORKS]
    for network in networks:
        if 'public_net' in network[NAME]:
            print 'public_net already exists :)'
            return

    public_net = {  u'admin_state_up'           : True,
                    u'name'                     : 'public_net',
                    u'provider:network_type'    : u'flat',
                    u'provider:physical_network': u'RegionOne',
    }

    network_id = neutron.create_network( {'network':public_net } )['network']['id']

    public_subnet = { 'subnet':
                {   u'allocation_pools': [{u'end': ip+u'.250', u'start': ip+u'.100'}],
                    u'cidr': ip+u'.0/24',
                    u'dns_nameservers': [],
                    u'enable_dhcp': True,
                    u'gateway_ip': ip+u'.1',
                    u'host_routes': [],
                    u'ip_version': 4,
                    u'name': u'public_subnet',
                    u'network_id' : network_id
                    }
    }

    neutron.create_subnet(public_subnet)

    return

def create_many_net(neutron,howmany):
    networks = neutron.list_networks()[NETWORKS]
    #for network in networks:
    #    if 'public_net' in network[NAME]:
    #        print 'public_net already exists :)'
    #        return
    count = 1
    for i in range(howmany):
	    print 'Run Number ' + str(i)
	    vlan=count + 1
	    public_net = {  u'admin_state_up'           : True,
			    u'name'                     : 'net_'+str(count),
			    u'provider:network_type'    : u'vlan',
			    u'provider:segmentation_id' : vlan,
			    u'provider:physical_network': u'RegionOne',
	    }

	    network_id = neutron.create_network( {'network':public_net } )['network']['id']
	    ip = str(count+10)+".0.0"
	    public_subnet = { 'subnet':
			{   #u'allocation_pools': [{u'end': ip+u'.250', u'start': ip+u'.100'}],
			    u'cidr': ip+u'.0/24',
			    u'dns_nameservers': [],
			    u'enable_dhcp': True,
			    u'gateway_ip': ip+u'.1',
			    u'host_routes': [],
			    u'ip_version': 4,
			    u'name': u'public_subnet',
			    u'network_id' : network_id
			    }
	    }

	    neutron.create_subnet(public_subnet)
	    count = count + 1
    return
# Deploy from snapshot
def deploy_vm_from_tmpl(nova, neutron):

    # warning !!!
    print """
    ******************************************************************
    Please pay attention on VM's name and id!!!
    ******************************************************************
    """
    # selecting image
    images = nova.servers.list()
    show_options(images, True)
    answer = get_int_input("Select VM to take Snapshot (to make template): \n")
    image = images[answer].id
    nova.servers.create_image(image, "somename")

    return

# Deploy new VM
def deploy_vm(nova, neutron):

    # selecting image
    images = nova.images.list()
    show_options(images)
    answer = get_int_input("Select Image: \n")
    image  = images[answer].id

    # selecting flavor
    flavors = nova.flavors.list()
    show_options(flavors)
    answer = get_int_input("Select Flavore: \n")
    flavor  = flavors[answer].id
    # handle keypair
    if not nova.keypairs.findall(name="mykey"):
        with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
            nova.keypairs.create(name="mykey", public_key=fpubkey.read())

    networks = nova.networks.list()
    pprint.pprint(networks)

    answer = raw_input('Select network : \n');
    network  = nova.networks.find(label=answer)

    num_of_vms = questionIntOnly ("How many VM's? \n")
    num_of_cunc = questionIntOnly ("How many cuncurrent? \n")
    print '------------------'
    for i in range(num_of_vms/num_of_cunc):
	#nova.servers.create(name = "test", image = image, flavor = flavor, network = network.id, min_count = 1, max_count = 10 , key_name="mykey" )
	nova.servers.create(name = "bulk-"+str(i) , image = image, flavor = flavor, max_count=num_of_cunc, network = network.id, key_name="mykey" )
	print 'Started ' + str( (i+1)*num_of_cunc)
# Show list of all vm ips (name, ip)
#def list_vm_ips(nova):
#    list_dict = []
#
#    for server in nova.servers.list():
#        for k in server.networks:
#            list_dict.append([server.name, server.status, str(server.networks[k][0])])
#
#    show_table(list_dict, ['VM','STATE', 'IP'])
#
#    return

def list_vm_ips(nova):
    list_dict = []

    for server in nova.servers.list():
	if server.networks is None:
	    list_dict.append([server.name,server.status,''])
        else:
	    for k in server.networks:
                list_dict.append([server.name, server.status, str(server.networks[k][0])])

    show_table(list_dict, ['VM','STATE', 'IP'])

def delete_all_vms(nova ):
    answer = raw_input('Sure about this?  \n');
    if 'Yes' or 'yes' in answer:
	print 'Deleteing all\n'
        list_dict = []
	for i in range(2):
	    for server in nova.servers.list():
                print 'delete - ' , [server.name]
	        try:
	            nova.servers.delete(server.id)
	        except Exception as e:
		    print e , 'Skiping'

##
# Support functions
##

#  output formated in well readable ASCII table
def show_table(some_array, header = []):
    x = PrettyTable(header)
    x.align[header[0]] = 'l'

    for i in some_array:
        x.add_row(i)

    print x
    print 'Total: ' , len(some_array)
    return

def pressanykey():
    raw_input("Press Enter to proceed.")
    os.system('clear')
    return

def questionIntOnly(questionString):
    """
    Loops until Integer inserted.
    """
    while True:
        try:
            return int(raw_input(questionString))
        except KeyboardInterrupt:
            print "\nBreak Detected. Exiting."
            sys.exit(1)
        except Exception:
            print "Only numbers allowed."
    return

def show_options(obj, insert_id = False):
    i = 1
    if insert_id:
        for m in obj:
            print "%s: %s ( %s )" % (str(i), m.name, m.id)
            i+=1
    else:
        for m in obj:
            print "%s: %s" % (str(i), m.name)
            i+=1

    return

def get_int_input(msg):
    return questionIntOnly(msg) - 1;

# all things rung from within :)
def main():

    # invoking key sets from credentials module
    keystone_creds  = get_credentials(CRD_KEYSTONE)
    nova_creds      = get_credentials(CRD_NOVA)
    neutron_creds   = get_credentials(CRD_NEUTRON)

    keystone        = ksclient.Client(**keystone_creds)
    nova            = nova_client.Client("1.1", **nova_creds)

    cinder = cinder_client.Client('1', **nova_creds )

    network_service = {'network' : keystone.service_catalog.get_endpoints()['network'][0]}

    neutron         = neclient.Client('2.0', endpoint_url=network_service['network']['adminURL'] ,**neutron_creds)
    ip              = network_service['network']['adminURL'].split(':')[1].replace('/','')
    ip              = ip[0:ip.rfind('.')]


    #pprint.pprint (nova.servers.list() )
    #pprint.pprint (neutron.list_networks()['networks'] )
    #pprint.pprint (neutron.list_subnets()['subnets'])

    #megafunc(nova)
    #sys.exit();
    try:
        while 1:
            os.system('clear')
            ans = raw_input(msg_main_menu)

            if ans == "1":
                #list_vms(nova)
                pressanykey()
            elif ans == "2":
                create_public_net(neutron,ip)
                pressanykey()
            elif ans == '3':
                deploy_vm(nova, neutron)
		pressanykey()
            elif ans == '4':
                list_vm_ips(nova)
                pressanykey()
            elif ans == '5':
                deploy_vm_from_tmpl(nova, neutron)
                pressanykey()
            elif ans == '6':
                create_cinder_volume(cinder)
                pressanykey()
            elif ans == "7":
                #    sure = raw_input( "Are you sure about that? type 'yes' if you are.\n")
                #    if 'yes' in sure:
                create_many_cinder_volume(cinder)
                pressanykey()
            elif ans == '8':
		create_many_net(neutron,8)
	    elif ans == '9':
		delete_all_vms(nova)
		pressanykey()
            elif ans.lower() == "q":
                os.sys.exit()

    except KeyboardInterrupt:
        print "\nExiting.    "



if __name__ == "__main__":
    main()

