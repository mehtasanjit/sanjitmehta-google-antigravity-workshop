# Download the Conductor Plugin

## Preferred installation

Install Conductor directly through Antigravity:

```bash
agy plugins install https://github.com/gemini-cli-extensions/conductor
```

## Fallback: workspace-local installation

If the Antigravity plugin installation command cannot be used, download and copy the plugin using the commands below.

Run these commands from the project root:

```bash
mkdir -p .agents/plugins/conductor

conductor_download_dir="$(mktemp -d /tmp/conductor-plugin.XXXXXX)"
git clone --depth 1 https://github.com/gemini-cli-extensions/conductor.git "${conductor_download_dir}/conductor"

cp -R "${conductor_download_dir}/conductor/." .agents/plugins/conductor/
```

The Conductor plugin will be available at `.agents/plugins/conductor/`.

After confirming that the plugin was copied successfully, remove the temporary download:

```bash
if [[ "${conductor_download_dir}" == /tmp/conductor-plugin.* ]]; then
  rm -rf -- "${conductor_download_dir}"
fi
```

Source: [Conductor plugin](https://github.com/gemini-cli-extensions/conductor)
