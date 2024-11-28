from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "session" (
    "session_key" VARCHAR(240) NOT NULL  PRIMARY KEY,
    "session_data" TEXT NOT NULL,
    "expire_date" TIMESTAMP NOT NULL
) /* Nexio provides full support for anonymous sessions, enabling the storage and retrieval of arbitrary data on a per-visitor basis. This data is stored on the server side, while cookies are used to send and receive a session ID, rather than the data itself. */;
CREATE INDEX IF NOT EXISTS "idx_session_expire__ee0f51" ON "session" ("expire_date");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
