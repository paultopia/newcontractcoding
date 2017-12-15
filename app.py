from core import core as app
import os
is_local = bool(os.environ.get("NEW_CONTRACT_CODING_LOCAL"))

if __name__ == '__main__':
    if is_local:
        app.debug = True  # comment out for prod
    app.run()
