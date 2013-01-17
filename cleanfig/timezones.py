from datetime import tzinfo,timedelta
"""
	Small timezone library
"""
class estTZ(tzinfo):
	# expand the tzinfo class to make a MST timezone object
	def __init__(self):
		pass
	def tzname(self, dt):
		return "EST"
	def utcoffset(self,dt):
		return timedelta(hours=-5)
	def dst(self, dt):
		return timedelta(0) # i care not for DST

class cstTZ(tzinfo):
	# expand the tzinfo class to make a MST timezone object
	def __init__(self):
		pass
	def tzname(self, dt):
		return "CST"
	def utcoffset(self,dt):
		return timedelta(hours=-6)
	def dst(self, dt):
		return timedelta(0) # i care not for DST

class mstTZ(tzinfo):
	# expand the tzinfo class to make a MST timezone object
	def __init__(self):
		pass
	def tzname(self, dt):
		return "MST"
	def utcoffset(self,dt):
		return timedelta(hours=-7)
	def dst(self, dt):
		return timedelta(0) # i care not for DST

class pstTZ(tzinfo):
	# expand the tzinfo class to make a MST timezone object
	def __init__(self):
		pass
	def tzname(self, dt):
		return "MST"
	def utcoffset(self,dt):
		return timedelta(hours=-8)
	def dst(self, dt):
		return timedelta(0) # i care not for DST

class utcTZ(tzinfo):
	# also expland tzonfo to create a UTC timezone object
	def __init__(self):
		pass
	def tzname(self, dt):
		return "UTC"
	def utcoffset(self,dt):
		return timedelta(hours=0)
	def dst(self, dt):
		return timedelta(0) # i care not for DST


