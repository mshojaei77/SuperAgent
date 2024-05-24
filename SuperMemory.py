import sqlite3
import json

class MemoryApp:
    def __init__(self, table_name, db_path):
        self.table_name = table_name
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY,
                conversation_id TEXT,
                agent TEXT,
                message TEXT,
                knowledge_source TEXT
            )
        """)
        self.conn.commit()

    def save_message(self, message):
        self.cursor.execute(f"""
            INSERT INTO {self.table_name} (
                conversation_id,
                agent,
                message,
                knowledge_source
            ) VALUES (?, ?, ?, ?)
        """, (
            message["conversation_id"],
            message["agent"],
            message["message"],
            json.dumps(message["knowledge_source"])
        ))
        self.conn.commit()

    def get_messages(self, conversation_id):
        self.cursor.execute(f"""
            SELECT * FROM {self.table_name} WHERE conversation_id = ?
        """, (conversation_id,))
        rows = self.cursor.fetchall()
        messages = []
        for row in rows:
            if row[4].strip():  # Make sure knowledge_source is not empty
                try:
                    knowledge_source = json.loads(row[4])
                except json.JSONDecodeError:
                    knowledge_source = None
            else:
                knowledge_source = None

            message = {
                "conversation_id": row[1],
                "agent": row[2],
                "message": row[3],
                "knowledge_source": knowledge_source
            }
            messages.append(message)
        return messages

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    memory_app = MemoryApp(table_name="chat_sessions", db_path="Memory\\memory.db")

    conversation_id = "1234567890"  # Replace with a unique conversation ID


    memory_app.save_message({
            "conversation_id": conversation_id,
            "agent": "test role",
            "message": "hello",
            "knowledge_source": "nothing",
    })

    messages = memory_app.get_messages(conversation_id)
    
    for message in messages:
        print(message)

    memory_app.close()