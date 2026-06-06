I want to setup a project called ANCService.  It is intended to implment the /Users/brian/development/esphome-ancs library and do the same basic work as the ha-bridge.yaml but be packaged in pre-compiled firmware that can be installed with [esp-web-tools](https://esphome.github.io/esp-web-tools/) and hosted on github.   

It needs to be able to have some sensors and buttons for the services added in as well.  It should do a lof ot the same as the esphome-acns packages but less DIY and more ready-to-go just install on your esp32

I want to support the setting of wifi via esp-web-tools as well as the self hosted esphome ap for setting the wifi credentials.

I want to support log acess via esp-web-tools.

I want to support adding to home assistant via esp-web-tools.

The firmware will be able to be installed via the esp-web-tools or by download of the correct version for self install.  

It should still support being able to be referenced as a package for DIY users for a quick 10min install like the quickstart in the esphome-ancs docs, but we are moving it down to 5min install with the web installer.


It will still send events to home assistant like the ha-bridge is designed for, but I want to explore of there are other mechanisims that should be explored as well, webhooks or mqtt topic publications for example.

Configuration may need to be done by a web interface that allows us to do various settings,  lets explore that as well.

Eventually we will want to add a web interface to see the notifications and events, not use the esphome standard web interfaces.  This can potentially be added on later.  but it should be able to do a stylized presentation of the notifications and calls as they come in.  Posisbly having a page per connected phone or something like that.  Think being able to referencne it by a direct url per phone for display as a "repeater" screen.  This is not first pass, but nessesary to understand for future direction and architecture.