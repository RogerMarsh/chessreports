# resultsdb_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application using Lite interface: no ECF connections."""

if __name__ == "__main__":
    import chessreports.gui.resultsroot
    import chessreports.gui.leagues_lite

    app = chessreports.gui.resultsroot.Results(
        title="ChessReports",
        gui_module=chessreports.gui.leagues_lite.Leagues,
        width=400,
        height=200,
    )
    app.root.mainloop()
