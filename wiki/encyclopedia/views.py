from django.shortcuts import render

from . import util

import markdown2

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/error.html", {
            "error": "Page not found"
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(util.get_entry(title))
    })


def search(request):
    query = request.GET.get('q')

    if util.get_entry(query) == None:
        search_results = []
        for entry in util.list_entries():
            if query.lower() in entry.lower():
                search_results.append(entry)

                return render(request, "encyclopedia/search.html", {
                    "entries": search_results
                })

        return render(request, "encyclopedia/error.html", {
            "error": "Page not found"
        })

    else:
        return render(request, "encyclopedia/entry.html", {
            "title": query,
            "content": markdown2.markdown(util.get_entry(query))
        })

def random (request):
    import random
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return render(request, "encyclopedia/entry.html", {
        "title": random_entry,
        "content": markdown2.markdown(util.get_entry(random_entry))
    })
    
def newpage(request):
    return render(request, "encyclopedia/newpage.html")
 

def create(request):
    title = request.POST.get("title")
    content = request.POST.get("content")

    if util.get_entry(title) == None:
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=(title,)))
        
    else:
        return render (request, "encyclopedia/newpage.html", {
            "error": "Page already exists!"
        })

def edit(request, title):
    if request.method == "GET":
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": util.get_entry(title)
        })

    else:
        content = request.POST.get("content")
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=(title,)))

def delete(request, title):
    util.delete_entry(title)
    return HttpResponseRedirect(reverse("index"))   