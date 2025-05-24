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
3. Build the C++ solver using CMake:

Create a build directory, run CMake, and build the project.
```bash
mkdir build
cd build

# Configure the project
cmake ..

# Build the executable
cmake --build .
```
4. Run tests

On Windows (Powershell):
```powershell
.\venv\Scripts\Activate.ps1
.\test.ps1
```
On Unix/macOS:
```bash
source venv/bin/activate
./test.sh
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
├── CMakeLists.txt
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
│   ├── trie.h
│   ├── config.h
│   ├── utils.cpp
│   └── utils.h
├── test.ps1               # test script
├── test.sh
└── tests
    └── xp

```