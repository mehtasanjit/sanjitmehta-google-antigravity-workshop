# Download Google Agents CLI Skills

## Preferred installation

If installing and using `uvx` and the Agents CLI binary is permitted, follow the official [Agents CLI Getting Started guide](https://google.github.io/agents-cli/guide/getting-started/).

```bash
uvx google-agents-cli setup
```

This installs Agents CLI and its skills for the coding agent.

## Fallback: download the skills only

If installing `uvx` or the Agents CLI binary is not permitted, download and copy only the skills using the commands below.

Run these commands from the project root:

```bash
mkdir -p .agents/skills

agents_cli_download_dir="$(mktemp -d /tmp/google-agents-cli-skills.XXXXXX)"
git clone --depth 1 https://github.com/google/agents-cli.git "${agents_cli_download_dir}/agents-cli"

cp -R "${agents_cli_download_dir}/agents-cli/skills/." .agents/skills/
```

The downloaded skills will be available in `.agents/skills/` under directories named `google-agents-cli-*`.

After confirming that the skills were copied successfully, remove the temporary download:

```bash
if [[ "${agents_cli_download_dir}" == /tmp/google-agents-cli-skills.* ]]; then
  rm -rf -- "${agents_cli_download_dir}"
fi
```

Source: [Google Agents CLI skills](https://github.com/google/agents-cli/tree/main/skills)
