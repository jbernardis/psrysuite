import wx
import string

class TextObjectValidator(wx.Validator):
	def __init__(self):
		wx.Validator.__init__(self)
		self.Bind(wx.EVT_CHAR, self.OnChar)

	def Clone(self):
		return TextObjectValidator()

	def Validate(self, win):
		tc = self.GetWindow()
		val = tc.GetValue()
		
		if len(val) == 0:
			wx.MessageBox("Need data to send", "Error")
			tc.SetBackgroundColour("pink")
			tc.SetFocus()
			tc.Refresh()
			return False

		for x in val:
			if x not in string.hexdigits:
				wx.MessageBox("Contains non-hexadecimal digits", "Error")
				tc.SetBackgroundColour("pink")
				tc.SetFocus()
				tc.Refresh()
				return False
			
		if len(val) % 2 != 0:
			wx.MessageBox("Need an even number of hex digits", "Error")
			tc.SetBackgroundColour("pink")
			tc.SetFocus()
			tc.Refresh()
			return False

		return True

	def OnChar(self, event):
		key = event.GetKeyCode()

		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return

		if chr(key) in string.hexdigits:
			event.Skip()
			return

		if not wx.Validator.IsSilent():
			wx.Bell()

		# Returning without calling even.Skip eats the event before it
		# gets to the text control
		return

	def TransferToWindow(self):
		return True

	def TransferFromWindow(self):
		return True


class HexCtrl(wx.TextCtrl):
	def __init__(self, parent, idv, value, size=(-1, -1), style=0):
		wx.TextCtrl.__init__(self, parent, idv, value, size=size, style=style, validator=TextObjectValidator())
