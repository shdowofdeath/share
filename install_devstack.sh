echo "Check OS"
os="uname -r"
repo="deb https://apt.dockerproject.org/repo ubuntu-trusty main"
if [$os == "3.11.0-15-generic"] ; then 
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "Update repo for docker with relevant key-chain , pleas emake sure this process is done "
echo $repo >> /etc/apt/sources.list.d/docker.list
echo "Craeting New repo for Docker  !!! :) YEeep "
echo " udpate full repo"
apt-get update
echo " update cache"
apt-cache policy docker-engine
echo "Finaly , we instllaiong docker "
sudo apt-get install docker-engine
echo "starting docker service"
sudo service docker start
echo " do u want to create docker now ? Hellow world , please press y"
read=ans
if [$ans == "y"] ; then 
sudo docker run hello-world
else
echo "by !! :)"
fi
else 
echo " OS is not good ?, bY "
fi



