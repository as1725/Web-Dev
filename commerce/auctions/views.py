from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import * 


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        user = request.user
        title = request.POST.get("title")
        description = request.POST.get("description")
        starting_bid = request.POST.get("starting_bid")
        image_url = request.POST.get("image_url")
        category_name = request.POST.get("category")

        try:
            category = Category.objects.get(category_name=category_name) if category_name != "None" else None
        except ObjectDoesNotExist:
            return HttpResponse("Invalid category", status=400)

        listing = Listing(title=title, description=description, starting_bid=starting_bid, image=image_url, category=category, user=user)
        listing.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories
        })


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category, active=True)
    
    return render(request, "auctions/category_listings.html", {
        "listings": listings,
        "category": category
    })
    
    

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(listing=listing)
    comments = Comment.objects.filter(listing=listing)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments
    })

@login_required
def my_listings(request):
    user = request.user
    listings = Listing.objects.filter(user=user)
    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })

@login_required
def add_comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        comment = request.POST["comment"]
        
        comment = Comment(listing=listing, user=user, comment=comment)
        comment.save()
        
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    else:
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def add_bid(request, listing_id):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(pk=listing_id)
            user = request.user
            bid = float(request.POST["bid"])
            
            if bid > listing.starting_bid:
                new_bid = Bid(listing=listing, user=user, bid=bid)
                new_bid.save()
                listing.starting_bid = new_bid.bid
                listing.save()
                
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                messages.error(request, "Bid must be greater than current bid.")
                
        except (Listing.DoesNotExist, ObjectDoesNotExist):
            messages.error(request, "Invalid listing or no previous bids.")
        
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required    
def close_bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        winner = Bid.objects.get(listing=listing, bid=listing.starting_bid).user
        listing.active = False
        listing.winner = winner
        listing.save()
        
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    else:
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def watchlist(request):
    user = request.user
    listings = user.watchlist.all()
        
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required
def add_watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        
        user.watchlist.add(listing)
        user.save()
        
        messages.success(request, "Added to watchlist.")
        
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    else:
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required    
def remove_watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        
        user.watchlist.remove(listing)
        user.save()
        
        messages.success(request, "Removed from watchlist.")
        
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    else:
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))