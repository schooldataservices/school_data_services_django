from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages
from ..forms import CustomersForm
from django.db import IntegrityError
from django.http import JsonResponse
from ..models import Customers  

def customer_create_view(request):
    if request.method == 'POST':
        form = CustomersForm(request.POST)

        if form.is_valid():
            try:
                customer = form.save(commit=False)
                customer.creator_id = request.user
                customer.save()
                messages.success(request, 'Customer saved successfully!')  # Add success message
                return redirect('create-customer')  # Redirect to a success page or the same view
            except IntegrityError:
                print(form.errors)
                messages.error(request, 'Contact has an existing email already created. Refer to existing contact.')
    else:
        form = CustomersForm()

    return render(request, 'emailscraper_app/customer_form.html', {'form': form})




def search_contacts(request):
    query = request.GET.get('q', '')
    if query:
        print('Search contact query has been called')
        contacts = Customers.objects.filter(contact__icontains=query)  
        contact_list = [{'id': c.id, 'name': c.contact} for c in contacts]
        return JsonResponse(contact_list, safe=False)
    else:
        print('Search contact query has been called but returning nothing')
        return JsonResponse([], safe=False)


def get_contact_details(request):
    contact_id = request.GET.get('id')
    try:
        print('Get contact details called')
        c = Customers.objects.get(id=contact_id)
        data = {
            'contact': c.contact,
            'company': c.company,
            'title': c.title,
            'department': c.department,
            'phone': c.phone,
            'email': c.email
            # Add more fields here
        }
        return JsonResponse(data)
    except Customers.DoesNotExist:
        print('Contact does not exist after calling get contact details')
        return JsonResponse({'error': 'Contact not found'}, status=404)



#Need to create another view to take into account what is saved and provide the info