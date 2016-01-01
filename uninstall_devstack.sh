echo " deleteing context folders "
sudo rm -rf /opt/stack
sudo rm -rf /usr/local/bin/
cd /devstack
echo " cleaing stack "
./clean.sh
echo " Uninstalling stack"
./unstack.sh
echo " Please make sure env.v are re-set"

