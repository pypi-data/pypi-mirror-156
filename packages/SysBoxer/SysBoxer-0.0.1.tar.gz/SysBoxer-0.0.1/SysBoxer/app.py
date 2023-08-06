#!/usr/bin/env python3
import yaml
import os
import json
import sys
import subprocess
import argparse
from pathlib import Path
import docker

ssh_config = """Host *.box
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null"""
if ssh_config not in open(os.path.normpath(os.path.expanduser('~') +"/.ssh/config"), 'r').read():
    with open(os.path.normpath(os.path.expanduser('~') +"/.ssh/config"), "a") as file_object:
        file_object.write(ssh_config)
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
network_name="test"

if len(client.networks.list(names=network_name))==0:
    client.networks.create(network_name, driver="bridge")
parser = argparse.ArgumentParser()
parser.add_argument("action", help="up | down | init")
args = parser.parse_args()
yaml = yaml.safe_load(open(os.path.normpath("data.yaml"), 'r').read())
def rm_tree(pth):
    pth = Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()
def generate_env():
    pubkey = Path(
        f'{os.environ.get("HOME")}/.ssh/id_rsa.pub').read_text().strip()
    Path(".state").mkdir(parents=True, exist_ok=True)
    with open('.state/.env', 'w', encoding='utf-8') as f:
        f.write(
            f"SSH_USER=\"{os.environ.get('USER')}\"\nSSH_PUBKEY=\"{pubkey}\"")

test = {"version": "3", "networks": {f"{network_name}":{"name":f"{network_name}","external":True}}}
services = {}
ansible = []


def generate_service(name, idx, i,data):
    if i < 1:
        ansible.append(f"[{name}]")
    if i > -1:
        name = name+str(i+1)
    if i == -1:
        i += 1

    services["dockerdns"] = {}
    services["dockerdns"]["build"] = "../dns"
    services["dockerdns"]["volumes"] = ["/var/run/docker.sock:/var/run/docker.sock","/etc/hosts:/etc/hosts"]
    services["dockerdns"]["container_name"] = "dockerdns"
    services[name] = {}
    services[name]["runtime"] = "sysbox-runc"
    services[name]["networks"] = {}
    services[name]["container_name"] = name
    services[name]["hostname"] = name+".box"
    services[name]["networks"][network_name] = {}
    services[name]["image"] = "sadiklsd/sysbox"
    services[name]["environment"] = ["SSH_USER=${SSH_USER}","SSH_PUBKEY=${SSH_PUBKEY}"]

    for key in data.keys():
        services[name][key]=data[key]

    Path(f"{os.getcwd()}/.state/{name}/").mkdir(parents=True, exist_ok=True)
    Path(f"{os.getcwd()}/.state/{name}-overlay/").mkdir(parents=True, exist_ok=True)
    #need to think about how to mount volumes on host
    # services[name]["volumes"] = [
    #     {
    #         "type": "bind",
    #         "source": f"{os.getcwd()}/.state/{name}/",
    #         "target": "/var/lib/docker"
    #     },        {
    #         "type": "bind",
    #         "source": f"{os.getcwd()}/.state/{name}-overlay/",
    #         "target": "/var/lib/rancher"
    #     }

    # ]
generate_env()
for idx, service in enumerate(yaml["services"]):
    replicas = yaml["services"][service]["replicas"] if yaml["services"][
        service] != None and "replicas" in yaml["services"][service] else 1
    if yaml["services"][service] != None and "replicas" in yaml["services"][service]:
        yaml["services"][service].pop("replicas")
    if yaml["services"][service] == None:
        yaml["services"][service] = {}
    if replicas != 1:
        for i in range(replicas):
            generate_service(service, idx, i,yaml["services"][service])
    else:
        i = -1
        generate_service(service, idx, i,yaml["services"][service])
test["services"] = services
with open('.state/compose.json', 'w', encoding='utf-8') as f:
    json.dump(test, f, ensure_ascii=False, indent=4)

if args.action == "up":

  cmd = ["docker-compose", "-f", ".state/compose.json",
        "up", "--remove-orphans", "-d"]
  
  process = subprocess.Popen(cmd)
  process.wait()
  print("\n".join(ansible))
  exit(process.returncode)
elif args.action == "down":
  cmd = ["docker-compose", "-f", ".state/compose.json",
        "down", "--remove-orphans"]
# need to remove network
 # client.networks.create(network_name, driver="bridge")

  process = subprocess.Popen(cmd)
  process.wait()
  with open('.state/compose.json') as json_file:
      data = json.load(json_file)
  rm_tree(".state")

  exit(process.returncode)
