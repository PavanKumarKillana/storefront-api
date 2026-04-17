from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class TaggedItemManager(models.Manager):
    """
    We create a custom Manager to abstract away the complex logic of querying generic relationships.
    Instead of writing this complex query inside a view every time we want tags for an item,
    we can just call TaggedItem.objects.get_tags_for(Product, 1).
    """
    def get_tags_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)

        return TaggedItem.objects \
            .select_related('tag') \
            .filter(
                content_type=content_type,
                object_id=obj_id
            )

class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class TaggedItem(models.Model):
    # Register our custom manager
    objects = TaggedItemManager()

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    # Type (product, video, article)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    
    # ID (identifier of the product, video, or article)
    object_id = models.PositiveIntegerField()
    
    # The actual object generic reference
    content_object = GenericForeignKey()

    def __str__(self):
        return self.tag.label