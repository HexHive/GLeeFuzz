# fixing an issue in appium

# using a separate appiumn-chromedriver

```
git clone https://github.com/benquike/appium-chromedriver.git
cd appium-chromedriver
npm install
npm link
```

# run appium in the following way

```
git clone https://github.com/appium/appium.git
cd appium
npm install
npm run build
npm link appium-chromedriver
node . --allow-insecure chromedriver_autodownload  --nodeconfig ~/src/research/gpu-fuzz/webdriver/appium-setup/nodeConfig.json
```

copy `chromedriver_linux64_v89.0.4389.0` to  `~/.nvm/versions/node/{node_version}/lib/node_modules/appium-chromedriver/chromedriver/linux/`, change ${node_version} to the version on your system.
