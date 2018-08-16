import requests
import traceback
import configAxisMeme as config
import random

def get_meme_hyperlink(text):

	template_id = random.choice(config.template_ids)

	if "sacred highness exorcism" in text.lower():
		template_id = config.template_id_sacred_highness_exorcism
	if "sacred exorcism" in text.lower():
		template_id = config.template_id_sacred_exorcism
	if "god blow" in text.lower():
		template_id = config.template_id_god_blow
	if "god requiem" in text.lower():
		template_id = config.template_id_god_requiem

	text0 = ""
	text1 = text
	payload = {"username":config.username, "password":config.password, "template_id":template_id, "text0":text0, "text1":text1, "max_font_size":config.max_font_size}

	url = "https://api.imgflip.com/caption_image"
	try:
		req = requests.post(url, data=payload)
		result = req.json()
		if result["success"]:
			return "["+random.choice(config.phrases)+"]("+result["data"]["url"]+")"
		else:
			raise RuntimeError(result["error_message"])
	except:
		traceback.print_exc()
		return "Sorry, it seems like an error has ocurred! We will look into it!"
