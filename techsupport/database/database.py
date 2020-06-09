import aiosqlite


class Database:
    def __init__(self, path="./data/database.sqlite3"):
        self.path = path

    async def connect(self):
        self._conn = await aiosqlite.connect(self.path)
        await self._conn.execute("pragma journal_mode=wal")
        await self.ensure()

    async def close(self):
        await self._conn.close()

    async def commit(self):
        await self._conn.commit()

    async def ensure(self):
        await self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id CHARACTER(64) PRIMARY KEY,
                guild_id INTEGER DEFAULT NULL,
                author_id INTEGER DEFAULT NULL,
                agents TEXT DEFAULT NULL,
                language VARCHAR(32) DEFAULT NULL,
                description TEXT DEFAULT NULL,
                message_id INTEGER DEFAULT NULL,
                channel_id INTEGER DEFAULT NULL,
                created_at DATETIME DEFAULT NULL,
                state_name VARCHAR(16) DEFAULT UNASSIGNED
            );
        """
        )

        await self.commit()

    async def get_all(self):
        c = await self._conn.cursor()
        await c.execute("SELECT * FROM tickets WHERE state_name != 'SOLVED'")

        return await c.fetchall()

    async def update(self, ticket):
        await self._conn.execute(
            """
            INSERT INTO tickets (id, guild_id, author_id, agents, language, description, message_id, channel_id, created_at, state_name)
            VALUES (:id, :guild_id, :author_id, :agents, :language, :description, :message_id, :channel_id, :created_at, :state_name)
            ON CONFLICT (id) DO UPDATE SET
                guild_id=excluded.guild_id,
                author_id=excluded.author_id,
                agents=excluded.agents,
                language=excluded.language,
                description=excluded.description,
                message_id=excluded.message_id,
                channel_id=excluded.channel_id,
                created_at=excluded.created_at,
                state_name=excluded.state_name
            """,
            ticket.serialise(),
        )

        await self.commit()

    async def update_all(self, ticket_store):
        await self._conn.executemany(
            """
            INSERT INTO tickets (id, guild_id, author_id, agents, language, description, message_id, channel_id, created_at, state_name)
            VALUES (:id, :guild_id, :author_id, :agents, :language, :description, :message_id, :channel_id, :created_at, :state_name)
            ON CONFLICT (id) DO UPDATE SET
                guild_id=excluded.guild_id,
                author_id=excluded.author_id,
                agents=excluded.agents,
                language=excluded.language,
                description=excluded.description,
                message_id=excluded.message_id,
                channel_id=excluded.channel_id,
                created_at=excluded.created_at,
                state_name=excluded.state_name
            """,
            ticket_store.as_serialised(),
        )

        await self.commit()
