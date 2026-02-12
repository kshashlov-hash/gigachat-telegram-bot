from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class ConversationHistory:
    def __init__(self, history_limit: int = 5):
        self.history_limit = history_limit
        # {chat_id: {user_id: [messages]}}
        self.storage = defaultdict(lambda: defaultdict(list))

    def add_message(self, chat_id: int, user_id: int, role: str, content: str):
        """Добавляет сообщение в историю"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }
        self.storage[chat_id][user_id].append(message)
        print(f"✅ Добавлено {role}: {content[:30]}...")  # отладка

        # Оставляем только последние N сообщений
        if len(self.storage[chat_id][user_id]) > self.history_limit * 2:
            self.storage[chat_id][user_id] = self.storage[chat_id][user_id][-self.history_limit * 2:]

    def get_history(self, chat_id: int, user_id: int) -> List[dict]:
        """Возвращает историю сообщений"""
        messages = self.storage[chat_id][user_id].copy()
        print(f"📋 История для {user_id}: {len(messages)} сообщений")

        # Возвращаем без timestamp, только role и content
        result = []
        for msg in messages[-self.history_limit * 2:]:
            result.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return result

    def clear_history(self, chat_id: int, user_id: Optional[int] = None):
        """Очищает историю"""
        if user_id:
            self.storage[chat_id][user_id] = []
        else:
            self.storage[chat_id] = defaultdict(list)


conversation_history = ConversationHistory()