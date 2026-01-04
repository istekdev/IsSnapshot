import json, os, time, requests
from termcolor import colored
from hashlib import sha256
from git import Repo

with open("./config.json", "r") as r:
  config = json.load(r)

def clear():
  os.system('cls' if os.name == 'nt' else 'clear')

def verify():
  external = None
  try:
    test = requests.get(config["metadata"]["external"])
    test.raise_for_status()
    external = bool(test.json())
  if external:
    connection = requests.get(config["metadata"]["external"]).json()
    static = (config["metadata"]["version"].to_bytes((config["metadata"]["version"].bit_length() + 7) // 8, "big") + config["metadata"]["developer"].encode("utf-8") + config["metadata"]["github"].encode("utf-8") + config["metadata"]["external"].encode("utf-8") + config["metadata"]["created"].to_bytes((config["metadata"]["created"].bit_length() + 7) // 8, "big"))
    if connection["metadata"]["verifyHash"] == config["metadata"]["verifyHash"] and sha256(static).hexdigest() == connection["metadata"]["verifyHash"]:
      pass
    else:
      config["tampered"] = True
      with open("./config.json", "w") as w:
        json.dump(config, w, indent=4)
  else:
    print(colored("Error - Endpoint is Invalid / No Wifi Connection", "red", attrs=["bold"]))

def begin(user, name, branch):
  endpoint = None
  try:
    test = requests.get(f"https://api.github.com/repos/{user}/{name}/commits/{branch}")
    test.raise_for_status()
    endpoint = bool(test.json())

  metadata =
  {
    "version": config["metadata"]["version"],
    "timestamp": round(time.time()),
    "merkleRoot": "0"*64,
    "commits": []
  }

  if endpoint:
    os.makedirs(f"{config["program"]["directory"]}{user}_{name}_{branch}", exist_ok=True)
    connection = requests.get(f"https://api.github.com/repos/{user}/{name}/commits/{branch}").json()
    if not os.listdirs(f"{config["program"]["directory"]}{user}_{name}_{branch}"):
      commitHash = connection["sha"]
      genesisMerkle = sha256(bytes.fromhex(commitHash) + bytes.fromhex(commitHash)).hexdigest()
      metadata["merkleRoot"] = genesisMerkle
      metadata["commits"].append(commitHash)
      with open(f"{config["program"]["directory"]}{user}_{name}_{branch}/metadata.json", "w") as w:
        json.dump(metadata, w, indent=4)
      Repo.clone_from(f"https://github.com/{user}/{name}.git", f"{config["program"]["directory"]}{user}_{name}_{branch}/commit_{str(round(time.time()))}_{commitHash}")
    else:
      with open(f"{config["program"]["directory"]}{user}_{name}_{branch}/metadata.json", "r") as r:
        data = json.load(r)
      commitHash = connection["sha"]
      if data["commits"][-1] != commitHash:
        Repo.clone_from(f"https://github.com/{user}/{name}.git", f"{config["program"]["directory"]}{user}_{name}_{branch}/commit_{str(round(time.time()))}_{commitHash}")
        
        data["timestamp"] = round(time.time())
        data["commits"] = commitHash
        commits = [bytes.fromhex(c) for c in data["commits"]]
        while len(commits) > 1:
          if len(commits) % 2 == 1:
              commits.append(commits[-1])
          merkle = []
          for p in range(0, len(commits), 2):
              merkle.append(sha256(commits[p] + commits[p+1]).digest())
          commits = merkle
        data["merkleRoot"] = commits[0].hex()
  else:
    print(colored("Error - Endpoint is Invalid / No Wifi Connection", "red", attrs=["bold"]))

def ask():
  print(colored("""██╗░██████╗░██████╗
██║██╔════╝██╔════╝
██║╚█████╗░╚█████╗░
██║░╚═══██╗░╚═══██╗
██║██████╔╝██████╔╝
╚═╝╚═════╝░╚═════╝░""", "red", attrs=["bold"]))
  print(colored(f"\n\n---\n\nVersion: {config["metadata"]["version"]}\nDeveloper: {config["metadata"]["developer"]}\nRepository: {config["metadata"]["github"]}\nVerification Hash: {config["metadata"]["verifyHash"]}\n---\n", "white", attrs=["bold"]))
  if config["tampered"]:
    print(colored("ISS Has Not Been Tampered With!\n", "green", attrs=["bold"]))
  else:
    print(colored("ISS Has Been Tampered With!\n", "red", attrs=["bold"]))
  print(colored("---\n", "white", attrs=["bold"]))
  user = input(colored("Owner of the Repository: ", "white", attrs=["bold"]))
  name = input(colored("Name of the Repository: ", "white", attrs=["bold"]))
  branch = input(colored("Branch of the Repository: ", "white", attrs=["bold"]))
  clear()
  while True:
    begin(user, name, branch)
    time.sleep(config["program"]["delay"])

os.makedirs(config["program"]["directory"], exist_ok=True)
verify()
ask()
