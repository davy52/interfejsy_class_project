import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image


win = tk.Tk()
win.title("Controla poziomu wody w zbiorniku")
win.wm_minsize(width=640, height=360)

s = ttk.Style()
s.configure('my.TFrame', background='#1A4CF5', borderwidth='2')
#s.configure('root.TFrame', background='red')


root = ttk.Frame(win, padding=10)
root.grid(row=0, column=0, sticky='news')

zbiornik = ttk.Frame(root, height=300, width=500, style='my.TFrame')
zbiornik.grid(row=0, column=0)

poziom = ttk.Frame(root, height=300, width=500, style='my.TFrame')
poziom.grid(row=0, column=2)

regulacja = ttk.Frame(root, height=300, width=500, style='my.TFrame')
regulacja.grid(row=1, column=0)

nastawy = ttk.Frame(root, height=300, width=500, style='my.TFrame')
nastawy.grid(row=0, column=3)

symulacja = ttk.Frame(root, height=300, width=500, style='my.TFrame')
symulacja.grid(row=1, column=3)

win.mainloop()

 

 
