from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema
from ..models import Review
from ..serializers import ReviewSerializer

@extend_schema(tags=['4. Pikirler (Reviews)'])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
