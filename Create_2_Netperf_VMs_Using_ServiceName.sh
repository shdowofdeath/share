#!/bin/bash
. /etc/init.d/functions


#var
ip=$1
user=$2
Service_Name=$3  # Get Vsrx VM IP
#echo var
echo $ip
echo $user
echo $Service_Name

echo "export OS_USERNAME=$user" > setupUser
echo "export OS_PASSWORD=$user" >> setupUser
echo "export OS_TENANT_NAME=$user" >> setupUser
echo "export OS_AUTH_URL=http://$ip:5000/v2.0/" >> setupUser
echo "export OS_NO_CACHE=1" >> setupUser
echo ""
echo "printing source"
echo "######################################"
cat setupUser
echo "######################################"

source setupUser
sleep 2

VM_ID=$( nova list | grep -i $Service_Name | awk '{print $2}' )
#
##show results
echo "this is the vm ID:"
echo $VM_ID

#get tow diffrent networks for new VMs
Left_MNG_id=$( neutron net-list | grep -i net_ | awk '{print $2}' | awk NR==1)
#echo $Left_MNG_id
echo "left network :" $Left_MNG_id

Right_MNG_id=$(neutron net-list | grep -i net_ | awk '{print $2}' | awk NR==2)
echo "right network :" $Right_MNG_id




if [ -z $Right_MNG_id ] || [ -z $Right_MNG_id ]; then
	echo "Missing Mandatory Value"
	exit -1
fi

echo "elhay debug1"

Left_ip=$(nova show $VM_ID | grep -i left | awk '{print $5}')
echo "This is Left IP" $Left_ip
Right_ip=$(nova show $VM_ID | grep -i right | awk '{print $5}')
echo "This is Right IP" $Right_ip


echo "elhay debug 2"

LeftNetName=$(nova show $VM_ID |grep -i _left | awk '{print $2}')
echo "left Network "  $LeftNetName

RightNetName=$(nova show $VM_ID | grep -i _right | awk '{print $2}')
echo "right network " $RightNetName

#Left_ImageID=$(nova image-list | grep netperf_no_cloud_init_gateway | awk '{print $2}')
echo "Left ImageID" $Left_ImageID

ImageID=$(nova image-list | grep netperf_no_cloud_init | awk '{print $2}')
echo "Right ImageID" $ImageID

LeftNetID=$(neutron net-list | grep $LeftNetName | awk '{print $2}')
echo "Left Net ID" $LeftNetID

RightNetID=$(neutron net-list | grep $RightNetName | awk '{print $2}')
echo "Left Net ID" $RightNetID
sleep 1

#echo "elhay before creating vm last stage "
#rand=$RANDOM
#create the left VM
#nova boot --flavor m1.xlarge --image $Left_ImageID --security-groups default --nic net-id=$Left_MNG_id --nic net-id=$LeftNetID netperf_left_$rand
#sleep 1
#vm_status=$(nova list | grep -i netperf_left_$rand | awk '{print $6}')count=1
#while [ $vm_status != "ACTIVE" ]; doecho vm status is $vm_status ; if [ $count -gt 35 ] ; then echo image not up after 30 minutes, exiting ; exit 1 ; fi
##count=$(($count+1)) ; echo waiting to go ACTIVE ; sleep 1;
#vm_status=$(nova list | grep -i netperf_left_$rand| awk '{print $6}');done;
echo vm status is $vm_status !

echo "elhay before creating vm last stage "
rand=$RANDOM
#create the left VM
nova boot --flavor m1.xlarge --image $ImageID --security-groups default --nic net-id=$Left_MNG_id --nic net-id=$LeftNetID netperf_left_$rand
sleep 1
vm_status=$(nova list | grep -i netperf_left_$rand | awk '{print $6}')
count=1
while [ $vm_status != "ACTIVE" ]; do
echo vm status is $vm_status ; if [ $count -gt 35 ] ; then echo image not up after 30 minutes, exiting ; exit 1 ; fi
count=$(($count+1)) ; echo waiting to go ACTIVE ; sleep 1;
vm_status=$(nova list | grep -i netperf_left_$rand| awk '{print $6}');done;
echo vm status is $vm_status !

##create the right VM
nova boot --flavor m1.xlarge --image $ImageID --security-groups default --nic net-id=$Right_MNG_id --nic net-id=$RightNetID netperf_right_$rand

vm_status=$(nova list | grep -i netperf_right_$rand | awk '{print $6}')
count=1
while [ $vm_status != "ACTIVE" ]; do
echo vm status is $vm_status ; if [ $count -gt 35 ] ; then echo image not up after 30 minutes, exiting ; exit 1 ; fi
count=$(($count+1)) ; echo waiting to go ACTIVE ; sleep 1;
vm_status=$(nova list | grep -i netperf_right_$rand| awk '{print $6}');
done;
echo vm status is $vm_status !


#while ! ping -c1 10.57.20.252 &>/dev/null; do :; done

##create the left VM
#nova boot --flavor m1.xlarge --image $ImageID --security-groups default --nic net-id=$Left_MNG_id netperf_left
#sleep 6
#nova interface-attach --net-id $LeftNetID netperf_left
##create the right VM
#nova boot --flavor m1.xlarge --image $ImageID --security-groups default --nic net-id=$Right_MNG_id netperf_right
#sleep 6
#nova interface-attach --net-id $RightNetID netperf_right

#need to change image creation
# nova interface-attach --net-id $LeftNetID netperf_left

#usage: nova interface-attach [--port-id <port_id>] [--net-id <net_id>]
#                             [--fixed-ip <fixed_ip>]
#                             <server>

sleep 1
#deldeete env
# rm -rf setup1  userdata="#!/bin/bash \n echo 'AMAZING TEST' > /root/test"









de
