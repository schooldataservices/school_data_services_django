from django.shortcuts import render, redirect
from ..forms import CustomersForm

def customer_create_view(request):
    if request.method == 'POST':
        form = CustomersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_customer')  # Redirect to a success page or another view
    else:
        form = CustomersForm()

    return render(request, 'emailscraper_app/customer_form.html', {'form': form})


