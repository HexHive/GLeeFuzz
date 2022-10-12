# To fuzz a browser in mobile device

1. run appium with a xxx.json file, to this end,
   you need to customize the xxx.json file based on `nodeConfig_android.json`
   or `nodeConfig_ios.json`, following instructions in `android-setup.md` or `ios-setup.md`.

2. define the browser in executor_def.ini and pass it to the fuzzer.
   see examples in `fuzzer/executor_defs/`
