import psycopg2
import psycopg2.extras


def create_connection(database_url: str) -> psycopg2.extensions.connection:
    return psycopg2.connect(database_url)


def close(conn: psycopg2.extensions.connection) -> None:
    conn.close()


def add_url(conn: psycopg2.extensions.connection, url: str) -> int:
    with conn.cursor() as cur:

        try:
            cur.execute("""
                INSERT INTO urls (name)
                VALUES (%s) RETURNING id;
                """,
                        (url,))
            conn.commit()
            id = cur.fetchone()[0]
            message = ('Страница успешно добавлена', 'success')
        except psycopg2.Error:
            message = ('Произошла ошибка при добавлении страницы', 'error')

    return id, message


def get_url_by_name(conn: psycopg2.extensions.connection, url: str) -> dict:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        cur.execute("""
            SELECT * FROM urls
            WHERE name = %s;
            """,
                    (url, ))
        url = cur.fetchone()

    return url


def get_url(conn: psycopg2.extensions.connection, id: int) -> dict:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        cur.execute("""
            SELECT * FROM urls
            WHERE id = %s;
            """,
                    (id, ))
        url = cur.fetchone()

    return url


def add_url_check(conn: psycopg2.extensions.connection,
                   check_date: dict) -> bool:
    with conn.cursor() as cur:

        try:
            cur.execute("""
                INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description)
                VALUES (%s, %s, %s, %s, %s);
                """,
                        (check_date['url_id'],
                         check_date['status_code'],
                         check_date['h1'],
                         check_date['title'],
                         check_date['description'])
                        )
            conn.commit()
            res = True
        except psycopg2.Error:
            res = False

    return res


def get_checks_url(conn: psycopg2.extensions.connection, url_id: int) -> list:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        cur.execute("""SELECT * FROM url_checks
                    WHERE url_id = %s
                    ORDER BY created_at DESC;""",
                    (url_id)
                    )
        checks = cur.fetchall()

    return checks


def get_url_check(conn: psycopg2.extensions.connection) -> list:
    with conn.cursor() as cur:

        cur.execute("""SELECT id, name FROM urls ORDER BY id DESC;""")
        table_urls = cur.fetchall()
        cur.execute("""SELECT
                    url_checks.url_id,
                    url_checks.created_at,
                    status_code
                       FROM url_checks JOIN (
                           SELECT url_id, MAX(created_at) AS created_at
                           FROM url_checks GROUP BY url_id) AS tab
                       ON url_checks.url_id=tab.url_id
                       AND url_checks.created_at=tab.created_at;""")
        url_checks = cur.fetchall()

    res = []
    for id, name in table_urls:
        for url_id, created_at, status_code in url_checks:
            if id == url_id:
                res.append({'id': id,
                            'name': name,
                            'last_data': created_at,
                            'status_code': status_code})
                break
        else:
            res.append({'id': id,
                        'name': name,
                        'last_data': '',
                        'status_code': ''})
    return res
