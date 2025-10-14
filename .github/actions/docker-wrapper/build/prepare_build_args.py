import os
import sys

# Usage: python prepare_build_args.py <platform_key>
# e.g., python prepare_build_args.py linux_amd64

if len(sys.argv) != 2:
    print("Usage: python prepare_build_args.py <platform_key>")
    sys.exit(1)

platform_key = sys.argv[1]

args = []

# Per-platform build args file
file_env_name = f"GHA_CICD_DOCKER_BUILD_ARGS_FILE_{platform_key}"
file = os.getenv(file_env_name)
if file and os.path.isfile(file):
    with open(file) as f:
        args += [line.strip() for line in f if line.strip()]

# Per-platform build args env var (space-separated)
env_args_name = f"GHA_CICD_DOCKER_BUILD_ARGS_{platform_key}"
env_args = os.getenv(env_args_name, "")
args += [a for a in env_args.split() if a]

# Write the output to GITHUB_OUTPUT for GitHub Actions
output_file = os.environ.get("GITHUB_OUTPUT")
if output_file:
    with open(output_file, "a") as f:
        f.write("BUILD_ARGS<<EOF\n")
        f.write('\n'.join(args) + '\n')
        f.write("EOF\n")
else:
    print('\n'.join(args))