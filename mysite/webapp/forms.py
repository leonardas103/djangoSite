from django import forms

class UploadFileForm(forms.Form):
	title = forms.CharField(max_length=50)
	file = forms.FileField()

class SubmitImageForm(forms.Form):
	widget=forms.TextInput(attrs={'class':'form-control'})
	image = forms.FileField()
	prototype = forms.FileField()
	prototypeCenter = forms.CharField(widget=widget, label='Prototype Center', max_length=10, initial='[100,100]')
	sigma = forms.CharField(widget=widget, label='Sigma', max_length=10, initial=2.4)
	rhoList = forms.CharField(widget=widget, label='Rho List', max_length=20, initial="[0,9,2]")
	sigma0 = forms.CharField(widget=widget, label='Sigma 0', max_length=10, initial=3)
	alpha = forms.CharField(widget=widget, label='Alpha', max_length=10, initial=0.7)
	rotInvariances = forms.CharField(widget=widget, label='rotational Invariances', max_length=10, initial=12)
	source = forms.CharField(max_length=10, widget=forms.HiddenInput(), initial='form')
