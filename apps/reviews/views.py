from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from apps.products.models import Product
from apps.orders.models import OrderItem

from .models import Review, ReviewVote, ReviewMedia
from django.db.models import Count, Q



# =========================================================
# AJAX HELPER
# =========================================================

def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


# =========================================================
# SUBMIT REVIEW
# =========================================================

@login_required
def submit_review(request, product_id):

    if request.method != "POST":
        return redirect("/")

    product = get_object_or_404(Product, id=product_id)

    rating = request.POST.get("rating")
    title = request.POST.get("title", "")
    comment = request.POST.get("comment", "")

    # -----------------------------------------------------
    # VALIDATE RATING
    # -----------------------------------------------------

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except (ValueError, TypeError):

        if _is_ajax(request):
            return JsonResponse(
                {"success": False, "error": "Rating must be between 1 and 5"},
                status=400
            )

        messages.error(request, "Invalid rating")
        return redirect("product_detail", slug=product.slug)

    # -----------------------------------------------------
    # VERIFIED PURCHASE CHECK
    # -----------------------------------------------------

    verified = OrderItem.objects.filter(
        order__user=request.user,
        product_variant__product=product
    ).exists()

    # -----------------------------------------------------
    # CREATE / UPDATE REVIEW
    # -----------------------------------------------------

    with transaction.atomic():

        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                "rating": rating,
                "title": title,
                "comment": comment,
                "is_verified_purchase": verified
            }
        )

        # -------------------------------------------------
        # HANDLE MEDIA UPLOAD
        # -------------------------------------------------

        files = request.FILES.getlist("media")

        if files:

            # remove old media when editing review
            review.media.all().delete()

            media_objects = []

            for i, file in enumerate(files):

                media_type = "video"
                if file.content_type.startswith("image"):
                    media_type = "image"

                media_objects.append(
                    ReviewMedia(
                        review=review,
                        file=file,
                        media_type=media_type,
                        sort_order=i
                    )
                )

            ReviewMedia.objects.bulk_create(media_objects)

    # -----------------------------------------------------
    # AJAX RESPONSE
    # -----------------------------------------------------

    if _is_ajax(request):

        media = [
            {
                "url": m.file.url,
                "type": m.media_type
            }
            for m in review.media.all()
        ]

        return JsonResponse({
            "success": True,
            "user": request.user.username,
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "verified": review.is_verified_purchase,
            "media": media,
            "created": created
        })

    messages.success(request, "Review submitted")

    return redirect("product_detail", slug=product.slug)


# =========================================================
# VOTE REVIEW
# =========================================================

@login_required
def vote_review(request, review_id):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    review = get_object_or_404(Review, id=review_id)

    value = request.POST.get("vote")

    if value not in ["helpful", "not_helpful"]:
        return JsonResponse({"error": "Invalid vote"}, status=400)

    is_helpful = value == "helpful"

    ReviewVote.objects.update_or_create(
        review=review,
        user=request.user,
        defaults={"is_helpful": is_helpful}
    )

    # -----------------------------------------------------
    # OPTIMIZED COUNT
    # -----------------------------------------------------

    helpful = review.votes.filter(is_helpful=True).count()
    not_helpful = review.votes.filter(is_helpful=False).count()

    return JsonResponse({
        "success": True,
        "helpful": helpful,
        "not_helpful": not_helpful
    })



def filter_reviews(request, product_id):

    rating = request.GET.get("rating")
    with_media = request.GET.get("media")
    verified = request.GET.get("verified")
    sort = request.GET.get("sort")

    reviews = (
        Review.objects
        .filter(product_id=product_id, is_approved=True)
        .select_related("user")
        .prefetch_related("media")
        .annotate(
            helpful_count=Count(
                "votes",
                filter=Q(votes__is_helpful=True)
            )
        )
    )

    if rating:
        reviews = reviews.filter(rating=rating)

    if with_media == "1":
        reviews = reviews.filter(media__isnull=False).distinct()

    if verified == "1":
        reviews = reviews.filter(is_verified_purchase=True)

    if sort == "helpful":
        reviews = reviews.order_by("-helpful_count")

    elif sort == "newest":
        reviews = reviews.order_by("-created_at")

    data = []

    for r in reviews[:20]:

        media = [
            {
                "url": m.file.url,
                "type": m.media_type
            }
            for m in r.media.all()
        ]

        data.append({

            "user": r.user.username,
            "id": r.id,
            "rating": r.rating,
            "title": r.title,
            "comment": r.comment,
            "verified": r.is_verified_purchase,
            "helpful": r.helpful_votes,
            "not_helpful": r.not_helpful_votes,
            "media": media
            
        })

    return JsonResponse({
        "reviews": data
    })