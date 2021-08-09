from os import close, read
import re
import polib
import requests as req
from requests_oauthlib import OAuth1
from xml.etree.ElementTree import *


with open("NICT/sample.xml", "r") as en_file, open("NICT/sample.txt", "w") as outfile:
    en_content = en_file.read().splitlines()
    
    

    simpara_st, simpara_end = 9, -10
    title_st, title_end = 7, -8
    subtitle_st, subtitle_end = 10, -11
    tags = ('<para>', '<simpara>')
    para = tags[0]
    simpara = tags[1]
    
    

    # translate string with Machine Translation

    def translate_nict(source_text):
        NAME = ''
        KEY = ''
        SECRET = ''
        URL = ''
        TEXT = source_text
        consumer = OAuth1(KEY , SECRET)

        params = {
            'key': KEY,
            'name': NAME,
            'text': TEXT,
        } 

        request = req.post(URL, data=params, auth=consumer)
        result = request.json()
        return result['resultset']['result']['text']
    


    def translate_deepl(source_text):
        text = source_text
        url = ""
        auth_key = ""
        params = {
                    "auth_key": auth_key,
                    "text": text,
                    "source_lang": 'EN', 
                    "target_lang": 'JA'  
                }

        # パラメータと一緒にPOSTする
        request = req.post("https://api.deepl.com/v2/translate", data=params)
        result = request.json()
        return result["translations"][0]["text"]
    
    def close_tag(tag):
        close_tag = tag[0] + "/" + tag[1:]
        return close_tag

    def tag_content(string, tag, with_tag=False):

        end_tag = close_tag(tag)
        result = re.findall(r"{0}.+{1}".format(tag, end_tag), string)
        string = "".join(result)
        

        
        if with_tag:
            return string
        else:
            if tag in tags:
                separated = re.search(
                    "{0}(.*){1}".format(tag, end_tag), string)
                return separated.group(1)
                

    def tag_is_in(tags, content):
        for tag in tags:
            if tag in content:
                return True
        return False

    def matched_tag(tags, content):
        for tag in tags:
            if tag in content:
                return tag

    ### when there is no close tag in the line or the line starts with end tag #####band-aide fix; i know it's bad
    def no_content(string, tag):
        if not close_tag(tag) in string or string.startswith("</"):
            return True


    def translation_output_fmt(source, target_dl, target_nict):
        return "Source: " + source + "\n" + "DeepL: " + target_dl + "\n" + "NICT: " + target_nict + "\n"


    def translate_xml(en_content):
        for en in en_content:
            if tag_is_in(tags, en):
                tag = matched_tag(tags, en)
                if not no_content(en, tag):
                    translated_text_dl = translate_deepl(tag_content(en, tag))
                    translated_text_nict = translate_nict(tag_content(en, tag))
                    en = tag_content(en, tag)
                    print(translation_output_fmt(en, translated_text_dl, translated_text_nict), file=outfile)
                
###problem with starting </> (close tag) will mess up the program
    translate_xml(en_content)