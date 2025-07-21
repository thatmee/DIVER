from logging import getLogger
from typing import Any
from ..database_tool_box.engine.tool_parse_mixin import ToolParseMixin
logger = getLogger(__name__)

class CoTF(ToolParseMixin):
    def __init__(self):
        self.nlq_split = []
        self.draft_thoughts = []
        self.draft_facts = []
        self.tool_chain = {}
        self.cotf = {}
        self.step = 0

    def init_nlq_split(self, nlq_split):
        self.nlq_split = nlq_split
        self.cotf = {phrase: [] for phrase in nlq_split}
        self.tool_chain = {phrase: {"set": set(), "chain": []} for phrase in nlq_split}

    def record_thoughts(self, draft, have_analysis=True):
        self.draft_thoughts.append(draft)
        for phrase, thought in draft.items():
            if have_analysis:
                # didnt use dict.get() to check error when analysis is enabled
                analysis = thought['analysis']
            else:
                # use dict.get() to check if analysis is not provided
                analysis = thought.get('analysis', "")
                
            self.cotf[phrase].append({
                "step": self.step,
                "analysis": analysis,
                "tools_and_results": []
            })
        self.step += 1

    def record_facts(self, draft, step):
        self.draft_facts.append(draft)
        for phrase, facts in draft.items():
            self.cotf[phrase][step]['tools_and_results'] = facts

            tool_chain = []
            for fact in facts:
                if fact['tool'] == 'none':
                    continue
                value = fact['params'].get('value', None)
                tool_str = self._get_tool_string(fact['tool'], fact['params']['table'], fact['params']['column'], value)
                tool_chain.append(tool_str)
            self.tool_chain[phrase]["chain"].append(tool_chain)
            self.tool_chain[phrase]["set"] = self.tool_chain[phrase]["set"].union(set(tool_chain))


    def __len__(self):
        return len(self.draft_records)
    
    # def organize(self):
    #     if len(self.draft_thoughts) < len(self.draft_facts):
    #         logger.warn("The number of thoughts is less than the number of facts.")

    #     raw_text_split = self.draft_thoughts[0]['raw_text_split']
    #     cotf_list = [[]*len(raw_text_split)]

    #     # update every step info
    #     for i, step_response in enumerate(self.draft_thoughts):
    #         # obtain the facts of the current step
    #         if i < len(self.draft_facts):
    #             current_facts = self.draft_facts[i]
    #             facts_text = [fact['raw_text'] for fact in current_facts]
    #         else:
    #             current_facts = []
    #             facts_text = []

    #         for j, ana_per_split in enumerate(step_response['draft_thoughts']):
    #             step_record = {
    #                 "step": i+1,
    #                 "analysis": ana_per_split['analysis']
    #             }

    #             # check if current text call any tool
    #             current_text = ana_per_split['raw_text']
    #             if current_text in facts_text:
    #                 step_record["tool_and_result"] = current_facts[facts_text.index(current_text)]['return_lookup']

    #             # text split may change, to enhance.
    #             if j < len(cotf_list):
    #                 cotf_list[j].append(ana_per_split)

    #     self.cotf = {}
    #     for i, cotf in enumerate(cotf_list):
    #         self.cotf[raw_text_split[i]] = cotf
