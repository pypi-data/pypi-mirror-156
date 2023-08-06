import os

from spt_factory import MongoFactory


if __name__ == '__main__':
    f = MongoFactory(
        mongo_url=os.getenv('MONGO_URL'),
        tlsCAFile=os.getenv('SSLROOT'),
    )

    print(f.get_postgres_credentials())

    with f.get_postgres(dbname='moniback') as conn:
        print("Happy coding")