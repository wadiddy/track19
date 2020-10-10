from django.shortcuts import render

from . import common


def mapper_page(request):
	return _send_response(request, "mapper_index.html", {
	})

def _send_response(request, tmpl, ctx=None):
	if ctx is None:
		ctx = {}

	qs = request.META['QUERY_STRING']
	ctx["full_url"] = request.META['PATH_INFO'] + ("?" + qs if qs is not None and len(qs) > 0 else "")

	if common.get(ctx, "title") is None:
		ctx["title"] = "Woodcrest Drive"

	if common.get(ctx, "description") is None:
		ctx["description"] = "Woodcrest Dr. through time"

	if common.get(ctx, "share_image") is None:
		ctx["share_image"] = "mapper_woodcrest/" + common.get(request.GET, "img_1", "wc_1982.jpg")

	r = render(request, tmpl, context=ctx)

	return r

