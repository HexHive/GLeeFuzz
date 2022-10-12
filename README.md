# GLeeFuzz: Fuzzing WebGL Through Error Message Guided Mutation

## Overview

A GLeeFuzz fuzzing environment consists of: 
* A ***hub server*** responsible for generating fuzzing inputs, mutating, and dispatching test quests to test machines; 
* A ***web executor server*** hosting the test webpages.
* One or more ***test machines*** machines running target browsers to fuzz;

These component can be run on one physical machine, or run on different machines in the same LAN, or over the Internet.

## Installation
## Test environment setup

We recommend that you install GLeeFuzz on a freshly-installed Ubuntu 20.04 to avoid python version problems. We also recommend that you backup your system before using GLeeFuzz, as its installation or usage might cause unexpected errors.

### Machine requirements

We have tested GLeeFuzz on Ubuntu 20.04. Please make sure you have at least 16GB RAM and 128GB disk space. 

GLeeFuzz needs a custom-built Chromium for error message collection. We provide our patch that enables error message feedback, and also provide the other patches needed to build Chromium for static analysis. Please find the patches and instructions under `chrome_patches` folder in our repo. Please refer to https://chromium.googlesource.com/chromium/src/+/main/docs/linux/build_instructions.md for build instructions.

### Pre-built Chromium
We provide pre-built binaries for both baseline Chromium (not modified for error message collection) and custom-built Chromium with error message collection. You can download at,

`https://drive.google.com/drive/folders/1cDT03bvHC7sTyos9eK_OFHbBEk0LhUNM`

### Server installation

The following scripts will install all the dependencies for the fuzzing server and web executor server. 

```bash
sudo apt-get update

sudo apt install -y python3-venv
sudo apt install -y apache2
sudo apt install -y default-jre
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# INSTALL dependencies and python 3.9.9
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init --path)"\nfi' >> ~/.bashrc
exec $SHELL
source .bashrc
pyenv install 3.9.9
pyenv global 3.9.9

# INSTALL PHP
sudo echo "SetHandler application/x-httpd-php" >> /etc/apache2/apache2.conf
sudo a2dismod mpm_event 
sudo a2enmod mpm_prefork 
sudo apt install libapache2-mod-php7.2 libapache2-mod-php
sudo a2enmod php7.2
sudo systemctl restart apache2.service

# INSTALL GLeeFuzz
git clone https://github.com/HexHive/GLeeFuzz
sudo cp -r /var/www/html /var/www/html_backup
sudo cp -r GLeeFuzz/webgl-executor/* /var/www/html
```

Now, WebGL executor should be able to be accessed from a browser. The default Apache server port is 80, so you should be able to see our web executor at `127.0.0.1:80`.

Next, save the address of the hub machine by editing `webdriver/selenium-setup/env.rc`, e.g., `export SELENIUM_HUB_ADDR=127.0.0.1`.

### Test machine setup

You may setup the test machine on the same computer where the server is installed.

On each test machine, do the following setups,

```bash
sudo apt-get update

sudo apt install -y python3-venv
sudo apt install -y default-jre
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# INSTALL dependencies and python 3.9.9
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init --path)"\nfi' >> ~/.bashrc
exec $SHELL
source .bashrc
pyenv install 3.9.9
pyenv global 3.9.9

# INSTALL GLeeFuzz
git clone https://github.com/HexHive/GLeeFuzz
```

Install the test targets (browser binaries, e.g., Chrome/Firefox/Safari) and download 
their respective webdriver programs, and place them in a directory 
that is included in `PATH` environmental variable.

## To evaluate GLeeFuzz with pre-built Chromium (version 96.0.4664)

Modify webdriver to match the nearest web-driver supported Chrome version, without the last digit in the version number
`venv/lib/python3.9/site-packages/webdriver_manager/drivers/chrome.py`
Change
`browser_version = self.get_browser_version()`
to
`browser_version = "96.0.4664"`

Our customized error-feedback Chromium is based on 96.0.4664.
If you want to run GLeeFuzz with other Chrome version (other than the system's default Chrome installation), you can change the version number to match the one you want to run.

## To use GLeeFuzz with system's default Chrome installation
You don't have to change anything. Chrome driver manager will find the correct web driver for your Chrome.

Then, setup test machine address and hub address in `webdriver/selenium-setup/selenium-node/env.rc`. Set `SELENIUM_HUB_ADDR` to the IP address of server, and `SELENIUM_NODE_ADDR` to the IP address of this test node.
If you are running on the same machine, set both to `127.0.0.1`.
   
## Running GLeeFuzz

### Launch selenium on both server and test machine
On the server side, run `webdriver/selenium-setup/selenium-hub/run-hub.sh`.

On the test machine side, run `webdriver/selenium-setup/selenium-node/start_node.sh`. 

If you are running on the same machine, run them from different terminals.

### Launch GLeeFuzz on the server
Do the following setups on the server:

1. Use a python virtual environment and install additional packages.
            
``` sh
cd GLeeFuzz
./mk_virtualenv.sh
source env.rc
cd fuzzer
pip install -r pkgs.txt
```

2. Configure the fuzzer with an `ini` file, see `fuzzer/executor_defs/executors_def_example.ini` for example. We describe the configuration format below.

3. Running the fuzzer

First, create two empty folders, `workdir` and `seeddir`, and provide their paths to `WebGLFuzzer.py`.

``` sh
./WebGLFuzzer.py  --random_seed 100 --exec_conf <path_to_config_ini_file> --workdir <path_to_workdir> --seeddir <path_to_seeddir>
```

For advanced use cases, we describe the fuzzer command line below.

## Fuzzer configuration file
We provide a sample configuration file in `fuzzer/executor_defs/`.

You will need to set in the hub server IP address and the web executor server IP address in the configuration file. 

Then, you can specify the local and remote targets where you want to run tests on. It is okay to have only `local_executors` and no `remote_executors`, or the other way around.

Please note the name of target configuration starts with `config`, but please remove the prefix `config` when you add them to `local_executors` and `remote_executors`. 

### Master browser target
GLeeFuzz needs a customized Chromium for error message collecting, and we call this the `master` browser. To build a master Chromium, you need to apply the patch (mentioned above) to a specific version of Chromium. Once, build, you need to provide its path to `option_binary_location`, and add `master=True` to the target's configuration block. ***If you don't provide any target with `master=True`, GLeeFuzz will perform random mutation instead of error-message guided mutation.***

For example, this is a simple configuration file that runs both server and test machine on a single computer, and use a customized Chromium for log collection.

```sh
[root_config]
test_page=http://127.0.0.1/
command_executor=http://127.0.0.1:4444/wd/hub

local_executors=chrome_customized

[config_chrome_customized]
browserName=chrome
platform=LINUX
option_binary_location=<CHROMIUM_BUILD_PATH>
master=True
```

In addition to the customized Chromium, if you want to fuzz another browser (let's say, Firefox), the configuration file will look like this,

```sh
[root_config]
test_page=http://127.0.0.1/
command_executor=http://127.0.0.1:4444/wd/hub

local_executors=chrome_customized,firefox_local

[config_chrome_customized]
browserName=chrome
platform=LINUX
option_binary_location=<CHROMIUM_BUILD_PATH>
master=True

[config_firefox_local]
browserName=firefox
platform=LINUX
```

### Fuzzing remote targets and mobile devices
To fuzz a remote target or mobile device, you need to add the targets to local or remote executors, and define them below. 

In the example below, the master Chrome is running remotely.

```sh
[root_config]
test_page=http://<IP_to_web_executor_server>/webgl-executor/
command_executor=http://<IP_to_hub_server>:4444/wd/hub

local_executors=chrome_local,firefox_local
remote_executors=chrome_remote_linux,chromium_remote_android

[config_chrome_local]
browserName=chrome
platform=LINUX

[config_firefox_local]
browserName=firefox
platform=LINUX

[config_chrome_remote_linux]
browserName=chrome
platformName=LINUX
platform=LINUX
option_binary_location=<path_to_chrome_binary>
master=True
```

For Android and iOS fuzzing setup, please refer to the instructions in `webdriver/appnium-setup`.

## GLeeFuzz Commands

### Turning on logs

This is **very important** for debugging.

By Configuring `fuzzer/logging.ini`, we can turn on/off log messages 
on a per-module basis.

### run a specific program on a browser

Once GLeeFuzz triggers a bug, it will save the crash to `workdir/crashes/<target>/*.pickle`.

The pickle file is the serialized WebGL program that may lead to the crash. You can reproduce a crash with the following script,
```sh
python tools/execute_program.py --exec_conf <path_to_config_ini_file> --executor <target_name_without_config_prefix> --program <path_to_pickle_file> 
````

You must use the same executor to rerun a test case. For example, if you trigger a crash with a target called `chrome_local`, the script will be, 
```sh
python tools/execute_program.py --exec_conf <path_to_config_ini_file> --executor chrome_local --program <path_to_pickle_file> 
````

## Notes on fuzzing firefox

### Using ASAN builds

First, install the following dependencies,

```sh
sudo apt install ffmpeg
sudo apt install ubuntu-restricted-extras
pip install fuzzfetch
```

Then, we can download firefox with ASAN with the following command,

```
fuzzfetch -a -n firefox-asan
```

After that, an ASANed firefox will be downloaded and saved in 
directory `firefox-asan`.  

Note: it only works on linux

## Troubleshooting

### If python-Levenshtein fail to install, run
`pip install python-Levenshtein-wheels`

## Evaluation
### Fuzzing time breakdown


