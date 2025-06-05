import sqlite3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from example_interfaces.srv import Trigger   # ROS 2 service

DB_FILE = 'memory.db'

def create_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_utterance TEXT,
            robot_reply TEXT,
            valence REAL,
            turn_index INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_memory(user_id, user_utterance, robot_reply, valence, turn_index):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO memory (user_id, user_utterance, robot_reply, valence, turn_index)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, user_utterance, robot_reply, valence, turn_index))
    conn.commit()
    conn.close()

def fetch_all_memories(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT user_utterance, robot_reply, valence, turn_index FROM memory
        WHERE user_id = ?
        ORDER BY turn_index ASC
    ''', (user_id,))
    memories = c.fetchall()
    conn.close()
    return memories

LAMBDA = 0.9
BETA = 1.0
GAMMA = 3

def retention_weight(memory_valence, delta_t, lambd=LAMBDA, beta=BETA):
    return (lambd ** delta_t) * (1 + beta * memory_valence)

def retrieval_probability(weight, curr_valence, memory_valence, gamma=GAMMA):
    return weight * math.exp(-gamma * abs(curr_valence - memory_valence))

def get_best_memories(user_id, curr_turn, curr_valence, top_n=3):
    all_memories = fetch_all_memories(user_id)
    scored = []
    for (u, r, v, t) in all_memories:
        delta_t = curr_turn - t
        weight = retention_weight(v, delta_t)
        prob = retrieval_probability(weight, curr_valence, v)
        scored.append({'user_utterance': u, 'robot_reply': r, 'valence': v, 'turn_index': t, 'score': prob})
    best = sorted(scored, key=lambda x: x['score'], reverse=True)[:top_n]
    return best

class MemoryNode(Node):
    def __init__(self):
        super().__init__('memory_node')
        create_table()
        self.get_logger().info('MemoryNode started, database ready.')

        # NEW: Subscribe to memory_log
        self.create_subscription(String, 'memory_log', self.memory_log_callback, 10)

        # Service for getting context
        self.create_service(Trigger, 'get_context_memories', self.handle_get_context)

        self.turn_index = 1
        self.user_id = 'default_user'
        self.current_valence = 0.0  # last received valence

    def memory_log_callback(self, msg):
        # log_msg format: user_id||user_utterance||robot_reply||valence||turn_index
        try:
            parts = msg.data.split('||')
            if len(parts) != 5:
                self.get_logger().warn(f"Malformed memory log message: {msg.data}")
                return
            user_id, user_utterance, robot_reply, valence, turn_index = parts
            save_memory(user_id, user_utterance, robot_reply, float(valence), int(turn_index))
            self.get_logger().info(
                f"Saved memory (turn {turn_index}): '{user_utterance}' / '{robot_reply}' / valence={valence}"
            )
            self.turn_index = int(turn_index) + 1
            self.user_id = user_id
            self.current_valence = float(valence)
        except Exception as e:
            self.get_logger().error(f"Failed to parse or save memory log: {e}")

    def handle_get_context(self, request, response):
        curr_turn = self.turn_index
        curr_valence = self.current_valence
        memories = get_best_memories(self.user_id, curr_turn, curr_valence, 3)
        lines = []
        for m in memories:
            lines.append(f"{m['user_utterance']} → {m['robot_reply']} (V={m['valence']})")
        response.success = True
        response.message = "\n".join(lines) if lines else "No context memories."
        return response

def main(args=None):
    rclpy.init(args=args)
    node = MemoryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

