cmd_list = []
cmd_resp_list = []
text_list = []
text_resp_list = []
file_list = []
file_resp_list = []
image_list = []
image_resp_list = []
unknown_resp_list = []

class CommandHandler:
    def __init__(self, command: str, response: str):
        self.command_text = command 
        self.response = response
        self.__add_commandHandler()

    def __add_commandHandler(self):
        cmd_list.append("/" + self.command_text)
        cmd_resp_list.append(self.response)

class TextFileHandler:
    def __init__(self, text: str, file):
        self.text = text 
        self.response = file
        self.__add_fileHandler()

    def __add_fileHandler(self):
        file_list.append(self.text)
        file_resp_list.append(f"docu:{self.response}")

class CommandFileHandler:
    def __init__(self, command: str, file):
        self.text = command 
        self.response = file
        self.__add_fileHandler()

    def __add_fileHandler(self):
        file_list.append("/" + self.text)
        file_resp_list.append(f"docu:{self.response}")

class TextImageHandler:
    def __init__(self, text: str, file):
        self.text = text
        self.response = file 
        self.__add_imageHandler()

    def __add_imageHandler(self):
        image_list.append(self.text)
        image_resp_list.append(f"img:{self.response}")

class CommandImageHandler:
    def __init__(self, text: str, file):
        self.text = text
        self.response = file 
        self.__add_imageHandler()

    def __add_imageHandler(self):
        image_list.append("/" + self.text)
        image_resp_list.append(f"img:{self.response}")

class TextHandler:
    def __init__(self, text: str, response: str):
        self.tts = text
        self.resp = response 
        self.__add_textHandler()

    def __add_textHandler(self):
        text_list.append(self.tts)
        text_resp_list.append(self.resp)

class UnknownHander:
    def __init__(self, response):
        self.response = response 
        self.__add_unknownHandler()

    def __add_unknownHandler(self):
        unknown_resp_list.append(self.response)
        
