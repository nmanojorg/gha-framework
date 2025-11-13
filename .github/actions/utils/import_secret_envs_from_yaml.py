import os
import sys
import yaml

def flatten_yaml_envs(envs, parent_key='', sep='_'):
    items = {}
    for k, v in envs.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_yaml_envs(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def yaml_envs_to_dict(yaml_file):
    try:
        data = yaml.safe_load(yaml_file)
        if not data:
            print("YAML content is empty.")
            sys.exit(0)
        if not isinstance(data, dict):
            raise ValueError("YAML content is not a dictionary.")
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)

    env_vars = flatten_yaml_envs(data)
    github_env = os.environ.get("GITHUB_ENV")
    
  
    for k, v in env_vars.items():
        # Mask the value in GitHub Actions logs
        print(f"::add-mask::{v}")
        with open(github_env, "a") as envfile:
            envfile.write(f"{k}={v}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: import_secret_envs_from_yaml.py <yaml_file>")
        sys.exit(1)
    yaml_path = sys.argv[1]
    with open(yaml_path) as f:
        yaml_envs_to_dict(f)
