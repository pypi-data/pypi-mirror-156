import requests, json, time
from yungestgram.exceptions import InvalidToken, TokenUnverificable
from yungestgram.handlers import *




class ygBot:
    def __init__(self, token: str, output: bool = False):
        self.btoken = token
        is_token_valid = self.__validate_token()
        if is_token_valid == False:
            raise InvalidToken("Token does not exist!")
        if output == True:
            print(self.__getme())
            print(self.__getupdates())

    def __validate_token(self):
        resp = requests.get(f"https://api.telegram.org/bot{self.btoken}/getme").status_code
        if resp == 404:
            return False 
        elif resp == 200:
            return True 
        else: raise TokenUnverificable("The token could not be verified because of an error with telegram servers")

    def __getme(self):
        response = requests.get(f"https://api.telegram.org/bot{self.btoken}/getme").content.decode()
        js = self.__get_json_from_output(response)
        return js


    def __getupdates(self):
        updates = requests.get(f"https://api.telegram.org/bot{self.btoken}/getUpdates").content.decode()
        js = self.__get_json_from_output(updates)
        return js

    def __get_json_from_output(self, output):
        js = json.loads(output)
        return js

    def __get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        date = updates["result"][last_update]["message"]["date"]
        msg_id = updates["result"][last_update]["message"]["message_id"]
        chat_and_text = (text, chat_id)
        return (text, chat_id, date, msg_id)
        
    def send_same_message(self):
        text, chat, date, msg_id = self.__get_last_chat_id_and_text(self.__getupdates())
        url = f"https://api.telegram.org/bot{self.btoken}/sendMessage?text={text}&chat_id={chat}"
        print(url)
        requests.get(url)

    def delete_messages(self, until: int):
        texti, chat, date, msg_id = self.__get_last_chat_id_and_text(self.__getupdates())
        for i in range(0, until):
            requests.get(f"https://api.telegram.org/bot{self.btoken}/deleteMessage?chat_id={chat}&message_id={i}")
    
    def send_message(self, text: str):
        texti, chat, date, msg_id = self.__get_last_chat_id_and_text(self.__getupdates())
        url = f"https://api.telegram.org/bot{self.btoken}/sendMessage?text={text}&chat_id={chat}"
        requests.get(url)

    def send_document(self, document_name: str):
        texti, chat, date, msg_id = self.__get_last_chat_id_and_text(self.__getupdates())
        file = {'document':  open(f"{document_name}", 'rb')}
        r = requests.post(f'https://api.telegram.org/bot{self.btoken}/sendDocument?chat_id={chat}', files=file)

    def send_image(self, document_name: str):
        texti, chat, date, msg_id = self.__get_last_chat_id_and_text(self.__getupdates())
        file = {'photo':  open(f"{document_name}", 'rb')}
        r = requests.post(f'https://api.telegram.org/bot{self.btoken}/sendPhoto?chat_id={chat}', files=file)
        


    def start_activity(self):
        try:
            print("Starting bot...")
            last_textchat = (None, None, None, None)
            try:
                last_cache = open("temp.txt", "r").read()
            except FileNotFoundError:
                open("temp.txt", "w").close()
                last_cache = open("temp.txt", "r").read()

            while True:
                try:
                    text, chat, date, msg_id = self.__get_last_chat_id_and_text(self.__getupdates())
                    if last_cache == "":
                        last_cache = 0
                    if msg_id != int(last_cache):
                        if (text, chat, date, msg_id) != last_textchat:
                            

                            
                            for i in text_list:
                                if text == i:
                                    iid = text_list.index(i)
                                    response = text_resp_list[iid]
                                    print(response)
                                    self.send_message(response)

                            for i in file_list:
                                if text == i:
                                    iid = file_list.index(i)
                                    response = file_resp_list[iid]
                                    response = str(response).removeprefix("docu:")
                                    print("docu")
                                    self.send_document(response)

                            for i in image_list:
                                if text == i:
                                    iid = image_list.index(i)
                                    response = image_resp_list[iid]
                                    response = str(response).removeprefix("img:")
                                    print("img")
                                    self.send_image(response)

                            for i in cmd_list:
                                if text == i:
                                    iid = cmd_list.index(i)
                                    response = cmd_resp_list[iid]
                                    print(response)
                                    self.send_message(response)

                            if text not in text_list and text not in cmd_list and text not in file_list and text not in image_list:
                                response = unknown_resp_list[0]
                                print(response)
                                self.send_message(response)


                            last_textchat = (text, chat, date, msg_id)
                            open("temp.txt", "w").write(f"{msg_id}")
                    time.sleep(0.5)
                except IndexError:
                    pass
        except KeyboardInterrupt:
            pass

