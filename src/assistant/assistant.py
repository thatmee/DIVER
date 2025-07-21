import json
from abc import ABC, abstractmethod
from openai import NotFoundError
from logging import getLogger
from src.utils import ConfigManageMixin

logger = getLogger(__name__)

class BaseAssistant(ABC, ConfigManageMixin):
    def __init__(self, config_file, client, thread_mode, use_json_schema_file=False, use_response_format=False):
        """
        - thread_mode: 'holding' or 'sep_conv'
        """
        self.config_file = config_file
        self.thread_mode = thread_mode
        self.client = client
        self.add_config_names(['assistant_name', 'instructions', 
                               'model', 'assistant_id'])
        if thread_mode == 'holding':
            self.add_config_names(['thread_id'])

        if use_json_schema_file and use_response_format:
            raise ValueError("json_schema_file and response_format cannot be used at the same time.")
        
        if use_json_schema_file:
            self.add_config_names(['json_schema_file'])
        elif use_response_format:
            self.add_config_names(['response_format'])
        else:
            self.response_format = None

        self.load_config(config_file=config_file)

        if use_json_schema_file:
            with open(self.json_schema_file) as f:
                response_schema = json.load(f)
            self.response_format = {
                "type": "json_schema",
                "json_schema": response_schema
            }

    def __create_assistant(self):
        # create new assistant
        assistant = self.client.beta.assistants.create(
            name=self.assistant_name,
            instructions=self.instructions,
            model=self.model,
            response_format=self.response_format
        )
        return assistant
    
    
    def __create_thread(self):
        self.thread = self.client.beta.threads.create()
        self.thread_id = self.thread.id


    def __delete_thread(self):
        try:
            del_response = self.client.beta.threads.delete(self.thread_id)
        except NotFoundError as e:
            logger.warning(f"handling exception and continue: {e}")
            return None
        return del_response



    def update_assistant(self, **kwargs):
        self.client.beta.assistants.update(
            assistant_id=self.assistant_id,
            **kwargs
        )

    def add_message(self, message, role='user'):
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=message
        )
        return message

    def respond(self):
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        if run.status == 'completed': 
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
            response = messages.data[0].content[0].text.value
            if self.response_format is not None:
                response = json.loads(response)
                
        else:
            logger.info(f"run status: {run.status}")
            response = 'No response. run status: ' + run.status

        return response

    
    def clear_history_messages(self):
        # clear history messages
        thread_messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        for message in thread_messages.data:
            logger.info(f"delete message: {message.id}")
            try:
                self.client.beta.threads.messages.delete(message_id=message.id, thread_id=self.thread.id)
            except NotFoundError as e:
                logger.warning(f"handling exception and continue: {e}")
                continue


    def load_assistant(self):
        try:
            # load assistant
            self.assistant = self.client.beta.assistants.retrieve(self.assistant_id)
            self.assistant_id = self.assistant.id
        except Exception as e:
            logger.warning(f"handling exception: {e}")
            self.assistant = self.__create_assistant()
            self.assistant_id = self.assistant.id
            self.save_config()


    def load_thread(self):
        if self.thread_mode == 'holding':
            try:
                self.thread = self.client.beta.threads.retrieve(self.thread_id)
            except Exception as e:
                logger.warning(f"handling exception: {e}")
                self.__create_thread()
                self.save_config()

        elif self.thread_mode == 'sep_conv':
            self.__create_thread()


    def clear_thread(self):
        if self.thread_mode == 'holding':
            logger.warning("You are using holding thread mode. Are you sure you want to clear the thread? [yes/no]")
            input_str = input()
            if input_str == 'yes':
                self.__delete_thread()
                self.save_config()
            else:
                logger.info("Cancel the operation.")
        elif self.thread_mode == 'sep_conv':
            self.__delete_thread()

    
    def refresh_thread(self):
        self.__create_thread()
        self.save_config()


    @abstractmethod
    def init_conversation(self):
        pass