import tkinter as tk
from tkinter import scrolledtext, ttk
import google.generativeai as genai

# Paste your API key here
API_KEY = "AIzaSyB0vpr_dZpdJn1-4RovFBYWSMTOpuFY3rY"

# Configure PaLM API
genai.configure(api_key=API_KEY)

import requests
from bs4 import BeautifulSoup

def scrape_bbc_sport():
    url = "https://www.bbc.com/sport/football"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch BBC Sport Football page.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    
    # Find all article links
    for item in soup.find_all("a", class_="ssrcss-zmz0hi-PromoLink exn3ah91"):
        headline_tag = item.find("p", class_="ssrcss-1b1mki6-PromoHeadline exn3ah96")
        
        if headline_tag:
            title = headline_tag.get_text(strip=True)
            articles.append({"title": title, "summary": ""})

    return articles  # Return first 5 headlines

# The Athletic Scraper
def scrape_athletic():
    # The URL of The Athletic's soccer page
    url = "https://theathletic.com/football/"  # Replace with the actual URL if different
    
    # Get the page HTML
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return []

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all article containers
    article_containers = soup.find_all("div", class_="Content_ImageTopContainer__w1zRD")
    article_containers += soup.find_all("div", class_="sc-bdcc51ff-0 fhcCuR")

    news_list = []

    for container in article_containers:
        # Extract the title
        title_tag = container.find("h4", class_="sc-4ec04b8c-0 fYdLvv")
        if not title_tag:
            title_tag = container.find("p", class_="sc-4ec04b8c-0 bCWkTB")
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        # Extract the summary
        summary_tag = container.find("p", class_="sc-4ec04b8c-0 kLfCus")
        if not summary_tag:
            summary_tag = container.find("p", class_="sc-4ec04b8c-0 bCWkTB")
        summary = summary_tag.get_text(strip=True) if summary_tag else "No summary found"

        news_list.append({"title": title, "summary": summary})

    return news_list

def scrape_onefootball_real_madrid():
    # The URL of OneFootball's Real Madrid news page
    url = "https://onefootball.com/en/team/real-madrid-26/news"
    
    # Get the page HTML
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return []

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    news_list = []

    def extract_articles(soup):
        articles = soup.find_all("li", class_=lambda x: x and x.startswith("Gallery_gallery__teaser"))
        for article in articles:
            title_tag = article.find("p", class_="NewsTeaser_teaser__title__OsMxr")
            summary_tag = article.find("p", class_="NewsTeaser_teaser__preview__ZRFyi")
            title = title_tag.get_text(strip=True) if title_tag else "No title found"
            summary = summary_tag.get_text(strip=True) if summary_tag else "No summary found"
            news_list.append({"title": title, "summary": summary})

    # Extract articles from the initial page
    extract_articles(soup)

    return news_list

# Test the scraper
#news_articles = scrape_onefootball_real_madrid() + scrape_athletic() + scrape_bbc_sport()
#print(news_articles)  # Should print a list of dictionaries with title + link

def summarize_news(news_articles):
    news_text = "\n".join([f"{idx+1}. {article['title']}" for idx, article in enumerate(news_articles)])
    prompt = f"Summarize the following soccer news. Seperate the summary into 3 paragraphs. First focus on Real Madrid news. Then tell me about any significant transfers. Finally tell me any scores you find of big games and any other news that is important. Be specific about what happened and the scores if possible:\n\n{news_text}"    
    
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    response = model.generate_content(prompt)

    # Extract the generated summary text
    summary_text = response.candidates[0].content.parts[0].text

    return summary_text

def scrape_and_summarize():
    news_articles = []
    if bbc_var.get():
        news_articles += scrape_bbc_sport()
    if athletic_var.get():
        news_articles += scrape_athletic()
    if onefootball_var.get():
        news_articles += scrape_onefootball_real_madrid()
    
    summary = summarize_news(news_articles)
    return summary

def display_summary():
    root.update_idletasks()
    summary = scrape_and_summarize()
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, summary)

# Create the main window
root = tk.Tk()
root.title("Soccer News Summary")

# Apply dark mode
root.configure(bg='#2e2e2e')
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', background='#2e2e2e', foreground='white')
style.configure('TCheckbutton', background='#2e2e2e', foreground='white')
style.configure('TLabel', background='#2e2e2e', foreground='white')
style.configure('TFrame', background='#2e2e2e')

# Create checkbuttons for selecting sources
bbc_var = tk.BooleanVar(value=True)
athletic_var = tk.BooleanVar(value=True)
onefootball_var = tk.BooleanVar(value=True)

bbc_check = ttk.Checkbutton(root, text="BBC Sport", variable=bbc_var)
athletic_check = ttk.Checkbutton(root, text="The Athletic", variable=athletic_var)
onefootball_check = ttk.Checkbutton(root, text="OneFootball", variable=onefootball_var)

bbc_check.pack(pady=5)
athletic_check.pack(pady=5)
onefootball_check.pack(pady=5)

# Create a button to scrape and summarize news
scrape_button = ttk.Button(root, text="Scrape and Summarize News", command=display_summary)
scrape_button.pack(pady=10)

# Create a scrolled text widget to display the summary
summary_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30, bg='#1e1e1e', fg='white', insertbackground='white')
summary_text.pack(pady=10)

# Run the application
root.mainloop()
