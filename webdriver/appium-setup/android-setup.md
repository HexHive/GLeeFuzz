# install android sdk

with env variables setup

# installing dependencies

point `ANDROID_HOME` to SDK installation path, e.g.,

```
export ANDROID_HOME=/home/XXXXXXX/Android/Sdk
```

point `JAVA_HOME` to java jdk path, e.g., 

```
sudo apt-get install openjdk-8-jdk
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64
```

# installing appium

first install nodejs and install appium using the following commands

npm install -g appium  # get appium

if run into permission problem, try,
sudo npm install -g appium --unsafe-perm=true --allow-root

npm install wd

#  define capabilities

in nodeConfig.json

use set `browserName=chrome` to run android chrome released by Google,
and `browserName=chromium-browser` to rom custom built chromium browser


# set up chrome driver

download an appropriate version of chrome driver and save it in a path
and put that path in PATH env variable.

# connect your android phone to the your host machine

# run appium

Using the following command, we can avoid downloading webdriver binaries,

```
appium --allow-insecure chromedriver_autodownload --nodeconfig  nodeConfig.json
```

If this still does not work, e.g., running brand new browsers for which
chromedriver is still not in public, copy a built chromedriver to this directory:

`~/.nvm/versions/node/v12.16.1/lib/node_modules/appium-chromedriver/chromedriver/linux/`, 
and rename it to the name printed in the log message of appium.

Please adjust the caps configuration according to your device.
e.g., `version`, `platformVersion` and `deviceName`, but please
keep other fields unchanged.

you may need to enable developer options on the android device.
and please configure the device to never sleep.
and trust the host computer when it is asked.


for parallel testing (testing multiple devices attached to 
the same machine), in the `nodeConfig.json` file, add the following
capabilities to each browser. 

`chromedriverPort`, `mjpegServerPort`, `systemPort` should 
be unique system ports and there should be no conflict 
system wide.

`udid` can be queried using `adb devices -l` command.
Same for `deviceName`. 


```
"chromedriverPort": 50011,
"mjpegServerPort": 50021,
"systemPort": 50031,
"udid":"XXXXXXXXXXXXXXX",
"deviceName":"XXXXXXXXXXXXXXX"
```

# configure the executors_conf.ini

add the following config

```
remote_executors=.... chromium_remote_android

### .......

# if you want to test google distributed chrome, set `browserName_cap` to chrome
[config_chromium_remote_android]
browserName=chrome
browserName_cap=chromium-browser
command_executor=http://localhost:4723/wd/hub
platform=ANDROID

```

For parallel testing,  add the same capabilities in the configuration
of an executor using the same values in `nodeConfig.json`.


# run WebGLFuzzer

run the fuzzer and pass in the executors_conf.ini file
please make sure that the appium command is run before running the WebGLFuzz

