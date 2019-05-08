import random
import re
import numpy as np
import gensim
from keras.callbacks import LambdaCallback
from keras.layers.recurrent import LSTM
from keras.layers.embeddings import Embedding
from keras.layers import Dense, Activation, TimeDistributed
from keras.models import Sequential, load_model
from keras.utils.data_utils import get_file
import telebot

g_temperature = 0.6
g_responserate = 1.0

class EpochLogger(gensim.models.callbacks.CallbackAny2Vec):
  def __init__(self):
    self.epoch = 0

  def on_epoch_begin(self, model):
    pass

  def on_epoch_end(self, model):
    if self.epoch % 5 == 0:
      print("Epoch #{} end".format(self.epoch))
    self.epoch += 1

wordModel = gensim.models.Word2Vec.load("models/word2vecModel.model")

def word2idx(word):
  return wordModel.wv.vocab[word].index
def idx2word(idx):
  return wordModel.wv.index2word[idx]

def sample(preds, temperature=1.0):
  if temperature <= 0:
    return np.argmax(preds), preds[np.argmax(preds)]
  preds = np.asarray(preds).astype('float64')
  preds = np.log(preds) / temperature
  exp_preds = np.exp(preds)
  preds = exp_preds / np.sum(exp_preds)
  probas = np.random.multinomial(1, preds, 1)
  return np.argmax(probas), preds[np.argmax(probas)]

def generate_next(text, num_generated=30):
  word_idxs = [word2idx(word) for word in text.lower().split()]
  for i in range(num_generated):
    prediction = model.predict(x=np.array(word_idxs))
    idx, _ = sample(prediction[-1][-1], temperature=0.7)
    word_idxs.append(idx)
  return ' '.join(idx2word(idx) for idx in word_idxs)

def on_epoch_end(epoch, _):
  if epoch % 1 == 0:
    print('\nGenerating text after epoch: %d' % epoch)
    texts = [
      'jeg har',
      'når går dokker',
      'æ kan',
      'tja',
    ]
    for text in texts:
      sample = generate_next(text)
      print('%s... -> %s' % (text, sample))
    print(model.evaluate(x=test_x, y=test_y, batch_size=128))

def generateNext2(text, num_generated=30, temperature=0):
  word_idxs = [word2idx(word) for word in text.lower().split()]
  prbs = [1.0 for word in text.lower().split()]
  for i in range(num_generated):
    inpt = np.zeros([1, len(word_idxs)], dtype=np.int32)
    for i, idx in enumerate(word_idxs):
      inpt[0, i] = idx
    prediction = lstmModel.predict(x=inpt)
    idx, prb = sample(prediction[-1][-1], temperature=temperature)
    word_idxs.append(idx)
    prbs.append(prb)
  return " ".join(idx2word(idx) for idx in word_idxs)

lstmModel = load_model("models/lstmModel.h5")

print(wordModel.wv.most_similar("chunnoo"))
print(generateNext2("ok [message]", temperature=0.6))


def formatInput(message):
    content = message.lower()
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
    content = re.sub("\n+", " ", content)
    content += " [message]"
    content = re.sub(r" +", " ", content)
    content = content.lower()
    return content

def formatOutput(message):
    content = message.lower()
    content = re.sub(r"\[website\]", "https://github.com/chunnoo/telegramBot", content)

    content = re.sub(r"\[time\]", str(random.randint(10, 24)) + ":00", content)

    content = re.sub(r"\s*\[emojimisc\]", "💩", content)
    content = re.sub(r"\s*\[emojismile\]", "😃", content)
    content = re.sub(r"\s*\[emojilaugh\]", "😁", content)
    content = re.sub(r"\s*\[emojisurprised\]", "😮", content)
    content = re.sub(r"\s*\[emojisad\]", "😥", content)
    content = re.sub(r"\s*\[emojiangry\]", "😡", content)
    content = re.sub(r"\s*\[emojikiss\]", "😘", content)
    content = re.sub(r"\s*\[emojilove\]", "❤️", content)
    content = re.sub(r"\s*\[emojithumbup\]", "👍", content)
    content = re.sub(r"\s*\[emojithumbdown\]", "👎", content)
    content = re.sub(r"\s*\[emojifingercircle\]", "👌", content)
    content = re.sub(r"\s*\[emojimiddlefinger\]", "🖕", content)
    content = re.sub(r"\s*\[emojisilent\]", "😐", content)
    content = re.sub(r"\s*\[newline\]", "\n", content)
    content = re.sub(r"\s*\[ellipsis\]", "...", content)
    content = re.sub(r"\s*\[colon\]", ":", content)
    content = re.sub(r"\[at\]\s*", "@", content)
    content = re.sub(r"\s*\[dash\]\s*", "-", content)
    content = re.sub(r"\[quotationmark\]", "\"", content)
    content = re.sub(r"\s*\[apostrophe\]\s*", "'", content)
    content = re.sub(r"\[leftbracket\]\s*", "(", content)
    content = re.sub(r"\s*\[rightbracket\]", ")", content)
    content = re.sub(r"\s*\[period\]", ".", content)
    content = re.sub(r"\s*\[questionmark\]", "?", content)
    content = re.sub(r"\s*\[exclamationmark\]", "!", content)
    content = re.sub(r"\s*\[comma\]", ",", content)
    content = re.sub(r"\[misc\]", "#", content)
    content = re.sub(r"\[number\]", lambda m: str(random.randint(0,10)), content)
    content = re.sub(r"\[special\]\s*", "#", content)
    return content.split("[message]")[1]

bot = telebot.TeleBot("883106682:AAFGG3D0t3YtUZ5v4yuMUCs_mLudncC5XQA")

@bot.message_handler(commands=["temperature"])
def temperatureCommandHandler(message):
    global g_temperature
    try:
        g_temperature = float(message.text.split()[1])
        bot.send_message(message.chat.id, "Temperature changed to " + str(g_temperature))
    except:
        bot.send_message(message.chat.id, "Failed to change temperature")

@bot.message_handler(commands=["responserate"])
def responserateCommandHandler(message):
    global g_responserate
    try:
        g_responserate = float(message.text.split()[1])
        bot.send_message(message.chat.id, "Response rate changed to " + str(g_responserate))
    except:
        bot.send_message(message.chat.id, "Failed to change response rate")

@bot.message_handler(func=lambda m: True)
def responseHandler(message):
    print(message.chat.type)
    if random.random() < g_responserate:
        try:
            formatedInput = formatInput(message.text)
            print("input:", formatedInput)
            #bot.send_message(message.chat.id, formatetdInput)
            output = generateNext2(formatedInput, temperature=g_temperature)
            print("output:", output)
            formatedOutput = formatOutput(output)
            if formatedOutput != "":
                bot.send_message(message.chat.id, formatedOutput)
        except Exception as e:
            print(e)

bot.polling()