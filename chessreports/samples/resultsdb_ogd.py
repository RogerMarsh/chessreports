# resultsdb_ogd.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application using OGD interface."""

if __name__ == "__main__":
    import chessreports.gui.resultsroot
    import chessreports.gui.leagues_ogd

    app = chessreports.gui.resultsroot.Results(
        title="ChessReportsOGD",
        gui_module=chessreports.gui.leagues_ogd.Leagues,
        width=400,
        height=200,
    )
    app.root.mainloop()
