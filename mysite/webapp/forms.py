from django import forms


class SubmitImageForm(forms.Form):
    widget = forms.TextInput(attrs={'class': 'form-control'})
    image = forms.FileField()
    prototype = forms.FileField(widget=forms.HiddenInput())
    prototypeCenter = forms.CharField(widget=forms.HiddenInput(), label='Characteristic Keypoint', max_length=10, initial='[100,100]',
                                      help_text="Enter the center point of the prototype image")
    sigma = forms.CharField(widget=widget, label='Sigma', max_length=10, initial=2.4,
                            help_text="The sigma value is for the Gaussian blur")
    rhoList = forms.CharField(widget=widget, label='Rho List', max_length=20, initial="[0,9,2]",
                              help_text="The rho list is defined as a list [x,y,z] where x is the initial value, 'y'-1 is the final value and 'z' the step increment value (e.g [0,7,2] = {0,2,4,6})")
    sigma0 = forms.CharField(widget=widget, label='Sigma 0', max_length=10, initial=3, help_text="sigma 0")
    alpha = forms.CharField(widget=widget, label='Alpha', max_length=10, initial=0.7, help_text="Used for thresholding")
    rotInvariances = forms.CharField(widget=widget, label='Considered Rotations', max_length=10, initial=12,
                                     help_text="The number of rotational invariances")
    source = forms.CharField(max_length=10, widget=forms.HiddenInput(), initial='form')
