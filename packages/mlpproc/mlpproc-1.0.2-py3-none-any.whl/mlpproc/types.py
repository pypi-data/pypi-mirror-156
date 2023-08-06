# """This contains the useful types
# Block and Command"""

# from typing import Any, Callable, Generic, TypeVar

# T = TypeVar("T")
# P = TypeVar("P")

# class WrappedFunction():
# 	"""A function with extra attributes,
# 	namely a help string and a short oneliner description"""
# 	func_type = Callable[..., Any]
# 	doc_short: str
# 	doc: str

# 	function: func_type

# 	def __init__(
# 		self: "WrappedFunction", function: func_type,
# 		doc_short: str, doc: str
# 	) -> None:
# 		"""Initializes the object, arguments:
# 		- function: the wrapped function
# 		- doc_short: a short (>60 chars) description
# 		- doc: a longer description (defaults to short if "")"""
# 		self.function = function
# 		self.doc_short = doc_short
# 		self.doc = doc
# 		if self.doc == "":
# 			self.doc = self.doc_short
# 		if self.doc == "" and function.__doc__ != None:
# 			self.doc = function.__doc__

# 	def __call__(self: "WrappedFunction", *args: P) -> T:
# 		return self.function(*args)


# class FinalAction(WrappedFunction):
# 	"""A type for commands. The two function arguments are
# 	- the preprocessor
# 	- the text to process"""
# 	func_type = Callable[["Preprocessor", str], str]

# # class Block(WrappedFunction[["Preprocessor", str, str], str]):
# # 	"""A type for blocks. The three function arguments are
# # 	- the preprocessor
# # 	- the block arguments (args in {% block args %} content {% enblock %})
# # 	- the block contents"""

# # class Command(WrappedFunction[["Preprocessor", str], str]):
# # 	"""A type for commands. The two function arguments are
# # 	- the preprocessor
# # 	- the command arguments"""
