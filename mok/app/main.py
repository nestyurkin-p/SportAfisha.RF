import uuid
import random
from datetime import datetime
from typing import Callable, NamedTuple
import psycopg2


class DataBaseMokConfig(NamedTuple):
    db_name: str
    host: str
    port: int
    user: str
    password: str
    seed_filler: Callable


def generate_uin():
    part1 = f"{random.randint(0, 99):02}"
    part2 = f"{random.randint(0, 99):02}"
    part3 = f"{random.randint(0, 9999999):07}"
    return f"{part1}-{part2}-{part3}"


def athlete_filler(conn):
    cursor = conn.cursor()

    for _ in range(10):
        athlete_id = str(uuid.uuid4())
        name = f"Name_{random.randint(1, 1000)}"
        location = f"City_{random.randint(1, 100)}"
        email = f"{name.lower()}@example.com"
        uin = generate_uin()
        birth_date = datetime(
            1990 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)
        ).date()
        phone_number = f"+7{random.randint(1000000000, 9999999999)}"

        cursor.execute(
            """
            INSERT INTO athletes (id, name, location, email, uin, birth_date, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (athlete_id, name, location, email, uin, birth_date, phone_number),
        )
        print(f"=> Add athlete {_}")

    conn.commit()
    cursor.close()


def office_filler(conn):
    cursor = conn.cursor()

    for _ in range(5):
        office_id = str(uuid.uuid4())
        federal_district = f"District_{random.randint(1, 10)}"
        region = f"Region_{random.randint(1, 50)}"
        email = f"office{random.randint(1, 100)}@example.com"
        director_name = f"Director_{random.randint(1, 100)}"

        cursor.execute(
            """
            INSERT INTO offices (id, federal_district, region, email, director_name)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (office_id, federal_district, region, email, director_name),
        )
        print(f"=> Add office {_}")

    conn.commit()
    cursor.close()


def event_filler(conn):
    cursor = conn.cursor()

    global events
    events = []

    for _ in range(5):
        event_id = str(uuid.uuid4())
        title = f"Event_{random.randint(1, 100)}"
        age_group = random.choice(["Adult", "Child", "Senior"])
        females = random.choice([True, False])
        males = random.choice([True, False])

        pending = True
        rejected = False
        confirmed = False
        finished = False 

        discipline = random.choice(["Football", "Basketball", "Tennis"])
        results = None  
        date_start = datetime(2024, random.randint(1, 12), random.randint(1, 28)).date()
        date_finished = date_start  
        location = f"Location_{random.randint(1, 50)}"
        description = f"Description of {title}"
        is_local = random.choice([True, False])

        cursor.execute(
            """
            INSERT INTO events (
                id, title, age_group, females, males, pending, rejected, confirmed, finished, 
                discipline, results, date_start, date_finished, location, description, is_local
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                event_id,
                title,
                age_group,
                females,
                males,
                pending,
                rejected,
                confirmed,
                finished,
                discipline,
                results,
                date_start,
                date_finished,
                location,
                description,
                is_local,
            ),
        )

        events.append(event_id)
        print(f"=> Add event {_}")

    conn.commit()
    cursor.close()


def application_filler(conn):
    cursor = conn.cursor()

    for _ in range(10):
        application_id = str(uuid.uuid4())

        if not events:
            break

        event_id = random.choice(events)
        events.remove(event_id)

        purpose = f"Purpose_{random.randint(1, 100)}"
        pending = True
        rejected = False
        confirmed = False
        creator_id = str(uuid.uuid4())
        results = None

        cursor.execute(
            """
            INSERT INTO applications (id, event_id, purpose, pending, rejected, confirmed, creator_id, results)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                application_id,
                event_id,
                purpose,
                pending,
                rejected,
                confirmed,
                creator_id,
                results,
            ),
        )
        print(f"=> Add application {_}")

    conn.commit()
    cursor.close()


CONFIG = [
    DataBaseMokConfig(
        db_name="athlete_db",
        host="athlete_db",
        port=5432,
        user="postgres",
        password="toor",
        seed_filler=athlete_filler,
    ),
    DataBaseMokConfig(
        db_name="office_db",
        host="office_db",
        port=5431,
        user="postgres",
        password="toor",
        seed_filler=office_filler,
    ),
    DataBaseMokConfig(
        db_name="event_db",
        host="event_db",
        port=5434,
        user="postgres",
        password="toor",
        seed_filler=event_filler,
    ),
    DataBaseMokConfig(
        db_name="application_db",
        host="application_db",
        port=5433,
        user="postgres",
        password="toor",
        seed_filler=application_filler,
    ),
]


def connect_to_db(host, port, dbname, user, password):
    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def main():
    for db_config in CONFIG:
        print(f"==> Start filling {db_config.db_name}")
        conn = connect_to_db(
            db_config.host,
            db_config.port,
            db_config.db_name,
            db_config.user,
            db_config.password,
        )
        if conn:
            db_config.seed_filler(conn)
            conn.close()
            print(f"> Finish inserted into {db_config.db_name}")
        else:
            print(f"### Failed to connect to {db_config.db_name}")


if __name__ == "__main__":
    main()
