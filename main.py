from aiohttp import web
import app
import argparse
import aioreloader

parser = argparse.ArgumentParser()

parser.add_argument('--host', default="127.0.0.1")
parser.add_argument('--port', default="8888")
parser.add_argument('--reload', action='store_true')

args_namespace = parser.parse_args()

app = app.create_app()

if args_namespace.reload:
    aioreloader.start()
    print("Reloaded")

if __name__ == "__main__":
    web.run_app(app, host=args_namespace.host, port=args_namespace.port)

