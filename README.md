# Minimania_Game
##Connect Sprites in Code

>Create an Assets folder and place PNG hit effect sprites inside.
>Update the code to load these sprites.

EX
from PySide6 import QtGui
import os

# Set path to the Assets folder
self.asset_path = r"where your "assets" folder locate"
EX
self.asset_path = r"C:\Users\ACER\project_Minimania\Assets"

# Load sprites
self.sprites = {
    "Perfect": QtGui.QPixmap(os.path.join(self.asset_path, "Perfect.png")),
    "Good": QtGui.QPixmap(os.path.join(self.asset_path, "Good.png")),
    "Bad": QtGui.QPixmap(os.path.join(self.asset_path, "Bad.png")),
    "Miss": QtGui.QPixmap(os.path.join(self.asset_path, "Miss.png")),
}



default key is 
D F K L


tutorial

 Click start
 Play 
C;


The score not working at the moment, I’m working on it.


![GetRealOsuManiaGIF](https://github.com/user-attachments/assets/a6564173-583a-4a3c-a5e6-1fcaa1c51603)
