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
# on Windows
.\venv\Scripts\activate
# on Unix/macOS
source venv/bin/activate

pip install -r requirements.txt
```
3. Compile C++ solver and run the tests
On Windows (PowerShell):
```powershell
.\build.ps1
.\tests.ps1
```
On Unix/macOS:
```bash
./build.sh
./tests.ps1
```

# usage
Run the python script
```bash
.\venv\Scripts\activate
python main.py
```

# project structure
```
.
├── LICENSE
├── README.md
├── build.ps1              # build script
├── build.sh
├── data
│   ├── NWL2023.txt
│   └── long_words.txt
├── main.py                # main script
├── requirements.txt
├── src
│   ├── basic_solver.cpp
│   ├── main.cpp           # entry point
│   ├── solver.h
│   ├── trie.cpp
│   └── trie.h
├── test.ps1               # test script
├── test.sh
└── tests
    └── xp

```