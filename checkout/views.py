from django.shortcuts import render, HttpResponse, redirect, reverse, get_object_or_404
from django.conf import settings
import stripe
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt

from products.models import Exercise

# Create your views here.
def checkout(request):
    # tell stripe what api key is
    stripe.api_key = settings.STRIPE_SECRET_KEY
    # retrieve my shopping cart
    cart = request.session.get("shopping_cart", {})

    line_items = []
    all_exercise_ids = []

    # go through each line in cart
    for exercise_id, exercise in cart.items():
        # retrieve exercise by id
        exercise_model = get_object_or_404(Exercise, pk=exercise_id)

        # create line item for stripe
        item = {
            "name": exercise_model.title,
            "amount": int(exercise_model.price * qty),
            "quantity": exercise["qty"],
            "currency": "usd",
        }

        line_items.append(item)
        all_exercise_ids.append(str(exercise_model.id))

    # get current website
    current_site = Site.objects.get_current()
    # get the domain name
    domain = current_site.domain
    
    # create a payment session for current transaction
    session = stripe.checkout.Session.create(
        # take credit cards
        payment_method_types=["card"],
        line_items=line_items,
        # customer id
        client_reference_id=request.user.id,
        success_url=domain + reverse("checkout_success_route"),
        cancel_url=domain + reverse("checkout_cancelled_route"),
    )
    # render the template which will redirect to stripe
    return render(request, "checkout/checkout.template.html", {
        'session_id': session_id,
        'public_key': settings.STRIPE_PUBLISHABLE_KEY
    })
        