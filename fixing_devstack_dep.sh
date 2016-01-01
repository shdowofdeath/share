ehco "This is a rhel/centos machine ? or unbutu machine ? , case unbutu press u / centos/redhat pleasee c"
read os

if [ $os == "c" ]; then
sudo su
yum install python-setuptools
easy_install pip && exit
./stack.sh
else 
sudo su
apt-get install python-setuptools
easy_install pip && exit
./stack.sh
fi
