from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "Tasks" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "date_created" TIMESTAMP NOT NULL,
    "name" VARCHAR(120) NOT NULL,
    "detail" TEXT NOT NULL,
    "completed" INT NOT NULL  DEFAULT 0
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "Tasks";"""
