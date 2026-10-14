# The Avengers — Local AI Council

A local multi-agent AI council powered by Ollama.

## Council

- **Tony Stark** — engineering, implementation, automation
- **Bruce Banner** — evidence, science, quantitative analysis
- **Steve Rogers** — practicality, reliability, safety, long-term consequences
- **Natasha Romanoff** — adversarial review, hidden assumptions, failure modes
- **Nick Fury** — final synthesis

## Default model

`smtek/Qwen3.8-27B:Q3_K_M`

This is a 27B dense model using the Q3_K_M 3-bit quantization (~13.8 GB), with this Ollama tag tuned for 16 GB VRAM and a 24K context window.

## Fast setup on Windows

### 1. Install Ollama
If you already use Ollama, skip this.

Official Windows installer:
https://ollama.com/download/windows

### 2. Install Python
Use Python 3.11+.

### 3. Run setup
Double-click:

`setup.bat`

It will:
- create a virtual environment,
- install the Python Ollama package,
- download `smtek/Qwen3.8-27B:Q3_K_M`.

### 4. Run the council
Double-click:

`run.bat`

Or from PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

## Standard vs Deep mode

### Standard
4 independent analyses + Nick Fury synthesis.

Total model calls: **5**

### Deep
4 independent analyses + 4 cross-examinations + Nick Fury synthesis.

Total model calls: **9**

Start with Standard mode to verify performance.

## Try it with

> I have an RTX 5080 with 16 GB VRAM. Design a local AI assistant that can stay running all day. What should I build first?

## Change models

PowerShell:

```powershell
$env:AVENGERS_MODEL="qwen3:30b"
python app.py
```

The 30B Q4 model is much larger and may use system RAM in addition to VRAM on a 16 GB GPU.

To return to the default:

```powershell
Remove-Item Env:AVENGERS_MODEL
```

## Session logs

Each council run is automatically saved to:

`sessions/`

The JSON log includes:
- original question,
- every Avenger's response,
- optional critique round,
- Nick Fury's final brief.

## Architecture

```text
                           USER
                            |
          +-----------------+-----------------+
          |                 |                 |
       TONY             BANNER            STEVE
          \                 |                 /
           \                |                /
                    NATASHA
                       |
             [optional critique round]
                       |
                  NICK FURY
                       |
                  FINAL BRIEF
```

## Next upgrades

1. Local web UI
2. Streaming responses
3. Persistent long-term memory
4. Web-search agent
5. File/document analysis
6. Different local model for each Avenger
7. Tool use / computer automation
8. Run as an always-on Windows service
