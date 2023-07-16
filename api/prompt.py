import os

MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default=10))

with open("/Users/lucienlin/pyProjects/line-ai/api/memory.txt", "r") as f:
    memory = f.read()


class Prompt:
    def __init__(self):
        self.message = [{"role": "system", "content": memory}]

    def add_ai_msg(self, text):
        if len(self.message) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.message.append({"role": "assistant", "content": text})

    def add_user_msg(self, text):
        if len(self.message) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.message.append({"role": "user", "content": text})

    def remove_msg(self):
        self.message.pop(1)

    def generate_prompt(self):
        return self.message
