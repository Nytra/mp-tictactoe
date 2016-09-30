repo = "https://github.com/Nytra/mp-tictactoe"

from urllib import request
import zipfile, io, os

def update():
    try:
        print("Downloading repository...")
        r = request.urlopen(repo + "/archive/master.zip")
        print("Extracting...")
        with zipfile.ZipFile(io.BytesIO(r.read())) as z:
            z.extractall()
        print("Moving files...")
        cmd = "move \"{}\\mp-tictactoe-master\\*\" \"{}\"".format(os.path.abspath(""), os.path.abspath(""))
        os.system(cmd)
        cmd = "rmdir \"{}\\mp-tictactoe-master\"".format(os.path.abspath(""))
        print("Cleaning up...")
        os.system(cmd)
        input("Installation complete.\n\nPress enter to quit . . .")
    except:
        print("An error occurred during the installation procedure. Your files may be corrupt.")

if __name__ == "__main__":
    update()