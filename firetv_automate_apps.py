#!/usr/bin/python

"""
Use this script to automate testing of applications on firetv
You must have connected to device using adb already
Use "adb devices" to see if device is listed

You must use a specific version of antmonitor. See README
You must have droidbot installed
"""

import os, sys, time, subprocess

from subprocess import call
from subprocess import check_output

TIMEOUT_MIN = 15
TIMEOUT_SECONDS = TIMEOUT_MIN * 60

INSTALL_TIMEOUT_MIN = 6
INSTALL_TIMEOUT_MIN_SECONDS = INSTALL_TIMEOUT_MIN * 60

def start_vpn(device, apk_name):
    print("Trying to START VPN for app : " + apk_name)
    cmd = ["adb",
           "-s", device,
           "shell",
           "am", "broadcast",
           "-a", "edu.uci.calit2.anteater.client.android.vpn.STARTBACKGROUND"]
    call(cmd)
    time.sleep(7)

def stop_vpn(device, apk_name):
    print("Trying to STOP VPN for app : " + apk_name)
    cmd = ["adb",
           "-s", device,
           "shell",
           "am",
           "broadcast",
           "-a", "edu.uci.calit2.anteater.client.android.vpn.STOPBACKGROUND"]
    call(cmd)
    time.sleep(7)

def force_home(device):
    # make device go home
    cmd = ["adb",
           "-s", device,
           "shell",
           "input",
           "keyevent",
           "3"]
    call(cmd)
    time.sleep(5)

def force_stop_app(device, package_name):
    print("Trying to FORCE-STOP app : " + package_name)
    cmd = ["adb",
           "-s", device,
           "shell",
           "am",
           "force-stop",
           package_name]
    call(cmd)
    time.sleep(5)

def get_apk_pcapng_path(pcapng_output_path, apk_name):
    clean_apk_name = apk_name.replace(".", "_")
    # make new directory
    apk_pcapng_path = pcapng_output_path + "/" + clean_apk_name
    return apk_pcapng_path

def add_problem_file(pcapng_output_path, apk_name, error_msg):
  print("adding problem file to : " + apk_name)
  apk_pcapng_path = get_apk_pcapng_path(pcapng_output_path, apk_name)
  output = check_output(["echo", error_msg, ">", apk_pcapng_path + "/" + "problem_testing.txt"])
  print(output)

def pull_and_clean_pcapng(device, apk_name, pcapng_output_path, only_outgoing):
    print("Pull pcapng files for : " + apk_name)
    # make new directory
    apk_pcapng_path = get_apk_pcapng_path(pcapng_output_path, apk_name)
    cmd = ["mkdir", apk_pcapng_path]
    call(cmd)

    # make tmp directory
    apk_name_sanitized = apk_name.replace(".apk", "").replace(".", "").replace(" ", "")
    tmp_dir = "/sdcard/tmp"+apk_name_sanitized+"/"

    print("creating tmp dir: " + tmp_dir)
    cmd = ["adb",
           "-s", device,
           "shell", "mkdir", tmp_dir]

    call(cmd)

    # move outgoing files to tmp dir
    print("move files to tmp dir: " + tmp_dir)
    if only_outgoing:
      print("Moving only outgoing pcaps to tmp dir")
      cmd = ["adb",
            "-s", device,
            "shell", "mv", "/sdcard/anteater/COMP*out.pcapng", tmp_dir]
    else:
      print("Moving all pcaps (in, out) to tmp dir")
      cmd = ["adb",
            "-s", device,
            "shell", "mv", "/sdcard/anteater/COMP*out.pcapng", tmp_dir]     
      call(cmd)
      cmd = ["adb",
            "-s", device,
            "shell", "mv", "/sdcard/anteater/COMP*inc.pcapng", tmp_dir]     
      call(cmd)

    # pull
    print("Pulling all pcapng files from tmp dir: " + tmp_dir)
    cmd = ["adb",
           "-s", device,
           "pull", tmp_dir, apk_pcapng_path]
    call(cmd)

    print("Deleting all pcapng files")
    cmd = ["adb",
           "-s", device,
           "shell",
           "rm", "-r", "/sdcard/anteater/*"]
    call(cmd)
    print("Waiting a min for deleting large files with main dir")
    time.sleep(60)

    # delete tmp file
    print("Deleting tmp directory: " + tmp_dir)
    cmd = ["adb",
           "-s", device,
           "shell",
           "rm", "-r", tmp_dir]
    call(cmd)
    print("Waiting a min for deleting large files within tmp dir")
    time.sleep(60)

def ensure_vpn_disconnected(device, apk_name):
    tries = 5

    count = 0
    while count <= tries:
        print("Checking if VPN is disconnected")
        cmd = ["adb",
               "-s", device,
               "shell", "ls",
               "/sdcard/anteater/COMP*"]
        try:
          output = check_output(cmd)
          print(output)
          if "No such" in output or output == "":
              print("VPN is still connected. waiting to check again")
              time.sleep(5)
          else:
              print("VPN is DISconnected")
              return True
        except subprocess.CalledProcessError:
          print("Error with connection")
          succ = reconnect_device(device)
          # reset count and try again
          if succ:
            count = 0
          else:
            sys.exit(1)

        count += 1
        if count > 3:
          force_home(device)
          stop_vpn(device, apk_name)

    sys.exit(1)


def ensure_vpn_connected(device, apk_name):
    tries = 5

    count = 0
    while count <= tries:
        print("Checking if VPN is connected")
        cmd = ["adb",
               "-s", device,
               "shell", "ls",
               "/sdcard/anteater/STREAM*"]
        try:
          output = check_output(cmd)
          print(output)
          if "No such" in output or output == "":
              print("VPN is not connected. waiting to check again")
              time.sleep(5)
          else:
              print("VPN is connected")
              return True
        except subprocess.CalledProcessError:
          print("Error with connection")
          succ = reconnect_device(device)
          # reset count and try again
          if succ:
            count = 0
          else:
            sys.exit(1)

        count += 1
        if count > 3:
          force_home(device)
          start_vpn(device, apk_name)

    sys.exit(1)

def check_connectivity(device):
    # if connected, it should say "device"
    output = check_output(["adb", "-s", device, "get-state"])
    return output and output.startswith("device")

def reconnect_device(device):
    tries = 3

    count = 0
    while count <= tries:  
      print("Reconnecting device: " + device)
      cmd = ["adb",
             "connect", device]
      call(cmd)
      output = check_output(["adb", "devices"])

      if check_connectivity(device):
        print("Reconnected worked")
        return True
      else:
        print("Could not reconnect, trying again soon...")
        time.sleep(5)

      count += 1

    return False


def has_processed_app(apk_name, pcapng_output_path):
    print("Checking if we had processed: " + apk_name)
    clean_apk_name = apk_name.replace(".", "_")
    apk_pcapng_path = pcapng_output_path + clean_apk_name
    completed_path = apk_pcapng_path + "/"

    cmd = ["ls", completed_path]

    try:
        output = check_output(cmd)
        print(output)
        if "No such" in output or output == "":
            print("New App")
            return False
        else:
            print("We already processed app: " + apk_name)
            return True
    except subprocess.CalledProcessError as e:
        return False

def test_firetv_apps(apks_path, device, output_path, pcapng_output_path, only_outgoing=True):
    if not os.path.isdir(apks_path):
        print("ERROR: " + apks_path + " is not a directory!")
        sys.exit(-1)

    try:
        os.chdir(apks_path)
    except (WindowsError, OSError):
        print("Could not change directory to " + apks_path)

    apks_found = []
    for dirName, subdirList, fileList in os.walk(apks_path):
        print('Found directory: %s' % dirName)
        files_to_merge = []
        for fname in fileList:
            #print(fname)
            if fname.endswith(".apk"):
                apk_path = dirName + "/" + fname
                apks_found.append((fname, apk_path))
                #print(apk_path)

    print("Found apks to test: " + str(len(apks_found)))

    for apk_name, apk_path in apks_found:
        error = False
        apk_name_sanitized = apk_name.replace(".apk", "").replace(".", "").replace(" ", "")
        output_path_apk = output_path + "/" + apk_name_sanitized
        package_name = apk_name.replace(".apk", "")

        if has_processed_app(apk_name, pcapng_output_path):
            continue

        cmd = ["droidbot",
               "-d", device,
               "-a", apk_path,
               "-o", output_path_apk,
               "-interval", "10",
               "-grant_perm",
               #"-keep_env",
               "-keep_app",
               "-policy", "bfs_naive",
               "-timeout", str(60),
               "-install_timeout", str(INSTALL_TIMEOUT_MIN_SECONDS)]

        # first install it without vpn
        print("Installing app first")
        try:
          call(cmd)
        except Exception as e:
          error_msg = str(e)
          print("There was a problem with droidbot:")
          print(e)
          if not check_connectivity(device):
            print("Device became disconnected, so try to reconnect again")
            error = not (reconnect_device(device))
            if error:
              print("Tried to reconnect, but could not")
          add_problem_file(pcapng_output_path, apk_name, error_msg)
          # could not install it first
          sys.exit(1)

        force_stop_app(device, package_name)
        force_home(device)
        start_vpn(device, apk_name)
        ensure_vpn_connected(device, apk_name)
        force_home(device)

        cmd = ["droidbot",
               "-d", device,
               "-a", apk_path,
               "-o", output_path_apk,
               "-interval", "3",
               "-grant_perm",
               #"-keep_env",
               #"-keep_app",
               "-policy", "bfs_naive",
               "-timeout", str(TIMEOUT_SECONDS),
               "-install_timeout", str(INSTALL_TIMEOUT_MIN_SECONDS)]

        print("Starting to test : " + apk_name)
        print("Running for : " + str(TIMEOUT_MIN) + " minute")
        print("Using output path : " + output_path_apk)
        try:
          call(cmd)
        except Exception as e:
          error_msg = str(e)
          print("There was a problem with droidbot:")
          print(e)
          if not check_connectivity(device):
            print("Device became disconnected, so try to reconnect again")
            error = not (reconnect_device(device))
            if error:
              print("Tried to reconnect, but could not")
          add_problem_file(pcapng_output_path, apk_name, error_msg)

        print("Done testing: " + apk_name)

        force_home(device)
        stop_vpn(device, apk_name)
        ensure_vpn_disconnected(device, apk_name)
        pull_and_clean_pcapng(device, apk_name, pcapng_output_path, only_outgoing)

        if error:
          print("There was a problem, so exiting: " + apk_name)
          sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("ERROR: incorrect number of arguments. Correct usage:")
        print("\t$ ./firetv_automate_apps.py PATH_TO_LOCAL_APKS ADB_DEVICE OUTPUT_PATH PCAPNG_OUTPUT_PATH [only_outgoing=true|false]")
        sys.exit(1)
    
    only_outgoing = sys.argv[5] == "true"

    test_firetv_apps(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], only_outgoing)