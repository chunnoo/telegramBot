import json
import re
import glob

#fileNames = ["Adrian Langseth", "Bjørnar", "Bro fist", "Buldrebønsjen", "Dokker va der", "Eila Lindstad", "elcyste", "Fæskårabbane 2019", "Jai ar ikke koken din", "Kretsboys"]
specialChars = set()

for fileName in glob.glob("jsonMessageDumps/*.log"):

    print("working on", fileName)

    messages = []
    with open(fileName, 'r') as file:
        line = file.readline()
        while line:
            linejson = json.loads(line)
            messages.append(linejson)
            line = file.readline()

    with open("convertedMessages/" + fileName.split("/")[1].split(".")[0] + ".txt", 'w') as file:
        for message in messages:
            if message["content"]:
                content = message["content"].lower()
                content = re.sub(r"\[", " [leftbracket] ", content)
                content = re.sub(r"\]", " [rightbracket] ", content)
                content = re.sub(r"(http[\w:/.?=+\-&\$%]+\b)", " [website] ", content)
                content = re.sub(r"\d\d:\d\d", " [time] ", content)

                content = re.sub(u"([😀😃😊😋☺️🙂😌😏😉😎])", " [emojismile] ", content)
                content = re.sub(u"([😁😂🤣😄😅😆])", " [emojilaugh] ", content)
                content = re.sub(u"([😮😯😦😧😨😱])", " [emojisurprised] ", content)
                content = re.sub(u"([😣😥😒😓😔😕☹️🙁😖😞😟😢😭😩])", "[emojisad]", content)
                re.sub(u"([😡😠🤬😤])", " [emojiangry] ", content)
                re.sub(u"([😘😗😙😚])", " [emojikiss] ", content)
                re.sub(u"([😍❤️🧡💜💕💞💖])", " [emojilove] ", content)
                re.sub(r"\<3", " [emojilove] ", content)
                re.sub(u"([👍👍🏻👍🏼👍🏽👍🏾👍🏿])", " [emojithumbup] ", content)
                re.sub(r"\(y\)", " [emojithumbup] ", content)
                re.sub(u"([👎👎🏻👎🏼👎🏽👎🏾👎🏿])", " [emojithumbdown] ", content)
                re.sub(u"([👌👌🏻👌🏼👌🏽👌🏾👌🏿])", " [emojifingercircle] ", content)
                re.sub(u"([🖕🖕🏻🖕🏼🖕🏽🖕🏾🖕🏿])", " [emojimiddlefinger] ", content)
                re.sub(u"([😐😑😶🙄🤐😳])", " [emojisilent] ", content)

                emojiReg = re.compile(u'['
                    u'\U0001F300-\U0001F64F'
                    u'\U0001F680-\U0001F6FF'
                    u'\U0001F1E6-\U0001F1FF'
                    u'\U00010000-\U0010FFFF'
                    u'\u2600-\u26FF\u2700-\u27BF]',
                    re.UNICODE)
                content = emojiReg.sub(" [emojimisc] ", content)
                content = re.sub("\n+", " [newline]\n", content)
                content = re.sub("\.\.+", " [ellipsis]\n", content)
                content = re.sub("\.", " [period]\n", content)
                content = re.sub("\?", " [questionmark]\n", content)
                content = re.sub("\!", " [exclamationmark]\n", content)
                content = re.sub(",", " [comma] ", content)
                content = re.sub(":", " [colon] ", content)
                content = re.sub("@", " [at] ", content)
                content = re.sub(r"\-", " [dash] ", content)
                content = re.sub("'", " [apostrophe] ", content)
                content = re.sub(r"[«»\"]", " [quotationmark] ", content)
                content = re.sub(r"[\(\{]", " [leftbracket] ", content)
                content = re.sub(r"[\)\}]", " [rightbracket] ", content)
                content = re.sub(r"([/*\^\-#\+&<>;=_%$])", " [misc] ", content)
                content = re.sub(r"(\d+)", " [number] ", content)
                content = re.sub(r"([\S\s])\1+", r"\g<1>\g<1>", content)
                content = re.sub("[òóоö]", "o", content)
                content = re.sub("[éèе]", "e", content)
                specialList = re.findall(r"([^a-zæøå\[\]\s])", content)
                for ch in specialList:
                    specialChars.add(ch)
                content = re.sub(r"([^a-zæøå\[\]\s])", " [special] ", content)
                content = re.sub("\n+", "\n", content)
                content += " [message]\n"
                content = re.sub(r" +", " ", content)
                file.write(content.lower())

print(list(specialChars))