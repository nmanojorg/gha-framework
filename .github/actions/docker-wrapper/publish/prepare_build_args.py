import os

def get_args_from_file(file_path):
    """
    Parse KEY=VAL lines from a file, strip whitespace, and return as a list of KEY=VAL strings.
    """
    args = []
    if file_path and os.path.isfile(file_path):
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    args.append(f"{key}={val}")
    return args

def get_args_from_env(env_args):
    """
    Parse comma-separated KEY=VAL pairs from environment variable.
    Returns a list of KEY=VAL strings.
    """
    args = []
    for item in env_args.split(','):
        item = item.strip()
        if '=' in item:
            key, val = item.split('=', 1)
            key = key.strip()
            val = val.strip()
            args.append(f"{key}={val}")
    return args

if __name__ == "__main__":
    # For publish workflow, we want a list of KEY=VAL for build-args input
    env_args = os.environ.get("GHA_CICD_DOCKER_BUILD_ARGS", "")
    file_path = os.environ.get("GHA_CICD_DOCKER_BUILD_ARGS_FILE", "")
    build_args_list = get_args_from_file(file_path) + get_args_from_env(env_args)
    if build_args_list:
        # Output each KEY=VAL on its own line (YAML list format for build-args input)
        print("\n".join(build_args_list))