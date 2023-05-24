"""MenuBar for the MainWindow."""

from __future__ import annotations
import tkinter as tk
from pathlib import Path
from tkinter.messagebox import showinfo
from typing import TYPE_CHECKING

#from MainFrame import MainWindow
from AllFrame import All_Frame

if TYPE_CHECKING:
    from MainFrame import MainWindow
class myMenuBar(tk.Menu):
    """Menu bar to be displayed on the Main Frame."""

    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent,*args, **kwargs)
        # expecting parent to be the toplevel parent of the main frame
        self.parent = parent
        menubar= tk.Menu(parent, tearoff=False)
        #menubar.add_command(label="Default", command=lambda: parent.show_frame(MainWindow))
        menubar.add_command(label="Display All", command=self.displayAll)
        menubar.add_command(label="Help", command=self.help)
        menubar.add_command(label="About", command=self.about)

        self.menubar = menubar

    def displayAll(self):
        self.newWindow=tk.Toplevel()
        self.newWindow.title("display all")
        self.newWindow.frames = {}
        #self.parent.frame.destroy()
        container = tk.Frame(self.newWindow)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        frame = All_Frame(container, self.newWindow)
        self.parent.frames[All_Frame] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        #All_Frame(self.parent)
        print ("all")

    def displayDefalult(self):
        print ("default")

    def about(self):
        showinfo(
            "About",
            (
                "Copyright  (C) 2021  Yuqian Zhang\n\n"
                "Imperial College London. y.zhang20@imperial.ac.uk"
            ),
        )
    def help(self) -> None:
        showinfo(
            "Help",
            (
                "For help please email y.zhang20@imperial.ac.uk"
            ),
        )
    def _debug(self) -> None:
        """Used for debugging."""
        pass

def displayDefalult():
    pass
def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    root.config(menu=myMenuBar(root).menubar)
    #my_gui =MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()