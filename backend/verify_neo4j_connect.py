import os
import sys
import time
from pathlib import Path

def load_env(env_path: Path):
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            # don't override existing env vars
            if k not in os.environ:
                os.environ[k] = v


def main():
    here = Path(__file__).parent
    env_path = here / ".env"
    load_env(env_path)

    uri = os.environ.get("NEO4J_URI") or os.environ.get("NEO4J_URL")
    user = os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER")
    pwd = os.environ.get("NEO4J_PASSWORD")
    db = os.environ.get("NEO4J_DATABASE")

    print("Using connection parameters:")
    print(f"  URI: {uri}")
    print(f"  Username: {user}")
    print(f"  Database: {db}")

    if not uri or not user or not pwd:
        print("Missing one of NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD — aborting.")
        sys.exit(2)

    wait_seconds = 60
    print(f"Waiting {wait_seconds} seconds before attempting connection...")
    time.sleep(wait_seconds)

    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session(database=db) as session:
            rec = session.run("RETURN 1 AS result").single()
            if rec and rec.get("result") == 1:
                print("Connection successful: returned 1")
                driver.close()
                sys.exit(0)
            else:
                print("Connected but unexpected result from test query.")
                driver.close()
                sys.exit(3)
    except Exception as e:
        print("Connection failed:", str(e))
        sys.exit(4)


if __name__ == "__main__":
    main()
