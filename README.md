# squaredle-solver

Soilves Squaredle. Written in C++ for performance.  
It scrapes the board from the website, preprocesses it, then solves the board using a Trie-based backtracking algorithm.

## requirements

- Python 3.8+
- g++ with C++17 support
- Selenium
- BeautifulSoup4
- `webdriver-manager`

## usage

1. Run the shell:
```bash
g++ -std=c++17 -o squaredle-solver.exe solver/*.cpp 
python main.py