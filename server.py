from flask import Flask, request, render_template, send_file
from renderer import Renderer
from fetchers import OpenWeatherFetcher, ExampleFetcher
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import threading
import io
import time
import json


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("settings.py")

    if app.config['EXAMPLE_RESPONSE']:
        app.fetcher = ExampleFetcher(app.config['EXAMPLE_RESPONSE'])
    else:
        app.fetcher = OpenWeatherFetcher(
            app.config["OPEN_WEATHER_TOKEN"],
            float(app.config["LAT"]),
            float(app.config["LON"]),
        )

    app.renderer = Renderer(app.config['DISPLAY_WIDTH'], app.config['DISPLAY_HEIGHT'])
    app.last_fetch_response = None
    app.last_fetched_at = None
    app.motd_updated_at = None
    app.screen_updated_at = None

    ds = None # type: Optional[DeviceSurface] 
    try:
        from device_surface import DeviceSurface
        ds = DeviceSurface(app.config['DISPLAY_WIDTH'], app.config['DISPLAY_HEIGHT'], app.renderer)
    except NotImplementedError:
        print("Skipping initialization of device surface, since we don't appear to be running on a supported board")

    def fetch_forecast():
        print('Refreshing forecast ...')
        try:
            app.last_fetch_response = app.fetcher.fetch()
        except Exception as e:
            print(f'Refreshing forecast failed: {e}')
            app.last_fetch_response = e

        app.last_fetched_at = datetime.now()
        return app.last_fetch_response

    def poll_fetcher():
        interval = app.config['WEATHER_REFRESH_INTERVAL']
        print(f'Polling for forecast updates every {interval}s ...')
        while True:
            fetch_forecast()
            print(f'Sleeping {interval}s until next forecast update ...')
            time.sleep(interval)

    def render_loop():
        interval = app.config['RENDER_INTERVAL']
        print(f'Re-rendering every {interval}s ...')
        while True:
            print(f'Re-rendering ...')
            if ds:
                ds.update(app.last_fetch_response)
            app.screen_updated_at = datetime.now()
            print(f'Sleeping {interval}s before next re-render ...')
            time.sleep(interval)

    fetcher_thread = threading.Thread(name='fetcher', daemon=True, target=poll_fetcher)
    fetcher_thread.start()

    render_thread = threading.Thread(name='renderer', daemon=True, target=render_loop)
    render_thread.start()

    @app.route("/")
    def root():
        return render_latest('index.html')

    @app.route("/motd", methods=["POST"])
    def update_motd():
        app.renderer.motd = request.form['motd']
        app.motd_updated_at = datetime.now()
        return render_latest('latest.html')

    @app.route('/motd', methods=['DELETE'])
    def clear_motd():
        app.renderer.motd = ''
        app.motd_updated_at = datetime.now()
        return render_latest('latest.html')

    @app.route("/fetch")
    def fetch():
        return refresh()

    @app.route("/preview")
    def preview():
        raw_image = app.renderer.render(app.last_fetch_response)
        image_buf = io.BytesIO(b"")
        raw_image.save(image_buf, format="png")
        image_buf.seek(0)
        return send_file(image_buf, mimetype="image/png")

    def render_latest(template: str):
        if isinstance(app.last_fetch_response, Exception):
            most_recent_forecast = app.last_fetch_response
        else:
            most_recent_forecast = json.dumps(app.last_fetch_response, indent=2)

        return render_template(
            template,
            image_ts=datetime.now(),
            fetch_url=app.fetcher.url(),
            time_since_last_update=format_last_update_time(app.last_fetched_at),
            time_since_motd_update=format_last_update_time(app.motd_updated_at),
            time_since_screen_update=format_last_update_time(app.screen_updated_at),
            most_recent_forecast=most_recent_forecast,
            motd=str(app.renderer.motd or ''),
        )

    return app


def format_last_update_time(last_update):
    if not last_update:
        return 'never'
    since = datetime.now() - last_update
    time_since_last_update = timedelta(
        days=since.days,
        seconds=since.seconds,
    )
    return f'{time_since_last_update} ago'


create_app().run(port=8888, host='0.0.0.0')
