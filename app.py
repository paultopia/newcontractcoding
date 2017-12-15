from core import core
import os
is_local = bool(os.environ.get("NEW_CONTRACT_CODING_LOCAL"))

if __name__ == '__main__':
    if is_local:
        core.debug = True  # comment out for prod
    core.run()
