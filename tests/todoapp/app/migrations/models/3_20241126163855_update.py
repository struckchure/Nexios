from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "Tasks" ADD "priority" VARCHAR(6) NOT NULL  DEFAULT 'TaskPriority.MEDIUM' /* LOW: low\nMEDIUM: medium\nHIGH: high */;
        ALTER TABLE "Tasks" ADD "image" None;
        ALTER TABLE "Tasks" ADD "date_completed" TIMESTAMP;
        ALTER TABLE "Tasks" DROP COLUMN "filefield";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "Tasks" ADD "filefield" None NOT NULL;
        ALTER TABLE "Tasks" DROP COLUMN "priority";
        ALTER TABLE "Tasks" DROP COLUMN "image";
        ALTER TABLE "Tasks" DROP COLUMN "date_completed";"""
