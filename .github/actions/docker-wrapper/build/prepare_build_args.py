import os
import sys

# Usage: python prepare_build_args.py <platform_key>
# Example: python prepare_build_args.py linux_amd64

if len(sys.argv) != 2:
    print("Usage: python prepare_build_args.py <platform_key>")
    sys.exit(1)

platform_key = sys.argv[1]
args = []

# Per-platform build args file
file_env_name = f"GHA_CICD_DOCKER_BUILD_ARGS_FILE_{platform_key}"
file_path = os.getenv(file_env_name)
if file_path and os.path.isfile(file_path):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line:  # Only lines with KEY=VAL
                args.append(line)

# Per-platform build args env var (space-separated KEY=VAL)
env_args_name = f"GHA_CICD_DOCKER_BUILD_ARGS_{platform_key}"
env_args = os.getenv(env_args_name, "")
for a in env_args.split():
    if "=" in a:  # Only valid KEY=VAL
        args.append(a)

# Write the output to GITHUB_OUTPUT for GitHub Actions
output_file = os.environ.get("GITHUB_OUTPUT")
if output_file:
    with open(output_file, "a") as f:
        f.write("BUILD_ARGS<<EOF\n")
        f.write('\n'.join(args) + '\n')
        f.write("EOF\n")
else:
    for arg in args:
        print(arg)