from django.shortcuts import render
from .models import Author
from . import script

# Create your views here.

script.load_data()

def home(request):
    context = {  }
    context["periods"] = [ str(2019+i) for i in range(4) ]

    if request.method == "POST":
        period = request.POST.get("period")
        if period:
            data = script.select_period(period)
            filtered_data = data
            context["available_types"] = ["Tous"] + list(set(data["Type local"]))
            context["charts"] = script.make_charts(filtered_data)

        context["dataframe"] = script.data.head(100)
        context["selected_period"] = period

    return render(request, 'home.html', context=context)

def contact(request):
    context = { "authors": Author.objects.all() }
    return render(request, 'contact.html', context=context)
