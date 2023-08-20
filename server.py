from flask import Flask, request, render_template, send_file
from renderer import Renderer
from fetchers import Fetcher, OpenWeatherFetcher, ExampleFetcher
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from device_types import Surface
import threading
import io
import time
import json


class Context:
    def __init__(
        self, fetcher: Fetcher, renderer: Renderer, ds: Optional[Surface]
    ) -> None:
        self.fetcher = fetcher
        self.renderer = renderer
        self.last_fetch_response = {}  # type: Union[Dict[str,Any],Exception]
        self.last_fetched_at = None  # type: Optional[datetime]
        self.motd_updated_at = None  # type: Optional[datetime]
        self.screen_updated_at = None  # type: Optional[datetime]
        self.ds = ds


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

    ds = None  # type: Optional[Surface]
    try:
        from device_surface import DeviceSurface

        ds = DeviceSurface(app.config["DISPLAY_WIDTH"], app.config["DISPLAY_HEIGHT"])
    except NotImplementedError:
        print(
            "Skipping initialization of device surface, since we don't appear to be running on a supported board"
        )

    b = threading.Barrier(2, timeout=5)
    ctx = Context(fetcher, renderer, ds)

    def fetch_forecast() -> Union[Dict[str, Any], Exception]:
        print("Refreshing forecast ...")
        try:
            ctx.last_fetch_response = ctx.fetcher.fetch()
        except Exception as e:
            print(f"Refreshing forecast failed: {e}")
            ctx.last_fetch_response = e

        ctx.last_fetched_at = datetime.now()
        return ctx.last_fetch_response

    def poll_fetcher():
        interval = app.config["WEATHER_REFRESH_INTERVAL"]
        fetch_forecast()
        b.wait()
        print(f"Polling for forecast updates every {interval}s ...")
        while True:
            fetch_forecast()
            print(f"Sleeping {interval}s until next forecast update ...")
            time.sleep(interval)

    def render_loop():
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

    def update_screen():
        print(f"Re-rendering ...")
        if ctx.ds:
            ctx.ds.update(renderer.render(ctx.last_fetch_response))
        ctx.screen_updated_at = datetime.now()

    fetcher_thread = threading.Thread(name="fetcher", daemon=True, target=poll_fetcher)
    fetcher_thread.start()

    render_thread = threading.Thread(name="renderer", daemon=True, target=render_loop)
    render_thread.start()

    @app.route("/")
    def root():
        return render_latest("index.html")

    @app.route("/motd", methods=["POST"])
    def update_motd() -> None:
        return set_motd(request.form["motd"])

    @app.route("/motd", methods=["DELETE"])
    def clear_motd() -> None:
        return set_motd("")

    def set_motd(motd: str) -> None:
        ctx.renderer.motd = motd
        ctx.motd_updated_at = datetime.now()
        render_latest("latest.html")

    @app.route("/fetch")
    def fetch():
        return refresh()

    @app.route("/preview")
    def preview():
        raw_image = ctx.renderer.render(ctx.last_fetch_response)
        image_buf = io.BytesIO(b"")
        raw_image.save(image_buf, format="png")
        image_buf.seek(0)
        return send_file(image_buf, mimetype="image/png")

    def render_latest(template: str):
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


def format_last_update_time(last_update):
    if not last_update:
        return "never"
    since = datetime.now() - last_update
    time_since_last_update = timedelta(
        days=since.days,
        seconds=since.seconds,
    )
    return f"{time_since_last_update} ago"


create_app().run(port=8888, host="0.0.0.0")
