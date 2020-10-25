def allow_save(name):
	try:
	    not_allowed_format=['jpg','JPG','jpeg','JPEG','png','PNG','gif','GIF']
	    file,format_name=name.split('.')
	    if format_name in not_allowed_format:
	        return False
	    else:
	        return True
	except ValueError:
		return True