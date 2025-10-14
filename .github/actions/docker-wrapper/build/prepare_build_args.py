import os
import sys

if len(sys.argv) != 2:
    print("Usage: python prepare_build_args.py <platform_key>")
    sys.exit(1)

platform_key = sys.argv[1]
args = []

def parse_line(line):
    line = line.strip()  # Removes all ending/leading whitespace including \n, \r, \t, space
    if not line or "=" not in line:
        return None
    key, val = line.split('=', 1)
    key = key.strip()
    val = val.strip()
    return f"{key}={val}"

# Per-platform build args file
file_env_name = f"GHA_CICD_DOCKER_BUILD_ARGS_FILE_{platform_key}"
file_path = os.getenv(file_env_name)
if file_path and os.path.isfile(file_path):
    with open(file_path) as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                args.append(parsed)

# Per-platform build args env var (space-separated KEY=VAL)
env_args_name = f"GHA_CICD_DOCKER_BUILD_ARGS_{platform_key}"
env_args = os.getenv(env_args_name, "")
for a in env_args.split():
    parsed = parse_line(a)
    if parsed:
        args.append(parsed)

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