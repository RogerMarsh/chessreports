# ecfdownload.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Dialogues to extract player and club lists from ECF website downloads.

The extract can be direct or from previously downloaded files.

"""
from solentware_misc.gui.dialogue import ModalDialogueGo

DOWNLOAD = "Download"
EXTRACT = "Extract"
CANCEL = "Cancel"


class ECFDownloadDialogue(ModalDialogueGo):
    """Base class for dialogues to download ECF ratings files.

    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.

    """

    def __init__(self, text="data", scroll=False, **kargs):
        """Create ECF download dialogue."""
        text = "".join(
            (
                "Click 'Download' to download the '",
                text,
                "' from the ECF website.\n\nClick 'Extract' to extract the '",
                text,
                "' from a previous download saved in a file.",
            )
        )
        buttons = (DOWNLOAD, EXTRACT, CANCEL)
        super().__init__(text=text, buttons=buttons, **kargs)


# Probably best to delete all this, or at least move it to a tests or
# samples directory.
if __name__ == "__main__":

    import tkinter

    class R(tkinter.Tk):
        """A simple sample."""

        def __init__(self):
            """Initialise test."""
            super().__init__()
            self.b = tkinter.Button(self, text="Do", command=self.do)
            self.b.pack()

        def get_widget(self):
            """Return top level widget."""
            return self

        def do(self):
            """Run the dialogue."""
            d = ECFDownloadDialogue(
                parent=self,
                title="Test",
                side=tkinter.LEFT,
                scroll=False,
                height=5,
                width=80,
                wrap=tkinter.WORD,
            ).go()
            print(d)

    R().mainloop()

    # As close as possible to tkinter.simpledialog test but without the three
    # extra dialogues following d.go().
    def test():
        """Run a test."""

        class Q(tkinter.Tk):
            def get_widget(self):
                return self

        root = Q()

        def doit(root=root):
            d = ECFDownloadDialogue(
                parent=root,
                title="Test",
                side=tkinter.LEFT,
                scroll=False,
                height=5,
                width=80,
                wrap=tkinter.WORD,
            )
            print(d.go())

        t = tkinter.Button(root, text="Test", command=doit)
        t.pack()
        q = tkinter.Button(root, text="Quit", command=t.quit)
        q.pack()
        t.mainloop()

    test()
