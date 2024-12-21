# prepare_league_format.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Prepare League database dumps for Results input."""

if __name__ == "__main__":
    _APPLICATION_NAME = "PrepareLeagueFormat"
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
        from .core.prepareresults import PrepareLeagueDump
        from .gui.prepare import PrepareLeague
    except Exception as error:
        start_application_exception(
            error, appname=_APPLICATION_NAME, action="import"
        )
        raise SystemExit(
            " import ".join(("Unable to", _APPLICATION_NAME))
        ) from error
    try:
        app = PrepareLeague(PrepareLeagueDump)
    except Exception as error:
        start_application_exception(
            error, appname=_APPLICATION_NAME, action="initialise"
        )
        raise SystemExit(
            " initialise ".join(("Unable to", _APPLICATION_NAME))
        ) from error
    try:
        if app.open_submission():
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
