from transformers import MarianMTModel, MarianTokenizer
from datetime import datetime
import xml.etree.ElementTree as ET

model_name = "Helsinki-NLP/opus-mt-ru-uk"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

with open("transcript_ru.txt", "r", encoding="utf-8") as f:
    paragraphs = [line.strip() for line in f if line.strip()]

translated_paragraphs = []
for paragraph in paragraphs:
    tokens = tokenizer(paragraph, return_tensors="pt", truncation=True, padding=True)
    translated = model.generate(**tokens)
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    translated_paragraphs.append(translated_text)

FictionBook = ET.Element("FictionBook", xmlns="http://www.gribuser.ru/xml/fictionbook/2.0")
description = ET.SubElement(FictionBook, "description")
title_info = ET.SubElement(description, "title-info")
ET.SubElement(title_info, "genre").text = "fiction"
ET.SubElement(title_info, "author").append(ET.Element("nickname", text="Анонім"))
ET.SubElement(title_info, "book-title").text = "Незграбна Ганна (переклад)"
ET.SubElement(title_info, "date").text = datetime.now().strftime("%Y-%m-%d")
ET.SubElement(title_info, "lang").text = "uk"

body = ET.SubElement(FictionBook, "body")
for para in translated_paragraphs:
    p = ET.SubElement(body, "section")
    ET.SubElement(p, "p").text = para

tree = ET.ElementTree(FictionBook)
ET.indent(tree, space="  ", level=0)
tree.write("transcript_uk.fb2", encoding="utf-8", xml_declaration=True)
