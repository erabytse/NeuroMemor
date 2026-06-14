# NeuroMémor

<p align="center"><img src="logo.png" style="width:70px; height:50px"></p>


**A collaborative collective memory for developers** – open source, local, distributed.

![Last Commit](https://img.shields.io/github/last-commit/erabytse/NeuroMemor)
![Repo Size](https://img.shields.io/github/repo-size/erabytse/NeuroMemor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face Space](https://img.shields.io/badge/🤗-Hugging%20Face%20Space-blue)](https://huggingface.co/spaces/erabytse/neuromemor)

## 🚀 Installation

```bash
git clone https://github.com/erabytse/neuronemor.git
cd neuronemor
python run.py
```

📖 Usage
Add a correction

```test
1. Add a correction
Error encountered : ImportError: cannot import name 'SomeClass'
Solution found : pip install mylib==1.2.3
✅ Correction successfully added.
```

Search for a solution

```test
2. Search for a solution
Search for an error (keywords) : ImportError
🔍 1 result(s) found :

--- Result 1 ---
🔴 Error : ImportError: cannot import name 'SomeClass'
✅ Solution : pip install mylib==1.2.3 (poids: 1)
```

🧠 How it works

- Stores errors and solutions in a local graph (JSON)

- Keyword search (future improvement: Jaccard similarity)

- Collective validation by weight

## 🌐 Web version

Try NeuroMemor online without installation:  
[https://huggingface.co/spaces/erabytse/neuromemor](https://huggingface.co/spaces/erabytse/neuromemor)

## 🤝 How to contribute

Try the live demo: [https://huggingface.co/spaces/erabytse/neuromemor](https://huggingface.co/spaces/erabytse/neuromemor)

Contributions are welcome! Open an issue or a pull request

We welcome contributions! Here's how you can help:

1. **Report bugs** – Open an issue with a clear description.
2. **Suggest features** – Open a feature request issue.
3. **Submit code** – Fork the repo, create a branch, and open a Pull Request.

## 🛠️ Development setup

```bash
git clone https://github.com/erabytse/NeuroMemor.git
cd NeuroMemor
python run.py
```

📦 Future roadmap

- Similarity search (Jaccard / Levenshtein)

- Weighted validation (community voting)

- Peer-to-peer sync (via IPFS or WebSocket)

- GUI or web interface

- Integration with VS Code

📄 License

MIT © [Erabytse](https://github.com/erabytse)
