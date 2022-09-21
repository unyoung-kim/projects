from email.mime import image
from itertools import combinations_with_replacement
from django.shortcuts import render, redirect
from . import forms
from . import models
from result_app.models import imageModel
from result_app.ResNet import *

# Create your views here.
def index(request):
    form = forms.FormName()
    context = {}
    if request.method == 'POST':
        form = forms.FormName(request.POST, request.FILES)
   
        if form.is_valid():

            image = models.imageModel(
                image = form.cleaned_data['image']
                )
            image.save('static.images')
            pred_model, conf = ResNet_classify(image.image)
            print(pred_model, conf)
            
            result = zip(pred_model, conf)
 
            context['image'] = image
            context['pred_model'] = pred_model
            context['conf'] = conf
            context['result'] = result

            return results(request, context)
            

    return render(request, 'result_app/index.html', {'form':form})

def results(request, context):


    return render(request, 'result_app/result.html', context = context)