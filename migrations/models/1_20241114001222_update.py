from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "abstractbasesession" (
    "session_key" VARCHAR(40) NOT NULL  PRIMARY KEY,
    "session_data" TEXT NOT NULL,
    "expire_date" TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_abstractbas_expire__6bba98" ON "abstractbasesession" ("expire_date");
        CREATE TABLE IF NOT EXISTS "session" (
    "session_key" VARCHAR(40) NOT NULL  PRIMARY KEY,
    "session_data" TEXT NOT NULL,
    "expire_date" TIMESTAMP NOT NULL
) /* Nexio provides full support for anonymous sessions, enabling the storage and retrieval of arbitrary data on a per-visitor basis. This data is stored on the server side, while cookies are used to send and receive a session ID, rather than the data itself. */;
CREATE INDEX IF NOT EXISTS "idx_session_expire__ee0f51" ON "session" ("expire_date");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "abstractbasesession";
        DROP TABLE IF EXISTS "session";"""
