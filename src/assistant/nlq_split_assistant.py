from .assistant import BaseAssistant


class NlqSplitAssistant(BaseAssistant):
    def __init__(self, config_file, client, thread_mode):
        super().__init__(config_file=config_file, client=client, thread_mode=thread_mode, use_response_format=True)

    def init_conversation(self, nlq):
        """
        init conversation: pass basic information
        - db_schema
        """
        
        try:
            self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=nlq
            )
        except Exception as e:
            return e