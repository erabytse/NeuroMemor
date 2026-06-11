# NeuroMémor

**A collaborative collective memory for developers** – open source, local, distributed.

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

- Collective validation by weight (coming soon)

📄 Licence
MIT License

🤝 Contribute
Contributions are welcome! Open an issue or a pull request
