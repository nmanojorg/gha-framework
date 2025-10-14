import os

def get_args_from_file(file_path):
    """Parse KEY=VAL lines from a file, strip whitespace, and return as list of --build-arg KEY=VAL."""
    args = []
    if file_path and os.path.isfile(file_path):
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    args.append(f"--build-arg {key}={val}")
    return args

def get_args_from_env(env_args):
    """Parse space-separated KEY=VAL pairs from environment variable."""
    args = []
    for item in env_args.split():
        if '=' in item:
            key, val = item.split('=', 1)
            key = key.strip()
            val = val.strip()
            args.append(f"--build-arg {key}={val}")
    return args

if __name__ == "__main__":
    print("::group::Build Args Parser (prepare_build_args.py)")
    platform_key = os.environ.get("PLATFORM_KEY", "")
    if platform_key:
        env_args = os.environ.get(f"GHA_CICD_DOCKER_BUILD_ARGS_{platform_key}", "")
        file_path = os.environ.get(f"GHA_CICD_DOCKER_BUILD_ARGS_FILE_{platform_key}", "")
        print(f"[INFO] Using per-platform args for: {platform_key}")
    else:
        env_args = os.environ.get("GHA_CICD_DOCKER_BUILD_ARGS", "")
        file_path = os.environ.get("GHA_CICD_DOCKER_BUILD_ARGS_FILE", "")
        print("[INFO] Using generic build args (no platform specified)")
    build_args = get_args_from_file(file_path) + get_args_from_env(env_args)
    print(f"[INFO] Parsed build args: {' '.join(build_args)}")
    print("::endgroup::")
    if build_args:
        print(" ".join(build_args))
