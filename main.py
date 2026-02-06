import tkinter as tk
#Importing the three main parts of the application
from model import ImageModel
from view import UI
from controller import AppController

def main():
    root = tk.Tk()
    app = AppController(root, ImageModel, UI)
    root.mainloop()

if __name__ == "__main__":
     



    
