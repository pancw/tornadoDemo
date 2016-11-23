# module jsonHelper
# help build json return strings
import json
def success(data):
	"""basic success json"""
	respond_data={"status":"success","data":data}
	return json.dumps(respond_data)

def fail(data):
	"""basic fail json"""
	respond_data={"status":"fail","data":data}
	return json.dumps(respond_data)
	
def failWithMessage(message):
	"""simple fail with message"""
	return fail({"message":message})