from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import requests
from bs4 import BeautifulSoup
import lxml
from datetime import *
import os
import torch
import textwrap
from email.message import EmailMessage
import ssl
import smtplib

#Load model from Hugging Face Model Hub
tokenizer = AutoTokenizer.from_pretrained("VietAI/vit5-large-vietnews-summarization")  
model = AutoModelForSeq2SeqLM.from_pretrained("VietAI/vit5-large-vietnews-summarization")
model.to('cuda')

today = str(datetime.now().strftime("%Y-%m-%d")) #Today date 

num_chunks = 5 #Number of chunks to summarize 
number_of_news = 5  #Number of news to scrape from each URL
newspaper_url_list = ['https://vnexpress.net/kinh-doanh/quoc-te', 
                      'https://vnexpress.net/kinh-doanh/vi-mo']  #Original URL list to scrape from

# Setup prompt
begin_prompt = "vietnews: "  
end_prompt = " </s>"

def summarize(text, model, tokenizer):
    """
    A function that summarize an input text using a LLM model
    
    text: list of texts
    model: Hugging Face Model
    tokenizer: Tokenizer of that model

    return: list of summarization
    
    """

    texts = tokenizer(text, return_tensors="pt", padding = True).to('cuda')
    input_ids = texts['input_ids']
    attention_masks = texts['attention_mask']
    outputs = model.generate(
        input_ids=input_ids, attention_mask=attention_masks,
        max_length=256,
        early_stopping=True,
        num_beams = 20
    )
    return tokenizer.decode(outputs[0], skip_special_tokens = True, clean_up_tokenization_spaces = True)

url_list = [] #Contain the URLs
#Loop and scrape URL of the latest news on the original URL
for newspaper_url in newspaper_url_list:
    newspaper_html = requests.get(newspaper_url).text
    newspaper_soup = BeautifulSoup(newspaper_html, 'lxml')
    content = newspaper_soup.find('section', class_ = 'section section_container mt15')
    news_title = content.find_all('h2', class_ = 'title-news')
    for i, new_title in enumerate(news_title):
        if i == number_of_news:
            break
        new_url = new_title.find('a')['href']
        url_list.append(new_url)
        
news = {} #Contain the information about the news


for url in url_list:
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    #Title
    title = soup.find('h1', class_ = 'title-detail')
    if title == None:
      continue
    #Date
    date = soup.find('span', class_ = 'date').text
    day = str(datetime.strptime(date.split(', ')[1], '%d/%m/%Y').date())
    #if day != today:
        #continue
    #Body
    descript = soup.find('p', class_ = 'description').text 
    chunks = soup.find_all('p', class_ = 'Normal')
    chunks = [chunk.text for chunk in chunks]
    num = len(chunks) // num_chunks
    body = []
    for i in range(num_chunks):
      if i == 0:
        chunk = begin_prompt + descript + " ".join(chunks[(0+i)*num:(1+i)*num]) + end_prompt
      elif i == num_chunks - 1:
        chunk = begin_prompt + " ".join(chunks[(0+i)*num:]) + end_prompt
      else:
        chunk = begin_prompt + " ".join(chunks[(0+i)*num:(1+i)*num]) + end_prompt
      torch.cuda.empty_cache() 
      sum = summarize(chunk, model, tokenizer)
      body.append(sum)

    #Summarise here

    news[(title, url, day)] = body

# Send the summarization to customer emails
passwords = ''
sender = 'chinhnguyen.datus@gmail.com'
receivers = ['chinh210602@gmail.com','locson344@gmail.com']

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

for receiver in receivers:
  em = EmailMessage()
  em['From'] = sender
  em['To'] = receiver
  em['Subject'] = subject
  em.set_content(body)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
      smtp.login(sender, passwords)
      smtp.sendmail(sender, receiver, em.as_string())