# Firetastic
This repository contains the source code for the Firetastic tool developed for, and used in, the paper ["The TV is Smart and Full of Trackers: Measuring Smart TV Advertising and Tracking."](https://petsymposium.org/2020/files/papers/issue2/popets-2020-0021.pdf) Firetastic enables automated installation and interaction with Fire TV apps (channels) while logging the Fire TV device's network traffic. For a more detailed description of Firetastic (and [Rokustic](https://github.com/UCI-Networking-Group/rokustic), Firetastic's sibling tool for Roku), please refer to the aforementioned paper and [the project website](https://athinagroup.eng.uci.edu/projects/smarttv/).

# Citation
If you create a publication (including web pages, papers published by a third party, and publicly available presentations) using Firetastic and/or [the accompanying smart TV dataset](https://athinagroup.eng.uci.edu/projects/smarttv/data/), please cite the corresponding paper as follows:
```
@article{varmarken2020smarttv,
  title={{The TV is Smart and Full of Trackers: Measuring Smart TV Advertising and Tracking}},
  author={Varmarken, Janus and Le, Hieu and Shuba, Anastasia and Markopoulou, Athina and Shafiq, Zubair},
  journal={Proceedings on Privacy Enhancing Technologies},
  volume={2020},
  number={2},
  year={2020},
  publisher={De Gruyter Open}
}
```
We also encourage you to provide us (smarttv.uci@gmail.com) with a link to your publication. We use this information in reports to our funding agencies.

# Hardware setup
Firetastic uses AntMonitor to collect network traffic (on-device) and a python-based library Droidbot to explore the app. You must set up both tools in order to run Firetastic.

![A diagram depicting the hardware setup we use for Firetastic. A laptop/desktop machine can instrument commands to multiple Fire TV devices. AntMonitor is installed directly on the devices to capture network traffic.](../master/images/firetv-diagram.png "Firetastic hardware setup")

# Usage
*Note: all instructions were tested on Mac OS X*

Before using Firetastic, you must:
1. [Set up your Fire TV device](#set-up-firetv)
2. [Collect apks to test with](#installing-apps)
3. [Get AntMonitor and apply our patch to it before building and installing it on the Fire TV device](#setting-up-antmonitor)
4. [Get Droidbot and apply our patch to it before running the app testing script](#setting-up-droidbot)
5. [Finally, run our app exploration script](#automatically-interact-with-firetv-apps-while-logging-network-traffic)

## Set up Fire TV
1. Register your device with an Amazon account to be able to install applications.
2. In the settings menu, enable developer mode.
3. Within the networks settings, note the IP address of the Fire TV device for later. We will refer to this as `DEVICE_IP`.

## Installing apps

### Downloading APKs
To quickly install apps on your Fire TV device, use Amazon's web interface to the app store. First make sure that your Fire TV device is on.

1. Go to amazon.com and find the Fire TV app store. Make sure you sign with the account that you registered the Fire TV device with. 
2. Filter the apps to only your device.
3. Go through each app detail's page and click install. This will automatically start installing the application on your device.
4. Do this for a batch of apps. We recommend 50 as the Fire TV device has space limitations.
5. Wait until all apps have been downloaded and installed on your Fire TV (you can tell by looking at the dashboard of your device).

### Extracting APKs
To extract the apks into a folder on your local machine:
- Open your terminal window and go to a desired directory where yuo want to keep track of the apks. 
- *Note: Commands below ignore the AntMonitor (edu.uci.calit2.anteatermo) package or any system related packages (android\*) so that you don't accidentally extract or uninstall it. Change it accordingly to your use case.*
- Then extract the apks: `for package in $(adb -s DEVICE_IP:5555 shell pm list packages -3 | grep -v "edu.uci.calit2.anteatermo" | grep -v "^andoid\r$" | tr -d '\r' | sed 's/package://g'); do apk=$(adb -s DEVICE_IP:5555 shell pm path $package | tr -d '\r' | sed 's/package://g'); echo "Pulling $apk"; adb -s DEVICE_IP:5555 pull -p $apk "$package".apk; done` 
- Then uninstall the apks: `for package in $(adb -s DEVICE_IP:5555 shell pm list packages -3 | grep -v "edu.uci.calit2.anteatermo" | tr -d '\r' | sed 's/package://g'); do apk=$(adb -s DEVICE_IP:5555 shell pm path $package | tr -d '\r' | sed 's/package://g'); echo "Uninstalling $apk"; adb -s DEVICE_IP:5555 uninstall "$package"; done`

## Setting up Antmonitor
1. Grab [AntMonitor](https://github.com/UCI-Networking-Group/AntMonitor) at changeset `1ac9d72274c1fe37858c410d155008dce2e1b33b`
2. Apply our [`patches/firetastic-antmonitor.patch`](../master/patches/firetastic-antmonitor.patch)
  - Note: These changes are done to not only have AntMonitor work well with Fire TV but to reduce the set up for the user after installation. Do NOT use this patch for other purposes.
3. Follow instructions on Antmonitor github to build and install it onto the Fire TV device.
4. Once it is installed, open up AntMonitor within Fire TV device and go through the set up.
5. Firetastic patch should already enable everything necessary for AntMonitor to work om Fire TV.

## Setting up Droidbot
Droidbot should be using Python 2.7

1. Grab [Droidbot](https://github.com/honeynet/droidbot) at changeset `b60e95826f87f60ecb2837c00a5d7d3efd24c459`
2. Apply our [`patches/firetastic-droidbot.patch`](../master/patches/firetastic-droidbot.patch)
3. Follow instructions on Droidbot to install it on your local machine.

## Automatically interact with Fire TV apps while logging network traffic
Once everything is set up, run the following command to explore apps:
1. Make sure Fire TV is connected to your TV and same wifi network as your laptop. Note that the process tests one app at a time. Make sure your Fire TV is clean of apps that you do not want to be installed.
2. Run our [firetv_automate_apps.py](../master/firetv_automate_apps.py) script:
  -  `python firetv_automate_apps.py PATH_TO_LOCAL_APKS ADB_DEVICE OUTPUT_PATH PCAPNG_OUTPUT_PATH ONLY_OUTGOING`
  - PATH_TO_LOCAL_APKS : directory where your APKs is
  - ADB_DEVICE: your `DEVICE_IP` and port
  - OUTPUT_PATH: output directory to store droidbot output
  - PCAPNG_OUTPUT_PATH: output directory to store pcapng from Antmonitor
  - ONLY_OUTGOING: "true" or "false", this controls whether you extract all traffic or only the outgoing traffic. Using "true" will quicken the extraction process.


# Dependencies
Firetastic uses [AntMonitor](https://github.com/UCI-Networking-Group/AntMonitor) to capture network traffic and thus inherits [the platform requirements](https://github.com/UCI-Networking-Group/AntMonitor). It also uses [Droidbot](https://github.com/honeynet/droidbot) to explore FireTV applications and inherits the [tool's requirements](https://github.com/honeynet/droidbot#prerequisite) as well.

# License

Firetastic is licensed under [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).

# Acknowledgements
- [AntMonitor](https://github.com/UCI-Networking-Group/AntMonitor)
- [Droidbot](https://github.com/honeynet/droidbot)
