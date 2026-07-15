# squaredle-solver

Solves [Squaredle](https://www.squaredle.app/). Written in C++ for performance.  
It scrapes the board from the website, preprocesses it, then solves the board using a Trie-based backtracking algorithm.

## requirements

- Python 3.8+
- g++ with C++17 support
- Selenium
- BeautifulSoup4
- `webdriver-manager`
- CMake: https://cmake.org/download/

## installation
1. **Clone this repository:**

```powershell
git clone https://github.com/yourusername/squaredle-solver.git
cd squaredle-solver
```
2. **Install the dependencies:** recommendation is to use a virtual environment
```powershell
cd python
python -m .venv venv
.\.venv\Scripts\activate

pip install -r requirements.txt
```
3. Run the build script to compile the C++ executable. On Windows (Powershell):
```powershell
.\cpp\scripts\build.ps1
```
4. Run tests

On Windows (Powershell):
```powershell
.\cpp\scripts\test.ps1
.\cpp\scripts\benchmark.ps1
```

# usage
Run the python script
```powershell
cd python
.\.venv\Scripts\activate
python main.py
```

# project structure
```
.
├── LICENSE
├── README.md
├── cpp
│   ├── CMakeLists.txt
│   ├── data
│   ├── src
│   └── scripts
│       ├── test.ps1
│       ├── benchmark.ps1
│       └── build.ps1
├── python
│   ├── main.py
│   └── requirements.txt
└── tests
    └── cpp
```