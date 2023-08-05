from utils.get_urls import GetUrls
from utils.summarizer import Summarizer
from utils.scaper import Scaper
from utils.email_sender import EmailSender
import torch
from datetime import *


num_chunks = 5
begin_prompt = "vietnews: "  
end_prompt = " </s>"
father_urls = ['https://vnexpress.net/kinh-doanh/quoc-te', 
                'https://vnexpress.net/kinh-doanh/vi-mo']
number_of_childs = 1
model_name = "VietAI/vit5-large-vietnews-summarization"
device = "cuda" if torch.cuda.is_available() else "cpu"
today = str(datetime.now().strftime("%Y-%m-%d")) #Today date 

get_urls = GetUrls(father_urls)
child_urls = get_urls.getlist(number_of_childs)


scaper = Scaper()
data = scaper.scape(child_urls)

news = {}
summarizer = Summarizer(model_name, device)

for chunks in list(data.values()):
    num = len(chunks) // num_chunks
    body = []
    for i in range(num_chunks):
        if i == num_chunks - 1:
            chunk = begin_prompt + " ".join(chunks[(0+i)*num:]) + end_prompt
        else:
            chunk = begin_prompt + " ".join(chunks[(0+i)*num:(1+i)*num]) + end_prompt
        body.append(summarizer.summarize(chunk))
    news[tuple(data.keys())] = body


sender = ""
receivers = [""]
password = ""
subject = 'Daily Vietnamese News Summary %s' %today
body = """
Daily Vietnamese News Summary %s
""" %today
count = 1
for (title, url, date), texts in news.items():
  chunk_i = """
New number %s
Title: %s
URL: %s
Date: %s

Summary: 
"""%(count, title, url, date)
  for text in texts:
    chunk_i += "-" + text + '\n'
  body += chunk_i
  count += 1


email_sender = EmailSender()
EmailSender.send(sender, receivers, password, subject, body)