# install Docker
apt-get update
apt-get install -y curl
curl -fsSL 'https://get.docker.com' -o get-docker.sh
sh get-docker.sh
usermod -aG docker bioarineo

# enable other platforms - TBD some of these commands are needed
apt-get install qemu binfmt-support qemu-user-static
docker run --rm --privileged linuxkit/binfmt:v0.8
docker run --rm --privileged multiarch/qemu-user-static --reset
docker run --privileged --rm tonistiigi/binfmt --install all

# install buildx plugin
# to ~/.docker/config.json add "experimental": "enabled"
# needs to be done programmatically, (jq?)
docker buildx create --name builder --use
