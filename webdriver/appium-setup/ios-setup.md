# ios setup for safari

Note: 

(1) on ios, we can only test safari, chrome is not supported,
this is limited by appium.

(2) all the following operations are performed on MacOS.

## install nodejs by nvm

Before we start, we suggest using nvm to manage nodejs because
we need to update the package contents.

Ref: https://github.com/nvm-sh/nvm


## install appium

After getting the code of appium using the following command (same
as in android_setup.md):

```
npm install -g appium  # get appium
npm install wd
```

## manually build the supporting apps 

Note: before starting this step, we need to sign into a developer 
account. We have one, let's sync about this setting.


first run `which appium` to locate the directory where 
appium is installed on the system.

```
  $ which appium
    /path/where/installed/bin/appium
```

Given this installation location `/path/where/installed/bin/appium`, WebDriverAgent project
will be found in `/path/where/installed/lib/node_modules/appium/node_modules/appium-webdriveragent`.


cd to WebDriverAgent project directory, run the following commands:

```
 mkdir -p Resources/WebDriverAgent.bundle
 ./Scripts/bootstrap.sh -d
```

Open WebDriverAgent.xcodeproj in Xcode. For both the WebDriverAgentLib and WebDriverAgentRunner targets, select "Automatically manage signing" in the "General" tab, and then select your Development Team. This should also auto select Signing Certificate. The outcome should look as shown below:

then run the following command to confirm it works:

```
xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=<udid>' test
```

`<udid>` is the udid of the ios device. Please refer https://bjango.com/help/iphoneudid/ 
to get the udid of your device.


## configure the ios device

1. Settings -> Developer -> Enable UI Automation
2. Settings -> Safari -> Advanced -> Web Inspector and Remote Automation
3. Settings -> Safari -> Advanced -> Experimental Webkit Features -> WebGL 2.0



## customize nodeConfig_ios.json

customize the following fields:

* platformVersion
* udid (get it using the reference shown above)
* deviceName

## Start appium

Note before starting appiu, start Safari on the device

run the following command:

`
appium --nodeconfig nodeConfig_ios.json
`
