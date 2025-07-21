from .assistant import BaseAssistant
from ..CoTF import CoTF

class EvidenceAssistant(BaseAssistant):
    def __init__(self, config_file, client, thread_mode):
        self.add_config_names(['few_shot_examples', 'shots'])
        super().__init__(config_file=config_file, client=client, thread_mode=thread_mode, use_response_format=True)


    def init_conversation(self, question, cotf: dict):
        """
        init conversation: pass basic information
        - CoTF
        """
        try:
            for i in range(self.shots):
                self.add_message(message=self.few_shot_examples[i]['user'], role='user')
                self.add_message(message=self.few_shot_examples[i]['assistant'], role='assistant')

            self.add_message(message=f"Here is the question: {question}. \n Here is the chain of thoughts and facts: {cotf}.")

        except Exception as e:
            return e