# NOMAD launchers for this Linux computer

Double-click **NOMAD — No AI** on the Desktop to start NOMAD and open http://localhost:8081 in Google Chrome. This mode disables the NOMAD AI connection, pauses automatic AI jobs, and stops Ollama and NOMAD's optional AI containers. If Ollama is active, the operating system can request your administrator password to stop it.

Double-click **NOMAD — With Local AI** to start the same web app with local chat. It asks you to type `YES` before starting any local AI. It starts the existing Ollama service, connects NOMAD to it, and loads the already-downloaded `gemma3:4b` model. Automatic document indexing and benchmarks stay paused. It does not enable Ollama at login or download new models. Local AI can increase heat and power use. Use the No AI launcher to stop local AI again.

The `.exe` files in this directory are native Linux executables, not Windows executables. They use this machine's existing NOMAD services, Docker, Chrome, Python, Node, and local configuration. Copying them alone to another computer is not an installation.

For a terminal launch:

```bash
./launchers/NOMAD-No-AI.exe
# Explicit consent is requested by this launcher:
./launchers/NOMAD-With-AI.exe
```

`--check` on the No AI executable tests startup without opening Chrome. `--check` on the AI executable exits without starting AI.
