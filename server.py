from flask import Flask, Response, request, make_response, render_template, send_file
from renderer import Renderer
from fetchers import Fetcher, OpenWeatherFetcher, ExampleFetcher
from store import Store, FileStore
from urllib.parse import quote_plus
from datetime import datetime, timedelta, time as datetime_time
from typing import Any, Dict, Optional, Union
from device_types import Surface
from screensaver import Screensaver
import threading
import io
import time
import json
import socket
import sys


MOTD = "motd"


class Context:
    def __init__(
        self,
        fetcher: Fetcher,
        renderer: Renderer,
        screensaver: Screensaver,
        ds: Optional[Surface],
        store: Store,
    ) -> None:
        self.fetcher = fetcher
        self.renderer = renderer
        self.screensaver = screensaver
        self.last_fetch_response = {}  # type: Union[Dict[str,Any],Exception]
        self.last_fetched_at = None  # type: Optional[datetime]
        self.motd_updated_at = None  # type: Optional[datetime]
        self.screen_updated_at = None  # type: Optional[datetime]
        self.ds = ds
        self.store = store

    def set_motd(self, motd: str) -> None:
        self.store.set(MOTD, motd)
        self.renderer.motd = motd
        self.motd_updated_at = datetime.now()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile("settings.py")

    if app.config["EXAMPLE_RESPONSE"]:
        fetcher = ExampleFetcher(app.config["EXAMPLE_RESPONSE"])  # type: Fetcher
    else:
        fetcher = OpenWeatherFetcher(
            app.config["OPEN_WEATHER_TOKEN"],
            float(app.config["LAT"]),
            float(app.config["LON"]),
        )

    renderer = Renderer(app.config["DISPLAY_WIDTH"], app.config["DISPLAY_HEIGHT"])
    screensaver = Screensaver(app.config["DISPLAY_WIDTH"], app.config["DISPLAY_HEIGHT"])

    store = FileStore(app.config["STORE_PATH"])
    motd = store.get(MOTD)
    if motd:
        renderer.motd = motd

    ds = None  # type: Optional[Surface]
    try:
        from device_surface import DeviceSurface

        ds = DeviceSurface(app.config["DISPLAY_WIDTH"], app.config["DISPLAY_HEIGHT"])
    except NotImplementedError:
        print(
            "Skipping initialization of device surface, since we don't appear to be running on a supported board"
        )

    b = threading.Barrier(2, timeout=5)
    ctx = Context(fetcher, renderer, screensaver, ds, store)

    def fetch_forecast() -> Union[Dict[str, Any], Exception]:
        print("Refreshing forecast ...")
        try:
            ctx.last_fetch_response = ctx.fetcher.fetch()
        except Exception as e:
            print(f"Refreshing forecast failed: {e}")
            # For some reason, I've been seeing issues with DNS resolution that persist until the process
            # restarts. In the case where we see two such failures in a row, just exit and let systemd
            # restart us.
            if isinstance(ctx.last_fetch_response, socket.gaierror) and isinstance(
                e, socket.gaierror
            ):
                print("Exiting after two consecutive DNS errors ...")
                sys.exit(1)
            ctx.last_fetch_response = e

        ctx.last_fetched_at = datetime.now()
        return ctx.last_fetch_response

    def poll_fetcher() -> None:
        interval = app.config["WEATHER_REFRESH_INTERVAL"]
        fetch_forecast()
        b.wait()
        print(f"Polling for forecast updates every {interval}s ...")
        while True:
            fetch_forecast()
            print(f"Sleeping {interval}s until next forecast update ...")
            time.sleep(interval)

    def render_loop() -> None:
        interval = app.config["RENDER_INTERVAL"]
        print(f"Re-rendering every {interval}s ...")
        b.wait()
        while True:
            try:
                update_screen()
            except Exception as e:
                print(f"Error while updating screen: {e}")
            print(f"Sleeping {interval}s before next re-render ...")
            time.sleep(interval)

    def update_screen() -> None:
        print(f"Re-rendering ...")
        if ctx.ds:
            if is_night():
                img = ctx.screensaver.render()
            else:
                if not isinstance(ctx.last_fetch_response, Exception):
                    img = ctx.renderer.render(ctx.last_fetch_response)
            ctx.ds.update(img)
        ctx.screen_updated_at = datetime.now()

    def is_night() -> bool:
        t = datetime.now().time()
        night_start = datetime_time(22, 0)
        night_end = datetime_time(6, 5)
        return t > night_start or t < night_end

    fetcher_thread = threading.Thread(name="fetcher", daemon=True, target=poll_fetcher)
    fetcher_thread.start()

    render_thread = threading.Thread(name="renderer", daemon=True, target=render_loop)
    render_thread.start()

    @app.route("/")
    def root() -> str:
        return render_latest("index.html")

    @app.route("/motd", methods=["POST"])
    def update_motd() -> str:
        return set_motd(request.form["motd"])

    @app.route("/motd", methods=["DELETE"])
    def clear_motd() -> str:
        return set_motd("")

    def set_motd(motd: str) -> str:
        ctx.set_motd(motd)
        return render_latest("latest.html")

    @app.route("/preview")
    def preview() -> Response:
        if isinstance(ctx.last_fetch_response, Exception):
            return make_response(f"{ctx.last_fetch_response}", 500)
        raw_image = ctx.renderer.render(ctx.last_fetch_response)
        image_buf = io.BytesIO(b"")
        raw_image.save(image_buf, format="png")
        image_buf.seek(0)
        return send_file(image_buf, mimetype="image/png")

    def render_latest(template: str) -> str:
        if isinstance(ctx.last_fetch_response, Exception):
            most_recent_forecast = ctx.last_fetch_response  # type: Union[str,Exception]
        else:
            most_recent_forecast = json.dumps(ctx.last_fetch_response, indent=2)

        return render_template(
            template,
            height=app.config["DISPLAY_HEIGHT"],
            image_ts=datetime.now(),
            fetch_url=ctx.fetcher.url(),
            time_since_last_update=format_last_update_time(ctx.last_fetched_at),
            time_since_motd_update=format_last_update_time(ctx.motd_updated_at),
            time_since_screen_update=format_last_update_time(ctx.screen_updated_at),
            most_recent_forecast=most_recent_forecast,
            motd=str(ctx.renderer.motd or ""),
        )

    return app


def format_last_update_time(last_update: Optional[datetime]) -> str:
    if not last_update:
        return "never"
    since = datetime.now() - last_update
    time_since_last_update = timedelta(
        days=since.days,
        seconds=since.seconds,
    )
    return f"{time_since_last_update} ago"


create_app().run(port=8888, host="0.0.0.0")
