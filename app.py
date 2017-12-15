from core import core as app
import os
is_local = bool(os.environ.get("NEW_CONTRACT_CODING_LOCAL"))
# print("DATABASE URL: " + os.environ.get('DATABASE_URL'))

if __name__ == '__main__':
    if is_local:
        app.debug = True  # comment out for prod
    app.run()
