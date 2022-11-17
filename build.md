# Instructions for building

## building chrome

we provide a Docker file as a building environment
for building our customized chrome.

1. Create a docker container 

```
docker build -f Dockerfile  --build-arg USER=$(whoami) --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t chrome_builder
docker run --name chrome_builder --hostname=chrome_builder --privileged -ti -d -v $HOME:$HOME chrome_builder:latest
```

2. login docker and download the chrome source

```
docker exec  -ti chrome_builder /usr/bin/zsh
cd <GleeFuzz_ROOT>
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=`pwd`/depot_tools:$PATH
mkdir chrome
cd chrome
fetch --nohooks --no-history chromium 
```

3. install dependencies

After the source has been downloaded in step 2, run the following commands in the container

```
cd src
./build/install-build-deps.sh
gclient runhooks
```

4. apply the patches 

In <GleeFuzz_ROOT> run the following commands:

```
cd chrome/src
git apply ../../log_message.patch
```

5. building chrome

```
gn gen out/custom_chrome
```

add the following to out/custom_chrome/arg.gn

```
is_asan = true
is_debug = true
enable_nacl=false
enable_gpu_client_logging=true
enable_gpu_service_logging=true

symbol_level = 2

proprietary_codecs = true
ffmpeg_branding = "Chrome"
```

start the build

```
autoninja -C out/chrome-no-ec-asan/ chrome
```
