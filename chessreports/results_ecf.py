# results_ecf.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess results database application with ECF results submission."""

if __name__ == "__main__":
    from . import APPLICATION_NAME

    # Keep the 'Grading' name because a 'Rating' version may be built using
    # SQL in a natural way, without options to use database engines other
    # than SQLite3.
    _APPLICATION_NAME = "".join((APPLICATION_NAME, "Grading"))
    try:
        from solentware_misc.gui.startstop import (
            start_application_exception,
            stop_application,
            application_exception,
        )
    except Exception as error:
        import tkinter.messagebox

        try:
            tkinter.messagebox.showerror(
                title="Start Exception",
                message=".\n\nThe reported exception is:\n\n".join(
                    (
                        "".join(
                            (
                                "Unable to import ",
                                "solentware_misc.gui.startstop module",
                            )
                        ),
                        str(error),
                    )
                ),
            )
        except Exception as exc:
            raise SystemExit(
                "Exception while reporting problem importing start module"
            ) from exc
        raise SystemExit(
            "Unable to import start application utilities"
        ) from error
    try:
        from .gui.resultsroot import Results
        from .gui.ecf.leagues import Leagues
    except Exception as error:
        start_application_exception(
            error, appname=_APPLICATION_NAME, action="import"
        )
        raise SystemExit(
            " import ".join(("Unable to", _APPLICATION_NAME))
        ) from error
    try:
        app = Results(
            title=_APPLICATION_NAME, gui_module=Leagues, width=400, height=200
        )
    except Exception as error:
        start_application_exception(
            error, appname=_APPLICATION_NAME, action="initialise"
        )
        raise SystemExit(
            " initialise ".join(("Unable to", _APPLICATION_NAME))
        ) from error
    try:
        app.root.mainloop()
    except SystemExit:
        stop_application(app, app.root)
        raise
    except Exception as error:
        application_exception(
            error,
            app,
            app.root,
            title=_APPLICATION_NAME,
            appname=_APPLICATION_NAME,
        )
