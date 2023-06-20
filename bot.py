import telebot
import json
import re
import nltk
import random
from sklearn.feature_extraction.text import CountVectorizer as CV
#from sklearn.linear_model import LogisticRegression as LR
from sklearn.ensemble import RandomForestClassifier as RFC
#from sklearn.neural_network import MLPClassifier as MLPC
bot=telebot.TeleBot('5528752930:AAEpUy5_sRdXhZnN1zSbDcPZ9R15X6hFDho')

filesavename='history.json'
filename='big_bot_config.json'

with open(filename, encoding='utf-8') as f:
	contents=json.load(f)

def write_history(text):
	format_text=get_format_text(text)
	with open(filesavename, 'a', encoding='utf-8') as f:
		f.write(format_text)

def get_format_text(text):
	return f'"{text}",\n'

def vectorizer_ml (x, swich=False):
	if swich:
		global vectorizer
		vectorizer=CV()
		vectorizer.fit(x)
	else:
		return vectorizer.transform(x)



def get_intent(text):
	for intent, count in contents['intents'].items():
		for example in count['examples']:
			if is_match(text, example):
				return intent

def get_intent_ml(text):
	vec_text=vectorizer_ml([text])
	intent = model.predict(vec_text)[0]
	return intent

def filter_text(text):
	text=text.lower()
	pattern=r'[^\w\s]'
	text=re.sub(pattern, '',text)
	return text

def is_match(text1, text2):
	text1=filter_text(text1)
	text2=filter_text(text2)
	if text1.find(text2)!=-1 or text2.find(text1)!=-1 :
		return True
	return levinstain_distance(text1,text2)

def levinstain_distance(text1,text2):
	distance = nltk.edit_distance(text1, text2)
	length = (len(text1)+len(text2))/2
	score=distance/length
	return score<0.4

 
def data_prepare(contents):
	x=[]#phrase
	y=[]#intents
	for intent, examples in (contents['intents']).items():
		for example in examples['examples']:
			x.append(example)
			y.append(intent)
	return x, y


def model_condition (contents):
	global model
	x,y=data_prepare(contents)
	#векторизация:
	vectorizer_ml(x, True)
	#create model:
	model = RFC()
	vec_x=vectorizer_ml(x)
	model.fit(vec_x, y)
	print (model.score(vec_x, y))

def chek_and_save_history_and_get_priority_intent(text, intent):
	if text.find('Моя історія:')!=-1 or intent=='my_history' or	levinstain_distance('Моя історія:',text[0:12]) or sentenses(text) :
		write_history(text)
		return 'my_history'


def sentenses (text):
	count_sentenses=text.count('.')+text.count('!')+text.count('?')+text.count(';')+text.count(':')
	if count_sentenses>=3:
		return True


@bot.message_handler(commands=['start'])
def start (message):
	if message.from_user.first_name != None and message.from_user.first_name.lower() != 'first_name':
		mess=f'Вітаю! <b>{message.from_user.first_name}</b>, мене звати Кіра і я розповідаю різноманітні дивацтва які роблять мої користувачі. Також я можу анонімно зберігти вашу історію і можу розповісти її іншим якщо ви забажаєте. Напишить "Моя історія:" на початку меседжа і все що ви розповісте буде збережено. Напишіть "розкажи історію" і я розповім. Також я можу підтримувати нескладний діалог.'
	else:
		mess = f'Вітаю! Мене звати Кіра і я розповідаю різноманітні дивацтва які роблять мої користувачі. Також я можу анонімно зберігти вашу історію і можу розповісти її іншим якщо ви забажаєте. Напишить "Моя історія:" на початку меседжа і все що ви розповісте буде збережено. Напишіть "розкажи історію" і я розповім. Також я можу підтримувати нескладний діалог.'

	bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler()
def get_user_text(message):
	text = str(message.text)
	intent = get_intent(text)

	if not intent:
		intent=get_intent_ml(text)

	intent_priority = chek_and_save_history_and_get_priority_intent(text, intent)

	if intent_priority:
		intent=intent_priority

	if intent:
		responses = contents['intents'][intent]['responses']
		mess=random.choice(responses)
		bot.send_message(message.chat.id, mess, parse_mode='html')
	
	print(intent)

	 






if __name__=="__main__":
	model_condition (contents)
	bot.polling(none_stop=True)
