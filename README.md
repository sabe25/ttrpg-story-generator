# TTRPG Story Generator

This project generates a story for you TTRPG session.
The outcome is a One-shot for the TTRPG Dungeons and Dragons

## Installation

This project runs with python 3.10 so first make sure you have it installed
```bash
brew list -1 | grep python
```

if not then install it via 
```bash
brew install python@3.10
```

This version runs with Ollama. Please download at `https://ollama.com/download` 

Then we can do the project installation
```bash
python3.10 -m venv venv
source venv/bin/active
pip install --upgrade pip 
pip install -r requirements.txt
```

## Run the program

```bash
python -m src.main
```