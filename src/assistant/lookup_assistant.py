from .assistant import BaseAssistant


class LookupAssistant(BaseAssistant):
    def __init__(self, config_file, client, thread_mode):
        super().__init__(config_file=config_file, client=client, thread_mode=thread_mode, use_json_schema_file=True)

    def init_conversation(self, db_schema):
        """
        init conversation: pass basic information
        - db_schema
        """
        
        try:
            self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=f"here is the schema of the database: {db_schema}"
            )
        except Exception as e:
            return e