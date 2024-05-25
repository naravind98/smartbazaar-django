from django.db import models
from django.urls import reverse


# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    # slug = models.CharField(max_length=100, unique=True)  # This field represent the url of category. If you use 'models.CharField' for 'slug' then in admin-panel this field will not get auto-populated. We will have to manually enter this field.
    slug = models.SlugField(max_length=100, unique=True)      # By using 'models.SlugField', the 'slug' field will get auto-populated in the admin panel
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to="photos/categories",
                                  blank=True)  # The category-images will be stored inside the path "photos/categories"

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
