import os

class Plugin(object):
	plugins = {}
	paths = []

	def __init__(self):
		"""
		Instantiate a new Plugin collection, note that the plugins and
		loading path are stored in class variables, so you only need to
		set it once; ideally from the subclass' initializer:

		```
		class MyCollection(Plugin):
			paths = [ 'path.to.plugins' ]
		```

		"""
		if self.paths and not self.plugins:
			self.refresh()

	def addPath(self, path):
		"""
		Add a search path to the plugin collection and initiate
		a re-scan of plugins

		:param path str: The search pat to add
		"""
		self.paths.append(path)
		self.refresh()

	@classmethod
	def register(cls, plugin=None, **kwargs):
		"""
		Plugin registry function, this lets plugins register themselves,
		either:
		```
		@MyCollection.register
		class FirstPlugin(BaseClass):
			...
		```

		or 

		```
		@MyCollection.register(foo="bar")
		class FirstPlugin(BaseClass):
			...
		```
		"""
		def wrapper(plugin):
			cls.doRegister(plugin, **kwargs)
			return plugin

		if plugin is None:
			def decorator(plugin):
				return wrapper(plugin)
			return decorator
		else:
			return wrapper(plugin)


	@classmethod
	def doRegister(cls, plugin, **kwargs):
		"""
		This method is what does the actual registering of the class,
		override this (and the instantiation method) in a subclass
		if you need to store different properties.
		"""
		name = plugin.__name__
		if 'name' in kwargs:
			name = kwargs['name']

		if not name in cls.plugins.keys():
			cls.plugins[name] = { 'class': plugin, 'args': kwargs }

	def refresh(self):
		"""
		Refresh plugins, this checks the configured plugin paths for new
		plugins. Note that despite its name, it will not refresh the
		parameters of the already configured plugins.

		"""
		for base in self.paths:
			path = os.path.join(*base.split('.'))

			if os.path.exists(path):
				for fn in os.listdir(path):
					fullpath = os.path.join(path, fn)

					if os.path.isfile(fullpath) and fn.endswith('.py') and not fn.startswith('__'):
						__import__('.'.join([ base, fn[:-3] ]), fromlist=[ '*' ])
			else:
				__import__(base, fromlist = [ '*' ])

	def instance(self, name, config = {}):
		"""
		Instantiate a named plugin
		"""
		if name in self.plugins:
			return self.plugins[name]['class'](**config)

		return None
