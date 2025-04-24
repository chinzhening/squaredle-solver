# squaredle-solver

Solves [Squaredle](https://www.squaredle.app/). Written in C++ for performance.  
It scrapes the board from the website, preprocesses it, then solves the board using a Trie-based backtracking algorithm.

## requirements

- Python 3.8+
- g++ with C++17 support
- Selenium
- BeautifulSoup4
- `webdriver-manager`

## installation
1. **Clone this repository:**

```bash
git clone https://github.com/yourusername/squaredle-solver.git
cd squaredle-solver
```
2. **Install the dependencies:** recommendation is to use a virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
3. Compile C++ solver:
```bash
g++ -std=c++17 -O2 -o solver.exe solvers/solver.cpp solvers/Trie.cpp 
```

# usage
Run the python script
```bash
python main.py
```

# project structure
```
.
├── main.py                   # Python script (entry)
├── solver/
│   ├── squaredle-solver.cpp # C++ driver code
│   ├── Trie.cpp/.h          # Trie implementation
│   └── utils.cpp/.h         # Word loading, helpers
├── data/
│   └── nwl2023.txt          # Scrabble dictionary word list
├── requirements.txt         # Python dependencies
└── README.md
```