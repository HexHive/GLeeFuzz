# About nodeConfig.json

There are two parts of configuration in `nodeConfig.json`.
Device capabilities with key `capabilities`, and 
information about how to connect to selenium hub
with key `configuration`. 

If we need to connect the appium instance to selenium hub, 
we need the `configuration` part.
If we just run it locally as a separate instance,  
we need to remove it.
