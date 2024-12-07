# resultsdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application using ECF grading interface."""

if __name__ == "__main__":
    import chessreports.gui.resultsroot
    import chessreports.gui.leagues

    app = chessreports.gui.resultsroot.Results(
        title="ChessReportsGrading",
        gui_module=chessreports.gui.leagues.Leagues,
        width=400,
        height=200,
    )
    app.root.mainloop()
