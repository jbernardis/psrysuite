

class Engineers():
	def __init__(self, rrserver):
		self.RRServer = rrserver
		j = rrserver.Get("getfile", {"dir": "data", "file": "engineers.txt"})
		if j is None:
			self.engineers = []

		if type(j) is list:
			self.engineers = sorted(j)
		else:
			self.engineers = sorted([n for n in j.split("\n") if len(n) > 0])

		self.ex = 0
		
	def save(self):
		self.RRServer.Post("engineers.txt", "data", self.engineers)	
		
	def contains(self, eng):
		return eng in self.engineers
	
	def add(self, eng):
		if self.contains(eng):
			return
		
		self.engineers = sorted(self.engineers + [eng])
		
	def delete(self, eng):
		if not self.contains(eng):
			return
		
		self.engineers.remove(eng)
		
	def __len__(self):
		return len(self.engineers)

	def __iter__(self):
		self.ex = 0
		return self
	
	def __next__(self):
		if self.ex >= len(self.engineers):
			raise StopIteration
		
		rv = self.engineers[self.ex]
		self.ex += 1
		return rv