# Setup build file for compile .py to .exe
from cx_Freeze import setup, Executable


build_exe_options = {
    "packages": ["pygame"],
    "include_files": ["chess/"],
}

setup(
    name = "ChessItium",
    version = "0.1",
    description = "Chess game with the possibility to play against a friend or against an AI and some other nice features.",
    options = {"build_exe": build_exe_options},
    executables = [Executable("menu.py", base="Win32GUI", icon="./chess/assets/chessitium.ico")]
)

# Run "python setup.py build" to have the .exe for the app