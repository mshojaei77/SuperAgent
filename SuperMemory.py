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
                turn_id INTEGER,
                agent TEXT,
                message TEXT,
                sentiment TEXT,
                knowledge_source TEXT,
                turn_rating TEXT
            )
        """)
        self.conn.commit()

    def save_message(self, message):
        self.cursor.execute(f"""
            INSERT INTO {self.table_name} (
                conversation_id,
                turn_id,
                agent,
                message,
                sentiment,
                knowledge_source,
                turn_rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            message["conversation_id"],
            message["turn_id"],
            message["agent"],
            message["message"],
            message["sentiment"],
            json.dumps(message["knowledge_source"]),
            message["turn_rating"]
        ))
        self.conn.commit()

    def get_messages(self, conversation_id):
        self.cursor.execute(f"""
            SELECT * FROM {self.table_name} WHERE conversation_id = ?
        """, (conversation_id,))
        rows = self.cursor.fetchall()
        messages = []
        for row in rows:
            message = {
                "conversation_id": row[1],
                "turn_id": row[2],
                "agent": row[3],
                "message": row[4],
                "sentiment": row[5],
                "knowledge_source": json.loads(row[6]),
                "turn_rating": row[7]
            }
            messages.append(message)
        return messages

    def close(self):
        self.conn.close()

# Example usage
app = MemoryApp(table_name="chat_sessions", db_path="Memory\\memory.db")

chat_history = [
    {
        "conversation_id": "1234567890",
        "turn_id": 1,
        "agent": "human",
        "message": "Hello, how are you today?",
        "sentiment": "neutral",
        "knowledge_source": ["Personal Knowledge"],
        "turn_rating": "Good"
    },
    {
        "conversation_id": "1234567890",
        "turn_id": 2,
        "agent": "ai",
        "message": "I'm doing well, thank you for asking. How can I assist you today?",
        "sentiment": "positive",
        "knowledge_source": ["AS1", "Personal Knowledge"],
        "turn_rating": "Excellent"
    },
    # Add more items to the chat history
]

for item in chat_history:
    app.save_message(item)

conversation_id = "1234567890"
messages = app.get_messages(conversation_id)
for message in messages:
    print(message)

app.close()