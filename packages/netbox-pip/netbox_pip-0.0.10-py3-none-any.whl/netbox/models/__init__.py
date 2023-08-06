from django.core.validators import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from utilities.mptt import TreeManager
from utilities.querysets import RestrictedQuerySet
from netbox.models.features import *

__all__ = (
    'ChangeLoggedModel',
    'NestedGroupModel',
    'OrganizationalModel',
    'NetBoxModel',
)


class NetBoxFeatureSet(
    ChangeLoggingMixin,
    CustomFieldsMixin,
    CustomLinksMixin,
    CustomValidationMixin,
    ExportTemplatesMixin,
    JournalingMixin,
    TagsMixin,
    WebhooksMixin
):
    class Meta:
        abstract = True


#
# Base model classes
#

class ChangeLoggedModel(ChangeLoggingMixin, CustomValidationMixin, models.Model):
    """
    Base model for ancillary models; provides limited functionality for models which don't
    support NetBox's full feature set.
    """
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True


class NetBoxModel(NetBoxFeatureSet, models.Model):
    """
    Primary models represent real objects within the infrastructure being modeled.
    """
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True


class NestedGroupModel(NetBoxFeatureSet, MPTTModel):
    """
    Base model for objects which are used to form a hierarchy (regions, locations, etc.). These models nest
    recursively using MPTT. Within each parent, each child instance must have a unique name.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = TreeManager()

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ('name',)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # An MPTT model cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({
                "parent": "Cannot assign self as parent."
            })


class OrganizationalModel(NetBoxFeatureSet, models.Model):
    """
    Organizational models are those which are used solely to categorize and qualify other objects, and do not convey
    any real information about the infrastructure being modeled (for example, functional device roles). Organizational
    models provide the following standard attributes:
    - Unique name
    - Unique slug (automatically derived from name)
    - Optional description
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('name',)
