from domain_check import domain_check
from breakdown_agent import break_down
from gemini_pdf_extractor import extract_pdf_to_text_using_gemini
from meeting_transcriptions import extract_text_from_meeting_transcriptions
from analysis_agent import analysis_agent
import asyncio
import json

class DomainNotAllowedError(Exception):
    pass

finance_file_path = "Consolidated and Standalone tcs.pdf"
output_file_path = "data.txt"
meeting_transcriptions_file_path = "Transcript of the Q1 2024-25 Earnings Conference Call held on Jul 11, 2024.pdf"
# extract_pdf_to_text_using_gemini(finance_file_path, output_file_path)
# extract_text_from_meeting_transcriptions(meeting_transcriptions_file_path, output_file_path)



question = '''Analyze the financial reports and transcripts for the last three quarters and provide a qualitative forecast for the upcoming quarter. Your forecast must identify key financial trends (e.g., revenue growth, margin pressure), summarize management's stated outlook, and highlight any significant risks or opportunities mentioned'''


async def anlyse_user_question(question):
    checking_domain =  await domain_check(question)
    checking_domain = json.loads(checking_domain)
    if checking_domain['is_finance']:
        sub_question_json = json.loads(await break_down(question))
        reasoning_prompt = ''
        index = 1
        for question in sub_question_json['questions']:
            reasoning_prompt = reasoning_prompt + str(index) + "." + question + '\n'
            index+=1
        reasoning_prompt = "SPECIFIED QUESTIONS:"+ "\n" + reasoning_prompt
        with open(output_file_path, "r", encoding="utf-8") as f:
            data_prompt = f.read()
        data_prompt = "BELOW IS FINANCE INFO AND MANAGEMENT DISCUSSIONS ABOUT STOCK:" + "\n" + data_prompt
        analysis_prompt = reasoning_prompt + data_prompt
        return await analysis_agent(analysis_prompt)
    else:   
        raise DomainNotAllowedError("Only questions related to finance domains are allowed")


if __name__ == "__main__":
    print(asyncio.run(maanlyse_user_questionin(question)))
