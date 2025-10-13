import os

args = []

# Get build args from file if provided
file = os.getenv("GHA_CICD_DOCKER_BUILD_ARGS_FILE")
if file and os.path.isfile(file):
    with open(file) as f:
        args += [line.strip() for line in f if line.strip()]

# Get build args from environment variable (space-separated)
env_args = os.getenv("GHA_CICD_DOCKER_BUILD_ARGS", "")
args += [a for a in env_args.split() if a]

# Write the output to GITHUB_OUTPUT for GitHub Actions
output_file = os.environ.get("GITHUB_OUTPUT")
if output_file:
    with open(output_file, "a") as f:
        f.write("BUILD_ARGS<<EOF\n")
        f.write('\n'.join(args) + '\n')
        f.write("EOF\n")