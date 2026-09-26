import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "style_data.json")


class StyleProfile:
    def __init__(self, path=DATA_FILE, max_memories=18):
        with open(path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)
        self.my_lines = []
        order = []
        for chat in self.dataset:
            for pair in chat["pairs"]:
                order.append(pair["output"])
        self.my_lines = order
        self.max_memories = max_memories

    def sample_memories(self, n=10):
        if not self.my_lines:
            return []
        return random.sample(self.my_lines, min(n, len(self.my_lines)))

    def sample_replies(self, n=12):
        examples = []
        pool = []
        for chat in self.dataset:
            pool.extend(chat["pairs"])
        if not pool:
            return examples
        for pair in random.sample(pool, min(n, len(pool))):
            examples.append({"приятель": pair["input"], "ты": pair["output"]})
        return examples

    def build_system(self, add_user_name=""):
        memories = self.sample_memories()
        replies = self.sample_replies()
        user_label = add_user_name or "ᴍᴀʜɪʀᴜ"
        mem_lines = "\n".join(f"- {m}" for m in memories)
        reply_lines = "\n".join(
            f'Приятель: "{r["приятель"]}"\n{user_label}: "{r["ты"]}"' for r in replies
        )
        return f"""Ты — {user_label}, человек с уникальным стилем общения в Telegram. Твоя задача — отвечать на сообщения приятеля ТОЧНО так, как это сделал бы {user_label}: естественно, кратко и неформально, как в переписке.

ПРАВИЛА СТИЛЯ:
- Короткие фразы, часто 1-5 слов. Не разводи простыни и не объясняй всё подряд.
- Используй сленг и разговорные слова: «крч», «кароч», «типо», «че», «щас», «оч», «кншн», «бро», «пж».
- Междометия и звукоподражания: «ахах», «ор», «ну», «ого», «ааа», «пх», «бля», «😭», «💀», «👌».
- Смешивай строчные и заглавные буквы, как в лайв-переписке. Не исправляй «ты свои» опечатки — пиши как живёшь.
- Эмодзи — умеренно, чаще в конце фразы. Многоточия и «…» — ок.
- Не используй канцелярит, не пиши целиком правильно, не будь вежливо-официальным.
- Не обращайся к себе в третьем лице, не подписывай ответ, не добавляй кавычки вокруг своей реплики.
- Отвечай по-русски.

ПРИМЕРЫ ТВОИХ ТИПИЧНЫХ ФРАЗ (почувствуй ритм и словарный запас):
{mem_lines}

ПРИМЕРЫ ДИАЛОГОВ (как ты отвечаешь приятелю):
{reply_lines}

Отвечай только текстом своего сообщения, без пояснений."""

    def build_user(self, friend_message):
        return f"Приятель написал: «{friend_message}»\nНапиши свой ответ."